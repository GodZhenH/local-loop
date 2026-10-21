"""Exchange (claim / complete / cancel) and impact-dashboard routes (Puvanan).

Uses Wong's logic (see the contract in the notes):
    backend/services/matching.py      -> haversine_km, is_within_radius
    backend/services/green_points.py  -> calculate_points
"""

import sqlite3

from flask import Blueprint, jsonify, request

from backend.database import get_current_challenge, get_db
from backend.models import (
    EXCHANGE_CANCELLED,
    EXCHANGE_COMPLETED,
    EXCHANGE_RESERVED,
    LISTING_AVAILABLE,
    LISTING_COMPLETED,
    LISTING_RESERVED,
)
from backend.services.green_points import calculate_points
from backend.services.matching import haversine_km, is_within_radius

exchanges_bp = Blueprint("exchanges", __name__)

EXCHANGE_DETAIL = """
    SELECT e.*, l.title, l.category,
           g.name AS giver_name, r.name AS receiver_name
    FROM exchanges e
    JOIN listings l ON l.id = e.listing_id
    JOIN users g ON g.id = e.giver_id
    JOIN users r ON r.id = e.receiver_id
"""


def _error(message, status):
    return jsonify({"error": message}), status


def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _exchange_detail(db, exchange_id):
    row = db.execute(EXCHANGE_DETAIL + " WHERE e.id = ?", (exchange_id,)).fetchone()
    return dict(row) if row else None


@exchanges_bp.post("/api/exchanges/claim")
def claim_listing():
    data = request.get_json(silent=True) or {}
    listing_id = _to_int(data.get("listing_id"))
    receiver_id = _to_int(data.get("receiver_id"))
    if listing_id is None or receiver_id is None:
        return _error("listing_id and receiver_id are required", 400)

    db = get_db()
    listing = db.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
    if listing is None:
        return _error("listing not found", 404)
    receiver = db.execute("SELECT * FROM users WHERE id = ?", (receiver_id,)).fetchone()
    if receiver is None:
        return _error("receiver not found", 404)

    if listing["owner_id"] == receiver_id:
        return _error("you cannot claim your own listing", 400)
    if listing["status"] != LISTING_AVAILABLE:
        return _error("listing is no longer available", 409)

    # Validate the 2 km radius on the server, not just in the UI.
    distance = haversine_km(
        receiver["latitude"], receiver["longitude"],
        listing["latitude"], listing["longitude"],
    )
    if not is_within_radius(distance):
        return _error("listing is outside your matching radius", 400)

    try:
        # Atomic reserve: only succeeds if it is still 'available'.
        cur = db.execute(
            "UPDATE listings SET status = ? WHERE id = ? AND status = ?",
            (LISTING_RESERVED, listing_id, LISTING_AVAILABLE),
        )
        if cur.rowcount == 0:
            db.rollback()
            return _error("listing was just claimed by someone else", 409)

        cur = db.execute(
            "INSERT INTO exchanges (listing_id, giver_id, receiver_id, status) "
            "VALUES (?, ?, ?, ?)",
            (listing_id, listing["owner_id"], receiver_id, EXCHANGE_RESERVED),
        )
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        return _error("listing already has an active exchange", 409)

    return jsonify(_exchange_detail(db, cur.lastrowid)), 201


