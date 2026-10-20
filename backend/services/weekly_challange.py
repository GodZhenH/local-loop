"""Weekly Green Challenge (owner: Wong).

Rotates the featured category every 7 days. Listing categories should use
the exact names in CATEGORIES so they match the featured category.
"""
from datetime import date, datetime, timedelta

CATEGORIES = ["Books & Stationery", "Clothing", "Household Items", "Recyclables"]
DESCRIPTIONS = {
    "Books & Stationery": "Give your old books, notebooks, and stationery a second life.",
    "Clothing": "Pass on wearable clothes that are still in usable condition.",
    "Household Items": "Share home essentials you no longer need.",
    "Recyclables": "Contribute eligible recyclables following local guidelines.",
}
FEATURED_REWARD = 20
# Monday the rotation started (week 1 = Books & Stationery). Change if needed.
CHALLENGE_START = date(2026, 10, 12)


def _to_date(d):
    if d is None:
        return date.today()
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, str):
        return datetime.fromisoformat(d).date()
    return d


def get_challenge_for_date(on_date=None, start=CHALLENGE_START):
    """Challenge active on a date (default today).

    Use the exchange's completion date to get the challenge that applied
    then, so later rotations never change points already earned.
    """
    d = _to_date(on_date)
    weeks = (d - start).days // 7  # floor division also works before start
    category = CATEGORIES[weeks % len(CATEGORIES)]
    week_start = start + timedelta(days=weeks * 7)
    return {
        "week_number": weeks + 1,
        "category": category,
        "description": DESCRIPTIONS[category],
        "reward_points": FEATURED_REWARD,
        "start_date": week_start.isoformat(),
        "end_date": (week_start + timedelta(days=6)).isoformat(),
    }


def get_current_challenge():
    return get_challenge_for_date(date.today())


def featured_category_for_date(on_date=None):
    return get_challenge_for_date(on_date)["category"]