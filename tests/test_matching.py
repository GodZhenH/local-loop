import pytest
from backend.matching import haversine_km, is_within_radius, find_nearby_items

ORIGIN = (3.1390, 101.6869)

def offset_north(km):
    return ORIGIN[0] + km / 111.195, ORIGIN[1]

def test_zero_distance():
    assert haversine_km(*ORIGIN, *ORIGIN) == 0

def test_known_distance_kl_to_singapore():
    d = haversine_km(3.1390, 101.6869, 1.3521, 103.8198)
    assert 300 < d < 330

def test_invalid_latitude():
    with pytest.raises(ValueError):
        haversine_km(95, 0, 0, 0)

def test_limit_is_inside():
    assert is_within_radius(2.0)
    assert not is_within_radius(2.01)

def test_find_nearby_filters_sorts_and_checks_status():
    def item(name, km, status="available"):
        lat, lon = offset_north(km)
        return {"name": name, "latitude": lat, "longitude": lon, "status": status}
    listings = [item("Clothes", 1.5), item("Textbooks", 0.8), item("Chair", 2.0),
                item("Bicycle", 3.2), item("Reserved", 0.5, "reserved")]
    result = find_nearby_items(*ORIGIN, listings)
    assert [r["name"] for r in result] == ["Textbooks", "Clothes", "Chair"]
    assert "distance_km" in result[0]

def test_bad_listing_skipped():
    assert find_nearby_items(*ORIGIN, [{"status": "available"}]) == []