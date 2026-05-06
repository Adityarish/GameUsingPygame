"""
components/leaderboard.py — Leaderboard UI component.
"""
from __future__ import annotations
import logging
import streamlit as st
import pandas as pd
from utils.db import get_top_scores, get_all_scores_df
from utils.session import get_player_name

logger = logging.getLogger(__name__)

GAME_LABELS = {"snake": "🐍 Snake", "car": "🏎 Car Racing", "quiz": "🧠 Quiz"}


def render_leaderboard() -> None:
    st.markdown("## 🏆 Leaderboard")

    # Filters
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        game_sel = st.selectbox("Game", list(GAME_LABELS.keys()),
                                format_func=lambda g: GAME_LABELS[g], key="lb_game")
    with col2:
        time_range = st.selectbox("Time Range", ["all", "today", "week"],
                                  format_func=lambda t: {"all": "All Time", "today": "Today", "week": "This Week"}[t],
                                  key="lb_time")
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        refresh = st.button("🔄 Refresh", use_container_width=True)

    player = get_player_name()

    try:
        records = get_top_scores(game=game_sel, limit=10, time_range=time_range)
    except Exception as e:
        st.error(f"Could not load leaderboard: {e}")
        return

    if not records:
        st.info("No scores yet for this filter. Play a game and save your score!")
        return

    # Build display DataFrame
    rows = []
    for i, r in enumerate(records, 1):
        is_player = r.get("player_name", "").lower() == player.lower()
        rows.append({
            "Rank": f"{'🥇' if i==1 else '🥈' if i==2 else '🥉' if i==3 else str(i)}",
            "Player": ("⭐ " if is_player else "") + r.get("player_name", "?"),
            "Score": f"{r.get('score', 0):,}",
            "Date": r.get("played_at", "")[:10],
            "Info": _format_meta(r.get("metadata", {}), game_sel),
        })

    df = pd.DataFrame(rows)

    st.markdown("""
    <style>
    .lb-table{width:100%;border-collapse:collapse;}
    .lb-table th{background:#1A1A2E;color:#6C63FF;padding:10px 14px;text-align:left;font-size:0.85rem;}
    .lb-table td{padding:9px 14px;border-bottom:1px solid #1A1A2E;font-size:0.9rem;}
    .lb-table tr:hover td{background:#16162A;}
    .lb-highlight td{background:#1a1a3a!important;color:#6C63FF;}
    </style>
    """, unsafe_allow_html=True)

    html_rows = ""
    for i, r in enumerate(records, 1):
        is_player = r.get("player_name", "").lower() == player.lower()
        rank_icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else str(i)
        player_disp = ("⭐ " if is_player else "") + r.get("player_name", "?")
        score_disp = f"{r.get('score', 0):,}"
        date_disp = r.get("played_at", "")[:10]
        info_disp = _format_meta(r.get("metadata", {}), game_sel)
        row_class = "lb-highlight" if is_player else ""
        html_rows += f"""<tr class="{row_class}">
          <td>{rank_icon}</td><td>{player_disp}</td>
          <td><strong>{score_disp}</strong></td><td>{date_disp}</td><td>{info_disp}</td>
        </tr>"""

    st.markdown(f"""
    <table class="lb-table">
      <thead><tr><th>Rank</th><th>Player</th><th>Score</th><th>Date</th><th>Details</th></tr></thead>
      <tbody>{html_rows}</tbody>
    </table>
    """, unsafe_allow_html=True)

    # CSV export
    st.markdown("<br>", unsafe_allow_html=True)
    try:
        full_df = get_all_scores_df()
        if not full_df.empty:
            csv = full_df.to_csv(index=False)
            st.download_button(
                "⬇ Export All Scores (CSV)",
                data=csv,
                file_name="arcade_hub_scores.csv",
                mime="text/csv",
                use_container_width=True,
            )
    except Exception as e:
        logger.error("CSV export error: %s", e)


def _format_meta(meta: dict, game: str) -> str:
    if not meta:
        return "—"
    if game == "quiz":
        cat = meta.get("category", "")
        diff = meta.get("difficulty", "")
        correct = meta.get("correct", "")
        return f"{cat} · {diff} · {correct}/10 ✅"
    if game == "car":
        lvl = meta.get("level", "")
        return f"Level {lvl}" if lvl else "—"
    return "—"
