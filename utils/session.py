"""
utils/session.py — Centralised st.session_state initialisation.
Call init_session() once at the top of app.py.
"""
from __future__ import annotations

import hashlib
import time
import logging

import streamlit as st

logger = logging.getLogger(__name__)


def init_session() -> None:
    """Set all default session_state keys exactly once per browser session."""
    try:
        defaults: dict = {
            # User identity
            "player_name": "Player1",
            # Navigation
            "current_page": "home",
            # Per-game scores (runtime, not persisted here)
            "scores": {"snake": 0, "car": 0, "quiz": 0},
            # High scores fetched from JSON store (refreshed on demand)
            "high_scores": {"snake": 0, "car": 0, "quiz": 0},
            # Quiz state
            "quiz_active": False,
            "quiz_question_idx": 0,
            "quiz_score": 0,
            "quiz_correct": 0,
            "quiz_wrong": 0,
            "quiz_skipped": 0,
            "quiz_streak": 0,
            "quiz_multiplier": 1.0,
            "quiz_lifelines": {"fifty_fifty": True, "skip": True},
            "quiz_category": "General Knowledge",
            "quiz_difficulty": "Medium",
            "quiz_answers": [],
            "quiz_start_time": None,
            "quiz_questions": [],
            "quiz_fifty_fifty_options": None,
            # Settings
            "sound_enabled": True,
            "dark_mode": True,
            # Dedup token (one score submission per session)
            "session_token": _make_token(),
            # Score just received from JS game
            "pending_score": None,
            "pending_game": None,
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    except Exception as exc:
        logger.error("init_session error: %s", exc)


def _make_token() -> str:
    """Generate a unique session token."""
    raw = f"{time.time()}-{id(st.session_state)}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def get_player_name() -> str:
    return st.session_state.get("player_name", "Player1") or "Player1"


def set_player_name(name: str) -> None:
    import re
    clean = re.sub(r"[^A-Za-z0-9 ]", "", name).strip()[:20]
    st.session_state["player_name"] = clean or "Player1"


def refresh_high_scores() -> None:
    """Pull current personal bests from JSON store into session state."""
    try:
        from utils.db import get_player_best
        player = get_player_name()
        for game in ("snake", "car", "quiz"):
            best = get_player_best(player, game)
            st.session_state["high_scores"][game] = best["score"] if best else 0
    except Exception as exc:
        logger.error("refresh_high_scores error: %s", exc)