@exchanges_bp.post("/api/exchanges/<int:exchange_id>/complete")
def complete_exchange(exchange_id):
    """The receiver confirms the handover; points go to the giver."""
    data = request.get_json(silent=True) or {}
    user_id = _to_int(data.get("user_id"))
    if user_id is None:
        return _error("user_id is required", 400)

    db = get_db()
    exchange = db.execute("SELECT * FROM exchanges WHERE id = ?", (exchange_id,)).fetchone()
    if exchange is None:
        return _error("exchange not found", 404)
    if exchange["status"] != EXCHANGE_RESERVED:
        return _error(f"exchange is already {exchange['status']}", 409)
    if user_id != exchange["receiver_id"]:
        return _error("only the receiver can confirm the handover", 403)

    listing = db.execute(
        "SELECT * FROM listings WHERE id = ?", (exchange["listing_id"],)
    ).fetchone()

    # The challenge applicable *now* decides the reward and is frozen on the record.
    featured_category = get_current_challenge()["category"]
    points = calculate_points(listing["category"], featured_category)
    reason = f"Completed exchange: {listing['title']}"
    if listing["category"] == featured_category:
        reason += " (featured category)"

    try:
        cur = db.execute(
            "UPDATE exchanges SET status = ?, completed_at = CURRENT_TIMESTAMP, "
            "featured_category = ?, points_awarded = ? WHERE id = ? AND status = ?",
            (EXCHANGE_COMPLETED, featured_category, points, exchange_id, EXCHANGE_RESERVED),
        )
        if cur.rowcount == 0:
            db.rollback()
            return _error("exchange was already completed or cancelled", 409)

        db.execute(
            "UPDATE listings SET status = ? WHERE id = ?",
            (LISTING_COMPLETED, exchange["listing_id"]),
        )
        # UNIQUE(exchange_id) blocks duplicate rewards.
        db.execute(
            "INSERT INTO point_transactions (user_id, exchange_id, points, reason) "
            "VALUES (?, ?, ?, ?)",
            (exchange["giver_id"], exchange_id, points, reason),
        )
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        return _error("this exchange has already been rewarded", 409)

    return jsonify(_exchange_detail(db, exchange_id))


@exchanges_bp.post("/api/exchanges/<int:exchange_id>/cancel")
def cancel_exchange(exchange_id):
    """Either party can cancel a reserved exchange; the listing becomes available again."""
    data = request.get_json(silent=True) or {}
    user_id = _to_int(data.get("user_id"))
    if user_id is None:
        return _error("user_id is required", 400)

    db = get_db()
    exchange = db.execute("SELECT * FROM exchanges WHERE id = ?", (exchange_id,)).fetchone()
    if exchange is None:
        return _error("exchange not found", 404)
    if user_id not in (exchange["giver_id"], exchange["receiver_id"]):
        return _error("only the giver or receiver can cancel", 403)
    if exchange["status"] != EXCHANGE_RESERVED:
        return _error(f"exchange is already {exchange['status']}", 409)

    cur = db.execute(
        "UPDATE exchanges SET status = ? WHERE id = ? AND status = ?",
        (EXCHANGE_CANCELLED, exchange_id, EXCHANGE_RESERVED),
    )
    if cur.rowcount == 0:
        db.rollback()
        return _error("exchange was already completed or cancelled", 409)
    db.execute(
        "UPDATE listings SET status = ? WHERE id = ?",
        (LISTING_AVAILABLE, exchange["listing_id"]),
    )
    db.commit()
    return jsonify(_exchange_detail(db, exchange_id))


@exchanges_bp.get("/api/exchanges")
def list_exchanges():
    user_id = request.args.get("user_id", type=int)
    db = get_db()
    if user_id is not None:
        rows = db.execute(
            EXCHANGE_DETAIL + " WHERE e.giver_id = ? OR e.receiver_id = ? ORDER BY e.id DESC",
            (user_id, user_id),
        ).fetchall()
    else:
        rows = db.execute(EXCHANGE_DETAIL + " ORDER BY e.id DESC").fetchall()
    return jsonify([dict(r) for r in rows])


@exchanges_bp.get("/api/impact")
def impact_dashboard():
    db = get_db()
    challenge = get_current_challenge()

    completed = db.execute(
        "SELECT COUNT(*) FROM exchanges WHERE status = ?", (EXCHANGE_COMPLETED,)
    ).fetchone()[0]
    points_awarded = db.execute(
        "SELECT COALESCE(SUM(points), 0) FROM point_transactions"
    ).fetchone()[0]
    contributors = db.execute(
        "SELECT COUNT(DISTINCT giver_id) FROM exchanges WHERE status = ?",
        (EXCHANGE_COMPLETED,),
    ).fetchone()[0]
    challenge_progress = db.execute(
        """
        SELECT COUNT(*) FROM exchanges e
        JOIN listings l ON l.id = e.listing_id
        WHERE e.status = ?
          AND l.category = ?
          AND date(e.completed_at) BETWEEN ? AND ?
        """,
        (EXCHANGE_COMPLETED, challenge["category"], challenge["week_start"], challenge["week_end"]),
    ).fetchone()[0]

    return jsonify(
        {
            "total_completed_exchanges": completed,
            "green_points_awarded": points_awarded,
            "community_participation": contributors,
            "weekly_challenge_progress": challenge_progress,
            "weekly_challenge_category": challenge["category"],
            "items_reused": completed,
        }
    )