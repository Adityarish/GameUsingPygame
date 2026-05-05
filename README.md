# 🕹 Arcade Hub

A **production-ready, multi-game arcade platform** built with Streamlit + HTML5 Canvas + JavaScript.

## Games

| Game | Controls | Features |
|---|---|---|
| 🐍 Snake | Arrow/WASD · P pause · Swipe | Power-ups, combo streak, Web Audio |
| 🏎 Car Racing | ← → / A D | Fuel, nitro, particles, day/night |
| 🧠 Quiz | Click buttons | 50+ Qs, 5 categories, lifelines |

## Architecture

```
arcade_hub/
├── app.py                   # Streamlit entry point
├── requirements.txt
├── .streamlit/config.toml   # Dark theme
├── data/
│   └── scores.json          # ← Local JSON leaderboard store
├── games/
│   ├── snake_game.py        # HTML5 Canvas Snake → str
│   ├── car_game.py          # HTML5 Canvas Car → str
│   └── quiz_game.py         # Streamlit-native Quiz UI
├── components/
│   ├── leaderboard.py       # Score table + CSV export
│   ├── navbar.py            # Sidebar + navigation
│   └── home.py              # Landing page + about
└── utils/
    ├── db.py                # Thread-safe JSON CRUD
    └── session.py           # st.session_state init helpers
```

## Storage Design

Scores are persisted to **`data/scores.json`** (no SQLite needed):

- **Atomic writes**: write to `scores.json.tmp` → `os.replace()` — crash-safe
- **Thread safety**: `threading.Lock()` wraps every read/write
- **Validation**: score caps per game, name sanitisation, session-token dedup
- **Same schema** as a SQLite table: `id`, `player_name`, `game`, `score`, `metadata`, `played_at`

## Setup

```bash
cd arcade_hub
pip install -r requirements.txt
streamlit run app.py
```

## Tests

```bash
cd arcade_hub
python -m pytest tests/test_games.py -v
```

## Tech Stack

- Python 3.11+
- Streamlit ≥ 1.32.0
- HTML5 Canvas + Vanilla JavaScript (no external game libs)
- Web Audio API (synthesised sound effects, no audio files)
- pandas (CSV export)
- `data/scores.json` (local file persistence)
# GameUsingPygame
