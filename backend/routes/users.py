"""User, points-history and leaderboard routes (Puvanan)."""

from flask import Blueprint, jsonify, request

from backend.database import get_db

users_bp = Blueprint("users", __name__)

USER_WITH_POINTS = """
    SELECT u.id, u.name, u.latitude, u.longitude, u.created_at,
           COALESCE(SUM(t.points), 0) AS total_points
    FROM users u
    LEFT JOIN point_transactions t ON t.user_id = u.id
"""


def _error(message, status):
    return jsonify({"error": message}), status


def _coords(data):
    try:
        lat = float(data.get("latitude"))
        lon = float(data.get("longitude"))
    except (TypeError, ValueError):
        return None
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None
    return lat, lon


@users_bp.post("/api/users")
def create_user():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    if not name:
        return _error("name is required", 400)
    coords = _coords(data)
    if coords is None:
        return _error("valid latitude and longitude are required", 400)

    db = get_db()
    cur = db.execute(
        "INSERT INTO users (name, latitude, longitude) VALUES (?, ?, ?)",
        (name, coords[0], coords[1]),
    )
    db.commit()
    row = db.execute(
        USER_WITH_POINTS + " WHERE u.id = ? GROUP BY u.id", (cur.lastrowid,)
    ).fetchone()
    return jsonify(dict(row)), 201


@users_bp.get("/api/users")
def list_users():
    rows = get_db().execute(USER_WITH_POINTS + " GROUP BY u.id ORDER BY u.name").fetchall()
    return jsonify([dict(r) for r in rows])


@users_bp.get("/api/users/<int:user_id>")
def get_user(user_id):
    row = get_db().execute(
        USER_WITH_POINTS + " WHERE u.id = ? GROUP BY u.id", (user_id,)
    ).fetchone()
    if row is None:
        return _error("user not found", 404)
    return jsonify(dict(row))


@users_bp.get("/api/users/<int:user_id>/points")
def user_points(user_id):
    db = get_db()
    if db.execute("SELECT 1 FROM users WHERE id = ?", (user_id,)).fetchone() is None:
        return _error("user not found", 404)

    rows = db.execute(
        "SELECT id, exchange_id, points, reason, created_at "
        "FROM point_transactions WHERE user_id = ? ORDER BY id DESC",
        (user_id,),
    ).fetchall()
    transactions = [dict(r) for r in rows]
    return jsonify(
        {
            "user_id": user_id,
            "total_points": sum(t["points"] for t in transactions),
            "transactions": transactions,
        }
    )


@users_bp.get("/api/leaderboard")
def leaderboard():
    limit = request.args.get("limit", default=10, type=int)
    limit = max(1, min(limit, 100))

    rows = get_db().execute(
        """
        SELECT u.id, u.name,
               COALESCE(SUM(t.points), 0) AS total_points,
               COUNT(t.id) AS verified_contributions
        FROM users u
        LEFT JOIN point_transactions t ON t.user_id = u.id
        GROUP BY u.id
        ORDER BY total_points DESC, u.name ASC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    board = []
    for rank, row in enumerate(rows, start=1):
        entry = dict(row)
        entry["rank"] = rank
        board.append(entry)
    return jsonify(board)