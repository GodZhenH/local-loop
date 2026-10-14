"""Nearby matching for Local Loop (owner: Wong).

Uses the Haversine formula to measure distance between coordinates and
filters listings to the default 2 km matching radius.
"""
from math import asin, cos, radians, sin, sqrt

EARTH_RADIUS_KM = 6371.0088
DEFAULT_RADIUS_KM = 2.0
AVAILABLE_STATUS = "available"


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance in kilometres between two (lat, lon) points."""
    for v in (lat1, lon1, lat2, lon2):
        if v is None:
            raise ValueError("Coordinates must not be None")
    if not (-90 <= lat1 <= 90 and -90 <= lat2 <= 90):
        raise ValueError("Latitude must be between -90 and 90")
    if not (-180 <= lon1 <= 180 and -180 <= lon2 <= 180):
        raise ValueError("Longitude must be between -180 and 180")

    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = phi2 - phi1
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * asin(sqrt(a))


def is_within_radius(distance_km, radius_km=DEFAULT_RADIUS_KM):
    """True if distance is inside the radius. The limit itself (2.0 km) counts."""
    # Round to metre precision so 2.0 km exactly is not lost to float noise.
    return round(distance_km, 3) <= radius_km


def find_nearby_items(user_lat, user_lon, listings,
                      radius_km=DEFAULT_RADIUS_KM, only_available=True):
    """Return listings within radius, nearest first.

    Each listing is a dict with 'latitude', 'longitude' and 'status'.
    Returned items are copies with an added 'distance_km' (rounded to 2 dp).
    Listings that are reserved/completed are skipped unless only_available=False.
    """
    nearby = []
    for item in listings:
        if only_available and item.get("status") != AVAILABLE_STATUS:
            continue
        try:
            d = haversine_km(user_lat, user_lon,
                             item["latitude"], item["longitude"])
        except (KeyError, ValueError):
            continue  # skip listings with missing/invalid coordinates
        if is_within_radius(d, radius_km):
            nearby.append({**item, "distance_km": round(d, 2)})
    nearby.sort(key=lambda x: x["distance_km"])
    return nearby