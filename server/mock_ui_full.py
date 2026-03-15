"""
mock_ui_full.py

This script simulates a frontend client (UI) interacting with the SmartDine backend API.
It exercises the full pipeline:

UI → Server → Yelp → Normalization → Ranker → Response → UI

It also logs restaurant visits and favorites so the backend can be tested end to end.

This script is meant for:
- backend integration testing
- verifying API endpoints
- demonstrating end-to-end system behavior
"""

import json
import requests
from datetime import datetime, UTC

# Base URL where the FastAPI backend is running
BASE_URL = "http://127.0.0.1:8000"

# Test user for the demo
USER_ID = "1001"


# -------------------------------------------------------------
# Utility function for printing JSON responses in a readable way
# -------------------------------------------------------------
def pretty_print(title, data):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(json.dumps(data, indent=2))


# -------------------------------------------------------------
# Utility: safe JSON/body printing on HTTP failures
# -------------------------------------------------------------
def print_http_error(response):
    print("STATUS:", response.status_code)
    try:
        print("BODY:", json.dumps(response.json(), indent=2))
    except Exception:
        print("BODY:", response.text)


# -------------------------------------------------------------
# Utility: basic assertion helper for test flow
# -------------------------------------------------------------
def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


# -------------------------------------------------------------
# Utility function to get user coordinates
# -------------------------------------------------------------
def detect_location():
    """
    Detects approximate location for testing. Falls back to UCI area if lookup fails.
    """
    try:
        r = requests.get("http://ip-api.com/json/", timeout=5)
        r.raise_for_status()
        data = r.json()
        lat = data.get("lat")
        lon = data.get("lon")
        if lat is not None and lon is not None:
            return lat, lon
    except Exception:
        pass

    # Fallback: UCI area
    return 33.6405, -117.8443


# -------------------------------------------------------------
# Create or update a user profile in the backend
# -------------------------------------------------------------
def upsert_profile():
    payload = {
        "user_id": USER_ID,
        "diet_restrictions": "",
        "preferred_cuisines": "japanese,mexican,coffee",
        "budget_max_price_level": 2,
        "dining_style": "casual",
        "max_distance_m": 2000
    }

    r = requests.post(f"{BASE_URL}/profile", json=payload, timeout=10)

    if not r.ok:
        print_http_error(r)
        r.raise_for_status()

    data = r.json()
    pretty_print("PROFILE UPSERT RESPONSE", data)
    assert_true(data.get("ok") is True, "POST /profile did not return ok=true")
    return data


# -------------------------------------------------------------
# Helper: get user profile
# -------------------------------------------------------------
def get_profile(user_id):
    r = requests.get(f"{BASE_URL}/profile/{user_id}", timeout=10)

    if not r.ok:
        print_http_error(r)
        r.raise_for_status()

    data = r.json()
    pretty_print("GET PROFILE RESPONSE", data)

    assert_true(data.get("user_id") == user_id, "GET /profile returned wrong user_id")
    return data


# -------------------------------------------------------------
# Request restaurant recommendations from the backend
# -------------------------------------------------------------
def recommend(lat, lng, time_available_min, max_distance_m=2000,
              time_of_day="lunch", transport_mode="walk"):
    payload = {
        "user_id": USER_ID,
        "context": {
            "lat": lat,
            "lng": lng,
            "time_available_min": time_available_min,
            "max_distance_m": max_distance_m,
            "time_of_day": time_of_day,
            "transport_mode": transport_mode
        }
    }

    r = requests.post(f"{BASE_URL}/recommend", json=payload, timeout=20)

    if not r.ok:
        print_http_error(r)
        r.raise_for_status()

    data = r.json()

    pretty_print(
        f"RECOMMEND RESPONSE [{time_of_day}, {transport_mode}, {time_available_min} min]",
        data
    )

    validate_recommend_response(data)
    return data


# -------------------------------------------------------------
# Helper: inspect what gets passed into the ranker
# -------------------------------------------------------------
def inspect_ranker_input(lat, lng, time_available_min, max_distance_m=2000,
                         time_of_day="lunch", transport_mode="walk"):
    payload = {
        "user_id": USER_ID,
        "context": {
            "lat": lat,
            "lng": lng,
            "time_available_min": time_available_min,
            "max_distance_m": max_distance_m,
            "time_of_day": time_of_day,
            "transport_mode": transport_mode
        }
    }

    r = requests.post(f"{BASE_URL}/debug/recommend", json=payload, timeout=20)

    if not r.ok:
        print_http_error(r)
        r.raise_for_status()

    data = r.json()
    pretty_print(
        f"DEBUG RECOMMEND [{time_of_day}, {transport_mode}, {time_available_min} min]",
        data
    )

    restaurants = data.get("ranker_input", {}).get("restaurants", [])
    assert_true(isinstance(restaurants, list), "debug/recommend missing ranker_input.restaurants")

    return data


