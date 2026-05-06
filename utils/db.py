"""
utils/db.py — Thread-safe local JSON file storage (replaces SQLite).

All score records share the same schema as the original SQLite design:
  {
    "id": <uuid4 str>,
    "player_name": str,
    "game": "snake" | "car" | "quiz",
    "score": int,
    "metadata": dict (optional JSON-serialisable),
    "played_at": ISO-8601 timestamp
  }

Atomic write pattern: write to <file>.tmp then os.replace() so a crash
mid-write never leaves a corrupt store.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

# Import after module is loaded to avoid circular dependency
import utils.score_files as _sf

logger = logging.getLogger(__name__)

# ── Path resolution ──────────────────────────────────────────────────────────
_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_SCORES_FILE = _DATA_DIR / "scores.json"
_SCORES_TMP = _DATA_DIR / "scores.json.tmp"

# ── Thread safety ────────────────────────────────────────────────────────────
_lock = threading.Lock()

# ── Theoretical score caps (server-side validation) ──────────────────────────
_SCORE_MAX = {
    "snake": 50_000,
    "car": 100_000,
    "quiz": 10_000,
}


# ── Internal helpers ─────────────────────────────────────────────────────────

def _ensure_store() -> None:
    """Create data dir + empty scores file if they don't exist."""
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not _SCORES_FILE.exists():
        _SCORES_FILE.write_text("[]", encoding="utf-8")


def _load() -> list[dict]:
    """Read and return all score records (never raises — returns [] on error)."""
    _ensure_store()
    try:
        text = _SCORES_FILE.read_text(encoding="utf-8")
        data = json.loads(text)
        if isinstance(data, list):
            return data
        return []
    except Exception as exc:
        logger.error("Failed to load scores.json: %s", exc)
        return []


def _save(records: list[dict]) -> bool:
    """Atomically write records list to disk."""
    try:
        _ensure_store()
        tmp_path = _SCORES_TMP
        tmp_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp_path, _SCORES_FILE)
        return True
    except Exception as exc:
        logger.error("Failed to save scores.json: %s", exc)
        return False


# ── Public API ───────────────────────────────────────────────────────────────

def add_score(
    player_name: str,
    game: str,
    score: int,
    metadata: dict[str, Any] | None = None,
    session_token: str | None = None,
) -> dict | None:
    """
    Insert a new score record.

    Returns the inserted record dict on success, None on failure.
    Validates:
    - game must be one of 'snake', 'car', 'quiz'
    - score must be non-negative integer within theoretical cap
    - player_name sanitised (alphanumeric + spaces, max 20 chars)
    - session_token deduplication: one save per token per game
    """
    try:
        # ── Sanitise player name
        import re
        clean_name = re.sub(r"[^A-Za-z0-9 ]", "", player_name).strip()[:20] or "Anonymous"

        # ── Validate game
        if game not in _SCORE_MAX:
            logger.warning("Unknown game '%s' — score rejected", game)
            return None

        # ── Validate score
        score = int(score)
        if score < 0:
            logger.warning("Negative score %d rejected", score)
            return None
        if score > _SCORE_MAX[game]:
            logger.warning("Score %d exceeds cap %d for game '%s'", score, _SCORE_MAX[game], game)
            return None

        record = {
            "id": str(uuid.uuid4()),
            "player_name": clean_name,
            "game": game,
            "score": score,
            "metadata": metadata or {},
            "played_at": datetime.now(timezone.utc).isoformat(),
            "session_token": session_token or "",
        }

        with _lock:
            records = _load()

            # ── Dedup: skip if same session_token already saved for this game
            if session_token:
                dupes = [r for r in records if r.get("session_token") == session_token and r.get("game") == game]
                if dupes:
                    logger.info("Duplicate session token — score not saved again")
                    return dupes[0]

            records.append(record)
            if not _save(records):
                return None

        # ── Also write to per-game TXT file
        try:
            notes = _build_notes(metadata or {}, game)
            _sf.record_score(game, clean_name, score, notes)
        except Exception as sf_exc:
            logger.warning("score_files write failed: %s", sf_exc)

        logger.info("Score saved: %s | %s | %d", clean_name, game, score)
        return record

    except Exception as exc:
        logger.error("add_score error: %s", exc)
        return None


def get_top_scores(
    game: str,
    limit: int = 10,
    time_range: str = "all",          # "today" | "week" | "all"
) -> list[dict]:
    """Return top `limit` scores for a game, filtered by time_range."""
    try:
        records = _load()

        now = datetime.now(timezone.utc)
        cutoff: datetime | None = None
        if time_range == "today":
            cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_range == "week":
            cutoff = now - timedelta(days=7)

        filtered = [r for r in records if r.get("game") == game]

        if cutoff:
            def _ts(r: dict) -> datetime:
                try:
                    return datetime.fromisoformat(r["played_at"])
                except Exception:
                    return datetime.min.replace(tzinfo=timezone.utc)

            filtered = [r for r in filtered if _ts(r) >= cutoff]

        filtered.sort(key=lambda r: r.get("score", 0), reverse=True)
        return filtered[:limit]

    except Exception as exc:
        logger.error("get_top_scores error: %s", exc)
        return []


def get_player_best(player_name: str, game: str) -> dict | None:
    """Return the single best score record for a player+game combination."""
    try:
        records = _load()
        player_records = [
            r for r in records
            if r.get("game") == game and r.get("player_name", "").lower() == player_name.lower()
        ]
        if not player_records:
            return None
        return max(player_records, key=lambda r: r.get("score", 0))
    except Exception as exc:
        logger.error("get_player_best error: %s", exc)
        return None


def get_all_scores_df() -> pd.DataFrame:
    """Return all scores as a pandas DataFrame (for CSV export)."""
    try:
        records = _load()
        if not records:
            return pd.DataFrame(columns=["id", "player_name", "game", "score", "played_at"])
        df = pd.DataFrame(records)
        df = df[["player_name", "game", "score", "played_at"]].copy()
        df.rename(columns={"player_name": "Player", "game": "Game", "score": "Score", "played_at": "Date"}, inplace=True)
        df.sort_values("Score", ascending=False, inplace=True)
        return df.reset_index(drop=True)
    except Exception as exc:
        logger.error("get_all_scores_df error: %s", exc)
        return pd.DataFrame()


def init_db() -> None:
    """Ensure the data store exists. Call once at app startup."""
    _ensure_store()
    _sf.init_score_files()
    logger.info("JSON data store initialised at %s", _SCORES_FILE)


def _build_notes(metadata: dict, game: str) -> str:
    """Convert metadata dict to a short human-readable notes string."""
    if game == "quiz":
        parts = []
        if metadata.get("category"): parts.append(metadata["category"])
        if metadata.get("difficulty"): parts.append(metadata["difficulty"])
        if metadata.get("correct") is not None: parts.append(f"{metadata['correct']}/10✅")
        if metadata.get("time"): parts.append(f"{metadata['time']}s")
        return " · ".join(parts)
    if game == "car":
        lvl = metadata.get("level", "")
        return f"Level {lvl}" if lvl else ""
    return ""
