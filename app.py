"""
app.py — Main Streamlit entry point for Arcade Hub.
"""
from __future__ import annotations
import logging
import streamlit as st

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Arcade Hub",
    page_icon="🕹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports (after set_page_config) ──────────────────────────────────────────
from utils.db import init_db
from utils.session import init_session, refresh_high_scores
from components.navbar import render_sidebar
from components.home import render_home, render_about
from components.leaderboard import render_leaderboard
from components.highscore_panel import render_highscore_panel


def _fullscreen_btn(game_label: str) -> None:
    """Render a fullscreen toggle button that targets the game iframe."""
    col1, col2 = st.columns([8, 1])
    with col2:
        if st.button("⛶", key=f"fs_{game_label}", help="Toggle Fullscreen",
                     use_container_width=True):
            # Inject JS to fullscreen the last iframe on the page
            st.components.v1.html("""
            <script>
            (function() {
              // Find the game iframe (last iframe in parent document)
              const iframes = window.parent.document.querySelectorAll('iframe');
              const gameIframe = iframes[iframes.length - 2];  // -2: skip this hidden component
              if (gameIframe) {
                if (!window.parent.document.fullscreenElement) {
                  gameIframe.requestFullscreen && gameIframe.requestFullscreen();
                } else {
                  window.parent.document.exitFullscreen && window.parent.document.exitFullscreen();
                }
              }
            })();
            </script>
            """, height=0)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, [data-testid="stAppViewContainer"] {
  background: #0E0E1A;
  color: #EAEAEA;
  font-family: 'Inter', sans-serif;
}
[data-testid="stSidebar"] {
  background: #12122A;
  border-right: 1px solid #6C63FF22;
}
h1, h2, h3 { color: #EAEAEA; }
.stButton > button {
  border-radius: 10px !important;
  font-weight: 600 !important;
  transition: all 0.2s !important;
}
.stButton > button[kind="primary"] {
  background: #6C63FF !important;
  border: none !important;
  color: #fff !important;
}
.stButton > button:hover { transform: scale(1.02); }
div[data-testid="metric-container"] {
  background: #1A1A2E;
  border: 1px solid #6C63FF22;
  border-radius: 10px;
  padding: 12px;
}
.stSelectbox > div { border-radius: 8px !important; }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Initialise ────────────────────────────────────────────────────────────────
try:
    init_db()
except Exception as e:
    logger.error("DB init failed: %s", e)

init_session()
refresh_high_scores()

# ── Score submission listener (postMessage from JS games) ─────────────────────
score_listener_html = """
<script>
window.addEventListener('message', function(e) {
  if (e.data && e.data.type === 'score') {
    const params = new URLSearchParams(window.location.search);
    params.set('pending_score', e.data.value);
    params.set('pending_game', e.data.game);
    window.history.replaceState({}, '', '?' + params.toString());
  }
}, false);
</script>
"""
st.components.v1.html(score_listener_html, height=0)

# Check URL params for pending score (Streamlit re-runs on URL change)
try:
    params = st.query_params
    if "pending_score" in params and "pending_game" in params:
        ps = int(params["pending_score"])
        pg = params["pending_game"]
        if ps > 0 and pg in ("snake", "car"):
            from utils.db import add_score
            from utils.session import get_player_name
            result = add_score(
                player_name=get_player_name(),
                game=pg,
                score=ps,
                session_token=st.session_state.get("session_token"),
            )
            if result:
                st.toast(f"✅ {pg.title()} score {ps:,} saved!", icon="🎉")
                refresh_high_scores()
            st.query_params.clear()
except Exception as e:
    logger.error("Score submission error: %s", e)

# ── Sidebar navigation ────────────────────────────────────────────────────────
render_sidebar()

# ── Page routing ──────────────────────────────────────────────────────────────
page = st.session_state.get("current_page", "home")

if page == "home":
    try:
        render_home()
    except Exception as e:
        st.error(f"Home page error: {e}")
        logger.exception("Home page error")

elif page == "snake":
    try:
        from games.snake_game import get_snake_html
        player = st.session_state.get("player_name", "Player1")
        hs = st.session_state["high_scores"].get("snake", 0)

        # Header row: title + fullscreen button
        h1, h2 = st.columns([9, 1])
        with h1:
            st.markdown("### 🐍 Snake Game")
        with h2:
            _fullscreen_btn("snake")

        # Game + panel layout
        game_col, panel_col = st.columns([3, 1], gap="medium")
        with game_col:
            with st.spinner("Loading Snake Game…"):
                html_str = get_snake_html(player, hs)
            st.components.v1.html(html_str, height=700, scrolling=False)
            st.caption("💡 Click canvas to focus • Arrow/WASD to move • P to pause • ⛶ for fullscreen")
        with panel_col:
            render_highscore_panel("snake", player)
    except Exception as e:
        st.error(f"Could not load Snake game: {e}")
        logger.exception("Snake game error")

elif page == "car":
    try:
        from games.car_game import get_car_html
        player = st.session_state.get("player_name", "Player1")
        hs = st.session_state["high_scores"].get("car", 0)

        h1, h2 = st.columns([9, 1])
        with h1:
            st.markdown("### 🏨 Car Racing")
        with h2:
            _fullscreen_btn("car")

        game_col, panel_col = st.columns([3, 1], gap="medium")
        with game_col:
            with st.spinner("Loading Car Racing…"):
                html_str = get_car_html(player, hs)
            st.components.v1.html(html_str, height=760, scrolling=False)
            st.caption("💡 ← → / A D to steer • Collect ⛽ fuel • ⛶ for fullscreen")
        with panel_col:
            render_highscore_panel("car", player)
    except Exception as e:
        st.error(f"Could not load Car Racing game: {e}")
        logger.exception("Car game error")

elif page == "quiz":
    try:
        from games.quiz_game import render_quiz

        h1, h2 = st.columns([9, 1])
        with h1:
            st.markdown("### 🧠 Quiz Game")
        with h2:
            _fullscreen_btn("quiz")

        player = st.session_state.get("player_name", "Player1")
        game_col, panel_col = st.columns([3, 1], gap="medium")
        with game_col:
            render_quiz()
        with panel_col:
            render_highscore_panel("quiz", player)
    except Exception as e:
        st.error(f"Could not load Quiz game: {e}")
        logger.exception("Quiz error")

elif page == "leaderboard":
    try:
        render_leaderboard()
    except Exception as e:
        st.error(f"Could not load Leaderboard: {e}")
        logger.exception("Leaderboard error")

elif page == "about":
    try:
        render_about()
    except Exception as e:
        st.error(f"Could not load About page: {e}")
        logger.exception("About error")
