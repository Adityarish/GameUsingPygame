"""
components/home.py — Formal, professional landing page.
"""
from __future__ import annotations
import streamlit as st
from datetime import datetime

GAMES = [
    {
        "key": "snake",
        "icon": "🐍",
        "title": "Snake",
        "subtitle": "Classic Arcade",
        "desc": "Navigate the snake to collect food and power-ups. Achieve combo streaks for score multipliers. Compete on the global leaderboard.",
        "color": "#6C63FF",
        "accent": "rgba(108,99,255,0.08)",
        "border": "rgba(108,99,255,0.3)",
        "features": ["Power-ups & Super Food", "Combo Streak System", "Mobile Touch Support"],
    },
    {
        "key": "car",
        "icon": "🏎",
        "title": "Car Racing",
        "subtitle": "Infinite Runner",
        "desc": "Dodge oncoming traffic, manage your fuel reserves, and collect bonuses on an infinite procedural road.",
        "color": "#E8A838",
        "accent": "rgba(232,168,56,0.08)",
        "border": "rgba(232,168,56,0.3)",
        "features": ["Fuel & Nitro System", "Particle Explosions", "Dynamic Day / Night"],
    },
    {
        "key": "quiz",
        "icon": "🧠",
        "title": "Quiz",
        "subtitle": "Knowledge Challenge",
        "desc": "Answer timed questions across five knowledge domains. Deploy lifelines strategically and sustain answer streaks for bonus scoring.",
        "color": "#3ECFB2",
        "accent": "rgba(62,207,178,0.08)",
        "border": "rgba(62,207,178,0.3)",
        "features": ["50+ Curated Questions", "Streak Multiplier", "5 Knowledge Domains"],
    },
]