# -------------------------------------------------------------
# Validate recommendation response shape
# -------------------------------------------------------------
def validate_recommend_response(data):
    assert_true("generated_at" in data, "Missing generated_at in /recommend response")
    assert_true("recommendations" in data, "Missing recommendations in /recommend response")
    assert_true(isinstance(data["recommendations"], list), "recommendations must be a list")

    for i, rec in enumerate(data["recommendations"]):
        assert_true("id" in rec, f"Recommendation {i} missing id")
        assert_true("name" in rec, f"Recommendation {i} missing name")
        assert_true("source" in rec, f"Recommendation {i} missing source")
        assert_true("lat" in rec, f"Recommendation {i} missing lat")
        assert_true("lng" in rec, f"Recommendation {i} missing lng")
        assert_true("categories" in rec, f"Recommendation {i} missing categories")
        assert_true("dietary_options" in rec, f"Recommendation {i} missing dietary_options")
        assert_true("description" in rec, f"Recommendation {i} missing description")
        assert_true("explanation" in rec, f"Recommendation {i} missing explanation")


# -------------------------------------------------------------
# Log a restaurant visit
# -------------------------------------------------------------
def log_visit(restaurant_id, meal_type="lunch", visit_rating=4):
    payload = {
        "user_id": USER_ID,
        "restaurant_id": restaurant_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "visit_rating": visit_rating,
        "context": {
            "day_of_week": datetime.now().strftime("%A"),
            "meal_type": meal_type
        }
    }

    r = requests.post(f"{BASE_URL}/visit", json=payload, timeout=10)

    if not r.ok:
        print_http_error(r)
        r.raise_for_status()

    data = r.json()
    pretty_print("VISIT LOG RESPONSE", data)
    assert_true(data.get("ok") is True, "POST /visit did not return ok=true")
    return data


# -------------------------------------------------------------
# Helper: pick top recommendation object
# -------------------------------------------------------------
def pick_top_recommendation(response_json):
    recs = response_json.get("recommendations", [])
    if not recs:
        return None
    return recs[0]


# -------------------------------------------------------------
# Helper: add favorite
# -------------------------------------------------------------
def add_favorite(user_id, restaurant):
    payload = {
        "user_id": user_id,
        "restaurant_id": restaurant["id"],
        "name": restaurant["name"],
        "address": restaurant.get("address"),
        "rating": restaurant.get("rating"),
        "description": restaurant.get("description"),
    }

    r = requests.post(f"{BASE_URL}/favorites", json=payload, timeout=10)

    if not r.ok:
        print_http_error(r)
        r.raise_for_status()

    data = r.json()
    pretty_print("ADD FAVORITE RESPONSE", data)
    assert_true(data.get("ok") is True, "POST /favorites did not return ok=true")
    return data


# -------------------------------------------------------------
# Helper: get favorites
# -------------------------------------------------------------
def get_favorites(user_id):
    r = requests.get(f"{BASE_URL}/favorites/{user_id}", timeout=10)

    if not r.ok:
        print_http_error(r)
        r.raise_for_status()

    data = r.json()
    pretty_print("GET FAVORITES RESPONSE", data)

    assert_true("favorites" in data, "GET /favorites missing favorites key")
    assert_true(isinstance(data["favorites"], list), "favorites must be a list")
    return data


# -------------------------------------------------------------
# Helper: ensure a specific favorite is present
# -------------------------------------------------------------
def assert_favorite_present(favorites_response, restaurant_id):
    favorites = favorites_response.get("favorites", [])
    found = any(f.get("id") == restaurant_id for f in favorites if isinstance(f, dict))
    assert_true(found, f"Favorite {restaurant_id} was not found in GET /favorites response")


# -------------------------------------------------------------
# Helper: delete user profile
# -------------------------------------------------------------
def delete_profile(user_id=USER_ID):
    r = requests.delete(f"{BASE_URL}/profile/{user_id}", timeout=10)

    if r.status_code == 404:
        data = {"status": 404, "body": r.json()}
        pretty_print("DELETE PROFILE RESPONSE", data)
        return data

    if not r.ok:
        print_http_error(r)
        r.raise_for_status()

    data = r.json()
    pretty_print("DELETE PROFILE RESPONSE", data)
    assert_true(data.get("ok") is True, "DELETE /profile did not return ok=true")
    return data


