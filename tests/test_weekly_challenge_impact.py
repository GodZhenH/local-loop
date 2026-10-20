from datetime import date
from backend.services.weekly_challange import get_challenge_for_date, CATEGORIES
from backend.services.impact import calculate_impact
from backend.services.green_points import build_points_transaction

def test_rotation():
    assert get_challenge_for_date(date(2026, 10, 12))["category"] == CATEGORIES[0]
    assert get_challenge_for_date(date(2026, 10, 19))["category"] == CATEGORIES[1]
    assert get_challenge_for_date(date(2026, 11, 9))["category"] == CATEGORIES[0]  # wraps

def test_past_week_unchanged():
    assert get_challenge_for_date("2026-10-14")["category"] == "Books & Stationery"

def test_impact():
    ex = [
        {"status": "completed", "giver_id": 1, "category": "Books & Stationery", "completed_at": "2026-10-13"},
        {"status": "completed", "giver_id": 2, "category": "Clothing", "completed_at": "2026-10-14"},
        {"status": "reserved", "giver_id": 3, "category": "Books & Stationery", "completed_at": None},
    ]
    pts = [{"user_id": 1, "points": 20}, {"user_id": 2, "points": 10}]
    r = calculate_impact(ex, pts, "Books & Stationery", "2026-10-12", "2026-10-18")
    assert r == {"total_completed_exchanges": 2, "green_points_awarded": 30,
                 "community_participation": 2, "weekly_challenge_progress": 1,
                 "items_reused": 2}

def test_transaction():
    ex = {"id": 7, "giver_id": 1, "category": "Clothing", "status": "completed"}
    t = build_points_transaction(ex, "Clothing", 1)
    assert t["points"] == 20 and t["user_id"] == 1
    assert build_points_transaction({**ex, "status": "claimed"}, "Clothing", 1) is None
    assert build_points_transaction(ex, "Clothing", 1, already_awarded=True) is None