def render_home() -> None:
    player = st.session_state.get("player_name", "Player1")
    hs = st.session_state.get("high_scores", {})
    now = datetime.now().strftime("%A, %d %B %Y")

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Reset ── */
    .lp * {{ box-sizing: border-box; font-family: 'Inter', sans-serif; }}

    /* ── Header bar ── */
    .lp-header {{
      display: flex; align-items: flex-end; justify-content: space-between;
      padding: 36px 0 28px;
      border-bottom: 1px solid rgba(255,255,255,0.07);
      margin-bottom: 36px;
    }}
    .lp-title-block {{ display: flex; flex-direction: column; gap: 4px; }}
    .lp-eyebrow {{
      font-size: 0.7rem; font-weight: 600; letter-spacing: 0.14em;
      text-transform: uppercase; color: #6C63FF; margin-bottom: 2px;
    }}
    .lp-title {{
      font-size: 2.1rem; font-weight: 700; color: #F0F0F8;
      line-height: 1.15; margin: 0;
    }}
    .lp-subtitle {{
      font-size: 0.88rem; color: #606080; margin-top: 4px;
      font-weight: 400; letter-spacing: 0.01em;
    }}
    .lp-meta {{
      text-align: right; font-size: 0.78rem; color: #444466;
      line-height: 1.7;
    }}
    .lp-meta strong {{ color: #888899; font-weight: 500; }}

    /* ── Section label ── */
    .section-label {{
      font-size: 0.68rem; font-weight: 600; letter-spacing: 0.12em;
      text-transform: uppercase; color: #444466;
      border-left: 2px solid #6C63FF; padding-left: 10px;
      margin-bottom: 18px;
    }}

    /* ── Game cards ── */
    .game-card {{
      background: #111120;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 24px;
      position: relative;
      overflow: hidden;
      transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
    }}
    .game-card:hover {{
      border-color: var(--accent-solid);
      box-shadow: 0 0 0 1px var(--accent-solid), 0 8px 28px var(--accent-glow);
      transform: translateY(-2px);
    }}
    .game-card-top {{
      display: flex; align-items: flex-start;
      justify-content: space-between; margin-bottom: 16px;
    }}
    .game-icon {{
      width: 44px; height: 44px;
      background: var(--accent-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.4rem;
    }}
    .game-badge {{
      font-size: 0.65rem; font-weight: 600; letter-spacing: 0.1em;
      text-transform: uppercase; color: var(--accent-solid);
      background: var(--accent-bg);
      border: 1px solid var(--border);
      padding: 3px 8px; border-radius: 4px;
    }}
    .game-title {{
      font-size: 1.05rem; font-weight: 700;
      color: #E8E8F4; margin: 0 0 2px;
    }}
    .game-desc {{
      font-size: 0.82rem; color: #5a5a78; line-height: 1.6;
      margin: 0 0 18px;
    }}
    .game-features {{
      list-style: none; margin: 0 0 20px; padding: 0;
      display: flex; flex-direction: column; gap: 7px;
    }}
    .game-features li {{
      display: flex; align-items: center; gap: 8px;
      font-size: 0.78rem; color: #6a6a88;
    }}
    .game-features li::before {{
      content: '';
      display: inline-block;
      width: 5px; height: 5px; border-radius: 50%;
      background: var(--accent-solid); flex-shrink: 0;
    }}
    .game-divider {{
      height: 1px; background: rgba(255,255,255,0.05);
      margin-bottom: 18px;
    }}

    /* ── Stats panel ── */
    .stats-panel {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1px;
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.07);
      border-radius: 10px;
      overflow: hidden;
      margin-top: 36px;
    }}
    .stat-cell {{
      background: #0D0D1A;
      padding: 20px 24px;
      display: flex; flex-direction: column; gap: 4px;
    }}
    .stat-label {{
      font-size: 0.67rem; font-weight: 600; letter-spacing: 0.1em;
      text-transform: uppercase; color: #444466;
    }}
    .stat-value {{
      font-size: 1.7rem; font-weight: 700; color: #E8E8F4;
      line-height: 1;
    }}
    .stat-value span {{ font-size: 0.8rem; color: #555570; font-weight: 400; margin-left: 4px; }}
    .stat-game {{ font-size: 0.72rem; color: #444466; margin-top: 2px; }}

    /* ── Notice bar ── */
    .notice-bar {{
      display: flex; align-items: center; gap: 10px;
      background: rgba(108,99,255,0.07);
      border: 1px solid rgba(108,99,255,0.2);
      border-radius: 8px;
      padding: 12px 18px;
      margin-top: 28px;
      font-size: 0.8rem; color: #666688;
    }}
    .notice-bar .dot {{
      width: 7px; height: 7px; border-radius: 50%;
      background: #6C63FF; flex-shrink: 0;
      animation: pulse 2s infinite;
    }}
    @keyframes pulse {{
      0%,100% {{ opacity:1; }} 50% {{ opacity:0.3; }}
    }}
    </style>

    <div class="lp">

      <!-- Header -->
      <div class="lp-header">
        <div class="lp-title-block">
          <div class="lp-eyebrow">Arcade Hub Platform</div>
          <h1 class="lp-title">Welcome back, {player}</h1>
          <div class="lp-subtitle">Select a game from the catalogue below to begin your session.</div>
        </div>
        <div class="lp-meta">
          <strong>{now}</strong><br>
          Session active &nbsp;·&nbsp; Scores saved locally
        </div>
      </div>

      <!-- Section label -->
      <div class="section-label">Game Catalogue &nbsp;— 3 titles available</div>

    </div>
    """, unsafe_allow_html=True)

    # ── Game cards (columns so Streamlit buttons work) ─────────────────────
    cols = st.columns(3, gap="medium")
    for i, g in enumerate(GAMES):
        with cols[i]:
            features_html = "".join(f"<li>{f}</li>" for f in g["features"])
            st.markdown(f"""
            <div class="game-card" style="
              --accent-solid:{g['color']};
              --accent-bg:{g['accent']};
              --accent-glow:{g['accent']};
              --border:{g['border']};
            ">
              <div class="game-card-top">
                <div class="game-icon">{g['icon']}</div>
                <div class="game-badge">{g['subtitle']}</div>
              </div>
              <div class="game-title">{g['title']}</div>
              <p class="game-desc">{g['desc']}</p>
              <ul class="game-features">{features_html}</ul>
              <div class="game-divider"></div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(
                f"Launch {g['title']} →",
                key=f"home_play_{g['key']}",
                use_container_width=True,
            ):
                st.session_state["current_page"] = g["key"]
                st.rerun()

    # ── Personal bests panel ────────────────────────────────────────────────
    snake_hs = hs.get("snake", 0)
    car_hs   = hs.get("car", 0)
    quiz_hs  = hs.get("quiz", 0)

    st.markdown(f"""
    <div class="lp">
      <div class="section-label" style="margin-top:36px">Personal Bests &nbsp;— {player}</div>
      <div class="stats-panel">
        <div class="stat-cell">
          <div class="stat-label">Snake</div>
          <div class="stat-value">{snake_hs:,}<span>pts</span></div>
          <div class="stat-game">Classic Arcade</div>
        </div>
        <div class="stat-cell">
          <div class="stat-label">Car Racing</div>
          <div class="stat-value">{car_hs:,}<span>pts</span></div>
          <div class="stat-game">Infinite Runner</div>
        </div>
        <div class="stat-cell">
          <div class="stat-label">Quiz</div>
          <div class="stat-value">{quiz_hs:,}<span>pts</span></div>
          <div class="stat-game">Knowledge Challenge</div>
        </div>
      </div>

      <div class="notice-bar">
        <div class="dot"></div>
        All scores are persisted to <code style="color:#8880FF;background:transparent">data/scores.json</code>
        &nbsp;—&nbsp; thread-safe atomic writes &nbsp;·&nbsp; no external database required.
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_about() -> None:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    .about-section {{ font-family: 'Inter', sans-serif; }}
    .about-section h2 {{ font-size:1.3rem; font-weight:700; color:#E8E8F4; border-bottom:1px solid rgba(255,255,255,0.07); padding-bottom:10px; margin-bottom:20px; }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("## ℹ️ About Arcade Hub")
    st.markdown("**Arcade Hub** is a self-contained multi-game platform built with Streamlit and HTML5 Canvas.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Tech Stack**")
        st.markdown("""
| Component | Technology |
|---|---|
| Web UI | Streamlit ≥ 1.32 |
| Game Engine | HTML5 Canvas + Vanilla JS |
| Sound | Web Audio API (synthesised) |
| Persistence | `data/scores.json` (local file) |
| Data Export | pandas → CSV |
        """)
    with col2:
        st.markdown("**Game Controls**")
        st.markdown("""
| Game | Controls |
|---|---|
| Snake | Arrow / WASD · P pause · Swipe |
| Car Racing | ← → Arrow / A D · Tap nitro |
| Quiz | Click answer buttons |
        """)
        st.markdown("**Storage Design**")
        st.info(
            "Scores are written atomically (`scores.json.tmp` → `os.replace()`). "
            "A `threading.Lock` ensures concurrent writes never corrupt the file.",
            icon="🔒",
        )
