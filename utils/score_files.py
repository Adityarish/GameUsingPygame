"""
utils/score_files.py — Per-game TXT file score storage.

Each game gets its own plain-text file in data/:
  data/snake_scores.txt
  data/car_scores.txt
  data/quiz_scores.txt

File format (one entry per line, pipe-delimited):
  player_name|score|date_played|metadata_notes

Example:
  Player1|1450|2026-05-06 10:12:33|Level 4
  Alice|9800|2026-05-06 09:45:00|Tech·Hard·8/10✅

Rules:
- Sorted by score descending, highest first
- Max 100 entries per file (oldest/lowest trimmed)
- Atomic write: write .tmp then os.replace()
- Thread-safe: shared threading.Lock per file
"""
from __future__ import annotations

import os
import threading
from datetime import datetime
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# One lock per game file
_LOCKS: dict[str, threading.Lock] = {
    "snake": threading.Lock(),
    "car":   threading.Lock(),
    "quiz":  threading.Lock(),
}

_MAX_ENTRIES = 100
_HEADER = "# Arcade Hub — {game} High Scores\n# Format: player|score|date|notes\n"


def _file_path(game: str) -> Path:
    return _DATA_DIR / f"{game}_scores.txt"


def _tmp_path(game: str) -> Path:
    return _DATA_DIR / f"{game}_scores.txt.tmp"


def _ensure_file(game: str) -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    fp = _file_path(game)
    if not fp.exists():
        fp.write_text(_HEADER.format(game=game.title()), encoding="utf-8")


def _read_entries(game: str) -> list[dict]:
    """
    Return list of score dicts, sorted by score desc.
    Each dict: {player, score (int), date, notes}
    """
    _ensure_file(game)
    entries: list[dict] = []
    try:
        lines = _file_path(game).read_text(encoding="utf-8").splitlines()
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("|")
            if len(parts) < 3:
                continue
            try:
                entries.append({
                    "player": parts[0],
                    "score":  int(parts[1]),
                    "date":   parts[2],
                    "notes":  parts[3] if len(parts) > 3 else "",
                })
            except ValueError:
                continue
    except Exception:
        pass
    entries.sort(key=lambda e: e["score"], reverse=True)
    return entries


def _write_entries(game: str, entries: list[dict]) -> None:
    """Atomically write sorted entries (top _MAX_ENTRIES) to the txt file."""
    top = sorted(entries, key=lambda e: e["score"], reverse=True)[:_MAX_ENTRIES]
    lines = [_HEADER.format(game=game.title())]
    for e in top:
        notes = e.get("notes", "").replace("|", " ")
        lines.append(f"{e['player']}|{e['score']}|{e['date']}|{notes}")
    content = "\n".join(lines) + "\n"
    tmp = _tmp_path(game)
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, _file_path(game))


# ── Public API ────────────────────────────────────────────────────────────────

def record_score(
    game: str,
    player_name: str,
    score: int,
    notes: str = "",
) -> None:
    """
    Append a score entry to the game's TXT file.
    The file is kept sorted (highest first) and trimmed to _MAX_ENTRIES.
    """
    if game not in _LOCKS:
        return
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {"player": player_name, "score": score, "date": date_str, "notes": notes}
    with _LOCKS[game]:
        entries = _read_entries(game)
        entries.append(entry)
        _write_entries(game, entries)


def get_top_scores(game: str, limit: int = 10) -> list[dict]:
    """Return top `limit` score entries for a game from its TXT file."""
    if game not in _LOCKS:
        return []
    with _LOCKS[game]:
        entries = _read_entries(game)
    return entries[:limit]


def get_game_high_score(game: str) -> int:
    """Return the single highest score ever recorded for a game."""
    top = get_top_scores(game, limit=1)
    return top[0]["score"] if top else 0


def get_player_best(game: str, player_name: str) -> int:
    """Return the best score for a specific player in a game."""
    if game not in _LOCKS:
        return 0
    with _LOCKS[game]:
        entries = _read_entries(game)
    player_entries = [e for e in entries if e["player"].lower() == player_name.lower()]
    if not player_entries:
        return 0
    return max(e["score"] for e in player_entries)


def init_score_files() -> None:
    """Create all three score files if they don't exist."""
    for game in ("snake", "car", "quiz"):
        _ensure_file(game)
