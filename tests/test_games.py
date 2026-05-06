"""
tests/test_games.py — Basic smoke tests for Arcade Hub.
Run with: python -m pytest tests/test_games.py -v
"""
import sys
import os
import json
import tempfile
import shutil

# Make arcade_hub importable from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ── db.py tests ───────────────────────────────────────────────────────────────
def test_db_roundtrip(tmp_path, monkeypatch):
    """add_score -> get_top_scores round-trips correctly."""
    import utils.db as db
    monkeypatch.setattr(db, "_DATA_DIR", tmp_path)
    monkeypatch.setattr(db, "_SCORES_FILE", tmp_path / "scores.json")
    monkeypatch.setattr(db, "_SCORES_TMP", tmp_path / "scores.json.tmp")
    db.init_db()

    result = db.add_score("TestPlayer", "snake", 1234)
    assert result is not None
    assert result["score"] == 1234
    assert result["player_name"] == "TestPlayer"

    top = db.get_top_scores("snake")
    assert len(top) == 1
    assert top[0]["score"] == 1234


def test_db_score_validation(tmp_path, monkeypatch):
    """Rejects negative and over-cap scores."""
    import utils.db as db
    monkeypatch.setattr(db, "_DATA_DIR", tmp_path)
    monkeypatch.setattr(db, "_SCORES_FILE", tmp_path / "scores.json")
    monkeypatch.setattr(db, "_SCORES_TMP", tmp_path / "scores.json.tmp")
    db.init_db()

    assert db.add_score("P", "snake", -1) is None
    assert db.add_score("P", "snake", 999_999_999) is None
    assert db.add_score("P", "badgame", 100) is None


def test_db_dedup(tmp_path, monkeypatch):
    """Duplicate session tokens don't create duplicate records."""
    import utils.db as db
    monkeypatch.setattr(db, "_DATA_DIR", tmp_path)
    monkeypatch.setattr(db, "_SCORES_FILE", tmp_path / "scores.json")
    monkeypatch.setattr(db, "_SCORES_TMP", tmp_path / "scores.json.tmp")
    db.init_db()

    db.add_score("P", "car", 500, session_token="tok123")
    db.add_score("P", "car", 500, session_token="tok123")
    top = db.get_top_scores("car")
    assert len(top) == 1


def test_db_player_name_sanitise(tmp_path, monkeypatch):
    """Player names are sanitised — HTML stripped, max 20 chars."""
    import utils.db as db
    monkeypatch.setattr(db, "_DATA_DIR", tmp_path)
    monkeypatch.setattr(db, "_SCORES_FILE", tmp_path / "scores.json")
    monkeypatch.setattr(db, "_SCORES_TMP", tmp_path / "scores.json.tmp")
    db.init_db()

    result = db.add_score("<script>alert(1)</script>", "quiz", 200)
    assert "<" not in result["player_name"]
    assert len(result["player_name"]) <= 20


# ── game HTML tests ───────────────────────────────────────────────────────────
def test_snake_html_contains_canvas():
    from games.snake_game import get_snake_html
    html = get_snake_html("TestPlayer", 9999)
    assert "<canvas" in html
    assert "gameCanvas" in html
    assert "TestPlayer" in html


def test_car_html_contains_canvas():
    from games.car_game import get_car_html
    html = get_car_html("TestPlayer", 9999)
    assert "<canvas" in html
    assert "gameCanvas" in html


def test_snake_html_escapes_xss():
    from games.snake_game import get_snake_html
    html = get_snake_html('<img src=x onerror=alert(1)>', 0)
    assert "<img" not in html


def test_car_html_escapes_xss():
    from games.car_game import get_car_html
    html = get_car_html('<script>evil()</script>', 0)
    assert "<script>evil" not in html


def test_snake_html_has_postmessage():
    from games.snake_game import get_snake_html
    html = get_snake_html("P", 0)
    assert "postMessage" in html


def test_car_html_has_postmessage():
    from games.car_game import get_car_html
    html = get_car_html("P", 0)
    assert "postMessage" in html


# ── scores.json file structure ────────────────────────────────────────────────
def test_scores_json_structure(tmp_path, monkeypatch):
    """scores.json must be a JSON array of dicts with required keys."""
    import utils.db as db
    monkeypatch.setattr(db, "_DATA_DIR", tmp_path)
    monkeypatch.setattr(db, "_SCORES_FILE", tmp_path / "scores.json")
    monkeypatch.setattr(db, "_SCORES_TMP", tmp_path / "scores.json.tmp")
    db.init_db()
    db.add_score("Alice", "quiz", 1500, metadata={"category": "Tech"})

    raw = (tmp_path / "scores.json").read_text()
    data = json.loads(raw)
    assert isinstance(data, list)
    assert len(data) == 1
    rec = data[0]
    for key in ("id", "player_name", "game", "score", "played_at"):
        assert key in rec, f"Missing key: {key}"
