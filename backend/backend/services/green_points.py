"""Green Points rules for Local Loop (owner: Wong).

Pure functions: the backend passes in the featured category that applies at
the time the exchange is completed, so changing next week's challenge never
alters points already earned.
"""

REGULAR_POINTS = 10
FEATURED_POINTS = 20
MILESTONE_BONUS = 50
MILESTONE_EVERY = 5  # bonus every N verified exchanges (team can change)


def _norm(category):
    return (category or "").strip().lower()


def calculate_points(item_category, featured_category, completed=True,
                     already_awarded=False):
    """Points for one exchange.

    - 0 unless the exchange is completed AND verified (completed=True)
    - 0 if this exchange was already rewarded (no duplicates)
    - 20 if item category matches the featured category at completion time
    - otherwise 10
    """
    if not completed or already_awarded:
        return 0
    if _norm(item_category) and _norm(item_category) == _norm(featured_category):
        return FEATURED_POINTS
    return REGULAR_POINTS


def milestone_bonus(verified_exchange_count, every=MILESTONE_EVERY):
    """50-point bonus when a user's verified exchange count hits a multiple of `every`."""
    if verified_exchange_count > 0 and verified_exchange_count % every == 0:
        return MILESTONE_BONUS
    return 0


def calculate_reward(item_category, featured_category, verified_exchange_count,
                     completed=True, already_awarded=False):
    """Full reward breakdown for a just-completed exchange.

    verified_exchange_count = the user's verified exchanges INCLUDING this one.
    Returns {'base': int, 'bonus': int, 'total': int}.
    """
    base = calculate_points(item_category, featured_category,
                            completed, already_awarded)
    bonus = milestone_bonus(verified_exchange_count) if base else 0
    return {"base": base, "bonus": bonus, "total": base + bonus}