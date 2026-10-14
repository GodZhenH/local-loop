from backend.green_points import calculate_points, milestone_bonus, calculate_reward

def test_featured_category_20():
    assert calculate_points("Books", "books") == 20

def test_regular_10():
    assert calculate_points("Clothing", "Books") == 10

def test_incomplete_earns_nothing():
    assert calculate_points("Books", "Books", completed=False) == 0

def test_no_duplicate_reward():
    assert calculate_points("Books", "Books", already_awarded=True) == 0

def test_featured_change_does_not_affect_past():
    assert calculate_points("Books", "Books") == 20
    assert calculate_points("Books", "Clothing") == 10  # new week, new call

def test_milestone():
    assert milestone_bonus(5) == 50
    assert milestone_bonus(4) == 0
    assert milestone_bonus(0) == 0

def test_reward_breakdown():
    assert calculate_reward("Books", "Books", 5) == {"base": 20, "bonus": 50, "total": 70}
    assert calculate_reward("Books", "Books", 5, completed=False)["total"] == 0