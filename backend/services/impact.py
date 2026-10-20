"""Community impact figures for the dashboard (owner: Wong).

Pure calculation over lists of dicts that Puvanan's database layer returns.
exchange: {'status', 'giver_id', 'category', 'completed_at'}
points transaction: {'user_id', 'points'}
"""
from datetime import date, datetime


def _d(v):
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, str):
        return datetime.fromisoformat(v).date()
    return v


def calculate_impact(exchanges, points_transactions, featured_category=None,
                     week_start=None, week_end=None):
    """Return the five dashboard numbers."""
    completed = [e for e in exchanges if e.get("status") == "completed"]

    progress = 0
    if featured_category:
        for e in completed:
            if e.get("category", "").strip().lower() != featured_category.strip().lower():
                continue
            if week_start and week_end and e.get("completed_at"):
                if not (_d(week_start) <= _d(e["completed_at"]) <= _d(week_end)):
                    continue
            progress += 1

    return {
        "total_completed_exchanges": len(completed),
        "green_points_awarded": sum(t.get("points", 0) for t in points_transactions),
        "community_participation": len({e["giver_id"] for e in completed if e.get("giver_id") is not None}),
        "weekly_challenge_progress": progress,
        "items_reused": len(completed),
    }