# -------------------------------------------------------------
# Helper: verify deleted profile is gone
# -------------------------------------------------------------
def verify_profile_deleted(user_id):
    r = requests.get(f"{BASE_URL}/profile/{user_id}", timeout=10)

    assert_true(r.status_code == 404, "Expected GET /profile after delete to return 404")

    try:
        data = r.json()
    except Exception:
        data = {"status": r.status_code, "body": r.text}

    pretty_print("VERIFY PROFILE DELETED", data)
    return data


# -------------------------------------------------------------
# Helper: verify favorites are cleared after user deletion
# -------------------------------------------------------------
def verify_favorites_cleared(user_id):
    r = requests.get(f"{BASE_URL}/favorites/{user_id}", timeout=10)

    if not r.ok:
        print_http_error(r)
        r.raise_for_status()

    data = r.json()
    pretty_print("VERIFY FAVORITES CLEARED", data)

    favorites = data.get("favorites", [])
    assert_true(favorites == [], "Expected favorites to be empty after deleting user")
    return data


# -------------------------------------------------------------
# Full demo scenario
# -------------------------------------------------------------
def run_demo():
    """
    Executes a complete backend interface test:
    1. Upsert profile
    2. Get profile
    3. Inspect ranker input
    4. Recommend restaurants
    5. Save a favorite
    6. Read favorites
    7. Log visits
    8. Repeat recommendation scenarios
    9. Delete user
    10. Verify cleanup
    """

    # 0) Create or update the user profile
    upsert_profile()

    # 1) Get user profile
    get_profile(USER_ID)

    # 2) Detect test location
    lat, lng = detect_location()
    print(f"\nDetected test location: lat={lat}, lng={lng}")

    # 3) Inspect ranker input and verify restaurant data shape
    debug_data = inspect_ranker_input(
        lat,
        lng,
        time_available_min=30,
        max_distance_m=2000,
        time_of_day="lunch",
        transport_mode="walk"
    )

    debug_restaurants = debug_data.get("ranker_input", {}).get("restaurants", [])
    if debug_restaurants:
        pretty_print("SAMPLE RANKER INPUT RESTAURANT", debug_restaurants[0])

    # 4) Lunch scenario
    resp1 = recommend(
        lat,
        lng,
        time_available_min=30,
        max_distance_m=2000,
        time_of_day="lunch",
        transport_mode="walk"
    )

    top_restaurant = pick_top_recommendation(resp1)
    assert_true(top_restaurant is not None, "No top recommendation returned for lunch scenario")

    # 5) Save favorite and verify favorites endpoint
    add_favorite(USER_ID, top_restaurant)
    favorites_response = get_favorites(USER_ID)
    assert_favorite_present(favorites_response, top_restaurant["id"])

    # 6) Log visit for top lunch result
    log_visit(top_restaurant["id"], meal_type="lunch", visit_rating=4)

    # 7) Quick snack / coffee break
    resp2 = recommend(
        lat=lat,
        lng=lng,
        time_available_min=10,
        max_distance_m=1200,
        time_of_day="snack",
        transport_mode="walk"
    )

    top2 = pick_top_recommendation(resp2)
    if top2:
        log_visit(top2["id"], meal_type="snack", visit_rating=5)

    # 8) Dinner scenario
    resp3 = recommend(
        lat=lat,
        lng=lng,
        time_available_min=60,
        max_distance_m=4000,
        time_of_day="dinner",
        transport_mode="drive"
    )

    top3 = pick_top_recommendation(resp3)
    if top3:
        log_visit(top3["id"], meal_type="dinner", visit_rating=4)

    # 9) Repeat lunch scenario to observe possible history effects
    resp4 = recommend(
        lat=lat,
        lng=lng,
        time_available_min=25,
        max_distance_m=2000,
        time_of_day="lunch",
        transport_mode="walk"
    )

    top4 = pick_top_recommendation(resp4)
    if top4:
        log_visit(top4["id"], meal_type="lunch", visit_rating=5)

    # 10) Check favorites again before deletion
    get_favorites(USER_ID)

    # 11) Delete the user and all associated data
    delete_profile(USER_ID)

    # 12) Verify cleanup
    verify_profile_deleted(USER_ID)
    verify_favorites_cleared(USER_ID)

    print("\nAll server interface tests completed successfully.")


# -------------------------------------------------------------
# Script entry point
# -------------------------------------------------------------
if __name__ == "__main__":
    run_demo()