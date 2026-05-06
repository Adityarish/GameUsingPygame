"""
components/navbar.py — Top navigation bar injected via st.markdown.
"""
from __future__ import annotations
import streamlit as st

PAGES = [
    ("🏠", "Home", "home"),
    ("🐍", "Snake", "snake"),
    ("🏎", "Car Racing", "car"),
    ("🧠", "Quiz", "quiz"),
    ("🏆", "Leaderboard", "leaderboard"),
    ("ℹ️", "About", "about"),
]


def render_navbar() -> None:
    current = st.session_state.get("current_page", "home")
    items_html = ""
    for icon, label, key in PAGES:
        active = "nav-active" if key == current else ""
        items_html += f"""
        <a href="#" class="nav-item {active}" onclick="setPage('{key}'); return false;">
          <span class="nav-icon">{icon}</span>
          <span class="nav-label">{label}</span>
        </a>"""

    st.markdown(f"""
    <style>
    .navbar{{
      display:flex; align-items:center; gap:4px;
      background:linear-gradient(90deg,#1A1A2E,#16213E);
      border-radius:14px; padding:8px 16px;
      border:1px solid #6C63FF33;
      margin-bottom:18px;
      box-shadow:0 4px 20px rgba(108,99,255,0.15);
    }}
    .navbar-brand{{
      color:#6C63FF; font-weight:800; font-size:1.2rem;
      margin-right:16px; white-space:nowrap;
      text-shadow:0 0 20px rgba(108,99,255,0.5);
    }}
    .nav-item{{
      display:flex; align-items:center; gap:5px;
      color:#EAEAEA; text-decoration:none;
      padding:6px 12px; border-radius:8px;
      font-size:0.88rem; transition:all 0.2s;
      white-space:nowrap;
    }}
    .nav-item:hover{{background:#6C63FF22; color:#6C63FF;}}
    .nav-active{{background:#6C63FF33!important; color:#6C63FF!important; font-weight:600;}}
    .nav-icon{{font-size:1rem;}}
    .nav-label{{}}
    @media(max-width:640px){{.nav-label{{display:none;}} .navbar-brand{{font-size:1rem;}}}}
    </style>
    <div class="navbar">
      <div class="navbar-brand">🕹 Arcade Hub</div>
      {items_html}
    </div>
    """, unsafe_allow_html=True)


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("### 🕹 Arcade Hub")
        st.markdown("---")

        name = st.text_input(
            "👤 Player Name",
            value=st.session_state.get("player_name", "Player1"),
            max_chars=20,
            key="sidebar_name_input",
        )
        if name != st.session_state.get("player_name"):
            import re
            clean = re.sub(r"[^A-Za-z0-9 ]", "", name).strip()[:20]
            st.session_state["player_name"] = clean or "Player1"

        st.markdown("---")
        st.markdown("### 🎮 Navigate")
        for icon, label, key in PAGES:
            active = st.session_state.get("current_page") == key
            if st.button(f"{icon} {label}", key=f"nav_{key}",
                         use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state["current_page"] = key
                st.rerun()

        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        st.session_state["sound_enabled"] = st.toggle(
            "🔊 Sound", value=st.session_state.get("sound_enabled", True))

        st.markdown("---")
        st.caption("Built with Streamlit + HTML5 Canvas")
        st.caption("Scores stored in `data/scores.json`")
