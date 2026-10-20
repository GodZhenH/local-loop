"""SQLite connection helpers for Local Loop (Puvanan)."""

import sqlite3
from datetime import date, timedelta
from pathlib import Path

from flask import current_app, g

from backend.models import CHALLENGE_ROTATION, SCHEMA

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "local_loop.db"


def get_db():
    """One connection per request, stored on flask.g."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()


def get_current_challenge():
    """Return this week's challenge, creating it from the rotation if needed.

    The category is stored per week, so changing a later week never alters
    what earlier weeks awarded (exchanges also store featured_category).
    """
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    db = get_db()
    row = db.execute(
        "SELECT * FROM challenges WHERE week_start = ?", (monday.isoformat(),)
    ).fetchone()

    if row is None:
        week_number = monday.isocalendar()[1]
        category = CHALLENGE_ROTATION[week_number % len(CHALLENGE_ROTATION)]
        db.execute(
            "INSERT OR IGNORE INTO challenges (week_start, week_end, category) "
            "VALUES (?, ?, ?)",
            (monday.isoformat(), sunday.isoformat(), category),
        )
        db.commit()
        row = db.execute(
            "SELECT * FROM challenges WHERE week_start = ?", (monday.isoformat(),)
        ).fetchone()

    return dict(row)