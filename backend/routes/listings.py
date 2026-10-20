"""Listing, nearby-browse and weekly-challenge routes (Puvanan).

Uses Wong's logic (see the contract in the notes):
    backend/services/matching.py      -> haversine_km, is_within_radius
    backend/services/green_points.py  -> calculate_points
"""

from flask import Blueprint, jsonify, request

from backend.database import get_current_challenge, get_db
from backend.models import CATEGORIES, DEFAULT_RADIUS_KM, LISTING_AVAILABLE
from backend.services.green_points import calculate_points
from backend.services.matching import haversine_km, is_within_radius

listings_bp = Blueprint("listings", __name__)


def _error(message, status):
    return jsonify({"error": message}), status


def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _coords(lat, lon):
    try:
        lat = float(lat)
        lon = float(lon)
    except (TypeError, ValueError):
        return None
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None
    return lat, lon


@listings_bp.get("/api/categories")
def categories():
    return jsonify(CATEGORIES)


@listings_bp.get("/api/challenge")
def current_challenge():
    challenge = get_current_challenge()
    featured = challenge["category"]
    challenge["featured_points"] = calculate_points(featured, featured)
    challenge["regular_points"] = calculate_points("Other", featured)
    return jsonify(challenge)


@listings_bp.post("/api/listings")
def create_listing():
    data = request.get_json(silent=True) or {}
    db = get_db()

    owner_id = _to_int(data.get("owner_id"))
    owner = None
    if owner_id is not None:
        owner = db.execute("SELECT * FROM users WHERE id = ?", (owner_id,)).fetchone()
    if owner is None:
        return _error("valid owner_id is required", 400)

    title = str(data.get("title", "")).strip()
    if not title:
        return _error("title is required", 400)

    category = data.get("category")
    if category not in CATEGORIES:
        return _error(f"category must be one of: {', '.join(CATEGORIES)}", 400)

    # Default to the owner's saved location if none is given.
    if data.get("latitude") is None and data.get("longitude") is None:
        coords = (owner["latitude"], owner["longitude"])
    else:
        coords = _coords(data.get("latitude"), data.get("longitude"))
        if coords is None:
            return _error("valid latitude and longitude are required", 400)

    cur = db.execute(
        "INSERT INTO listings (owner_id, title, description, category, latitude, longitude) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (owner_id, title, str(data.get("description", "")).strip(), category, *coords),
    )
    db.commit()
    row = db.execute("SELECT * FROM listings WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(dict(row)), 201


@listings_bp.get("/api/listings")
def browse_listings():
    """Available listings. Pass lat & lon to get distances and the 2 km filter."""
    args = request.args
    radius = args.get("radius", default=DEFAULT_RADIUS_KM, type=float)
    if radius is None or radius <= 0:
        return _error("radius must be a positive number", 400)
    include_far = args.get("include_far", "false").lower() == "true"
    category = args.get("category")
    exclude_user_id = args.get("exclude_user_id", type=int)

    coords = None
    if "lat" in args or "lon" in args:
        coords = _coords(args.get("lat"), args.get("lon"))
        if coords is None:
            return _error("valid lat and lon are required", 400)

    query = (
        "SELECT l.*, u.name AS owner_name FROM listings l "
        "JOIN users u ON u.id = l.owner_id WHERE l.status = ?"
    )
    params = [LISTING_AVAILABLE]
    if category:
        query += " AND l.category = ?"
        params.append(category)
    if exclude_user_id is not None:
        query += " AND l.owner_id != ?"
        params.append(exclude_user_id)

    rows = get_db().execute(query, params).fetchall()
    featured_category = get_current_challenge()["category"]

    results = []
    for row in rows:
        item = dict(row)
        item["featured"] = item["category"] == featured_category
        if coords:
            distance = haversine_km(coords[0], coords[1], item["latitude"], item["longitude"])
            item["distance_km"] = round(distance, 2)
            item["within_radius"] = is_within_radius(distance, radius)
            if not item["within_radius"] and not include_far:
                continue
        results.append(item)

    if coords:
        results.sort(key=lambda i: (not i["within_radius"], i["distance_km"]))
    else:
        results.sort(key=lambda i: i["id"], reverse=True)
    return jsonify(results)


@listings_bp.get("/api/listings/<int:listing_id>")
def get_listing(listing_id):
    row = get_db().execute(
        "SELECT l.*, u.name AS owner_name FROM listings l "
        "JOIN users u ON u.id = l.owner_id WHERE l.id = ?",
        (listing_id,),
    ).fetchone()
    if row is None:
        return _error("listing not found", 404)
    item = dict(row)
    item["featured"] = item["category"] == get_current_challenge()["category"]
    return jsonify(item)