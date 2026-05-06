"""
components/highscore_panel.py — Right-side High Score panel for each game.
Reads data from the per-game TXT score files via utils/score_files.py.
"""
from __future__ import annotations
import streamlit as st
from utils.score_files import get_top_scores, get_game_high_score, get_player_best

GAME_META = {
    "snake": {"icon": "🐍", "label": "Snake",      "color": "#6C63FF", "rgb": "108,99,255"},
    "car":   {"icon": "🏎",  "label": "Car Racing", "color": "#E8A838", "rgb": "232,168,56"},
    "quiz":  {"icon": "🧠",  "label": "Quiz",       "color": "#3ECFB2", "rgb": "62,207,178"},
}

_PANEL_CSS = """
<style>
.hs-panel {{
  background: #0D0D1A;
  border: 1px solid rgba({rgb},0.25);
  border-radius: 12px;
  padding: 0;
  overflow: hidden;
  font-family: 'Inter', 'Segoe UI', sans-serif;
  margin-bottom: 16px;
}}
.hs-header {{
  background: linear-gradient(90deg, rgba({rgb},0.18), rgba({rgb},0.05));
  border-bottom: 1px solid rgba({rgb},0.2);
  padding: 12px 16px;
  display: flex; align-items: center; gap: 8px;
}}
.hs-header .icon {{ font-size: 1.1rem; }}
.hs-header .title {{
  font-size: 0.75rem; font-weight: 700;
  letter-spacing: 0.1em; text-transform: uppercase;
  color: {color};
}}
.hs-alltime {{
  padding: 14px 16px 10px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}}
.hs-alltime .lbl {{
  font-size: 0.62rem; font-weight: 600;
  letter-spacing: 0.1em; text-transform: uppercase; color: #44446A;
}}
.hs-alltime .val {{
  font-size: 2rem; font-weight: 800; color: {color};
  line-height: 1.1; margin-top: 2px;
}}
.hs-alltime .sub {{ font-size: 0.68rem; color: #44446A; margin-top: 1px; }}
.hs-yours {{
  padding: 10px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  display: flex; align-items: center; justify-content: space-between;
}}
.hs-yours .lbl {{ font-size: 0.62rem; font-weight: 600; color: #44446A; text-transform: uppercase; letter-spacing: 0.08em; }}
.hs-yours .val {{ font-size: 1rem; font-weight: 700; color: #EAEAEA; }}
.hs-list {{ padding: 10px 0 4px; }}
.hs-row {{
  display: flex; align-items: center;
  padding: 6px 16px; gap: 10px;
  transition: background 0.15s;
}}
.hs-row:hover {{ background: rgba(255,255,255,0.03); }}
.hs-rank {{
  font-size: 0.7rem; font-weight: 700; color: #44446A;
  min-width: 20px; text-align: center;
}}
.hs-rank.gold   {{ color: #FFD700; }}
.hs-rank.silver {{ color: #C0C0C0; }}
.hs-rank.bronze {{ color: #CD7F32; }}
.hs-player {{
  flex: 1; font-size: 0.8rem; color: #BBBBD8;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.hs-player.me {{ color: {color}; font-weight: 600; }}
.hs-score {{
  font-size: 0.82rem; font-weight: 700; color: #EAEAEA;
  font-variant-numeric: tabular-nums;
}}
.hs-notes {{
  font-size: 0.62rem; color: #333355;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  max-width: 80px;
}}
.hs-empty {{
  padding: 18px 16px; text-align: center;
  font-size: 0.78rem; color: #333355;
}}
.hs-file-note {{
  padding: 8px 16px 10px;
  font-size: 0.63rem; color: #2A2A4A;
  border-top: 1px solid rgba(255,255,255,0.04);
}}
.hs-file-note code {{
  color: #44446A; background: transparent; font-size: 0.63rem;
}}
</style>
"""


def render_highscore_panel(game: str, player_name: str) -> None:
    """
    Render the full high-score panel for a game.
    Shows: all-time best, player's personal best, and top-10 leaderboard.
    Reads directly from data/<game>_scores.txt
    """
    meta = GAME_META.get(game)
    if not meta:
        return

    color = meta["color"]
    rgb   = meta["rgb"]
    icon  = meta["icon"]
    label = meta["label"]

    # Data
    try:
        all_time_best = get_game_high_score(game)
        my_best       = get_player_best(game, player_name)
        top10         = get_top_scores(game, limit=10)
    except Exception:
        all_time_best, my_best, top10 = 0, 0, []

    # Find who holds the all-time best
    best_holder = top10[0]["player"] if top10 else "—"

    # Render CSS once
    st.markdown(_PANEL_CSS.format(color=color, rgb=rgb), unsafe_allow_html=True)

    # Build top-10 rows HTML
    rows_html = ""
    if not top10:
        rows_html = f'<div class="hs-empty">No scores yet.<br>Play and save your first score!</div>'
    else:
        for i, entry in enumerate(top10, 1):
            rank_class = {1: "gold", 2: "silver", 3: "bronze"}.get(i, "")
            rank_icon  = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, str(i))
            is_me = entry["player"].lower() == player_name.lower()
            player_class = "me" if is_me else ""
            score_fmt = f"{entry['score']:,}"
            notes = entry.get("notes", "")[:28]
            rows_html += f"""
            <div class="hs-row">
              <div class="hs-rank {rank_class}">{rank_icon}</div>
              <div class="hs-player {player_class}">{entry['player']}</div>
              <div class="hs-score">{score_fmt}</div>
            </div>"""
            if notes:
                rows_html += f'<div style="padding:0 16px 4px 46px;font-size:0.62rem;color:#333355">{notes}</div>'

    txt_filename = f"data/{game}_scores.txt"
    my_best_fmt    = f"{my_best:,}" if my_best else "—"
    alltime_fmt    = f"{all_time_best:,}" if all_time_best else "—"

    st.markdown(f"""
    <div class="hs-panel">
      <div class="hs-header">
        <span class="icon">{icon}</span>
        <span class="title">{label} · High Scores</span>
      </div>
      <div class="hs-alltime">
        <div class="lbl">All-Time Best</div>
        <div class="val">{alltime_fmt}</div>
        <div class="sub">held by {best_holder}</div>
      </div>
      <div class="hs-yours">
        <div>
          <div class="lbl">Your Best</div>
          <div class="val">{my_best_fmt}</div>
        </div>
      </div>
      <div class="hs-list">
        {rows_html}
      </div>
      <div class="hs-file-note">📄 Source: <code>{txt_filename}</code></div>
    </div>
    """, unsafe_allow_html=True)
