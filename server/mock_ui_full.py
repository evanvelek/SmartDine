"""
mock_ui_full.py

This script simulates a frontend client (UI) interacting with the SmartDine backend API.
It exercises the full pipeline:

UI → Server → Yelp → Normalization → Ranker → Response → UI

It also optionally logs restaurant visits so that the ranking engine can later
incorporate visit history into its recommendations.

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
# Utility function to get user coordinates
# -------------------------------------------------------------
def detect_location():
    r = requests.get("http://ip-api.com/json/")
    data = r.json()
    return data["lat"], data["lon"]


# -------------------------------------------------------------
# Utility function for printing JSON responses in a readable way
# -------------------------------------------------------------
def pretty_print(title, data):
    """
    Prints formatted JSON output with a clear section header.

    This is used to make the console output easy to read when
    multiple API calls are executed in sequence.
    """
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(json.dumps(data, indent=2))


# -------------------------------------------------------------
# Create or update a user profile in the backend
# -------------------------------------------------------------
def upsert_profile():
    """
    Sends a POST request to the /profile endpoint.

    This simulates the UI saving user preferences such as:
    - dietary restrictions
    - preferred cuisines
    - budget
    - dining style
    - maximum travel distance
    """

    payload = {
        "user_id": USER_ID,
        "diet_restrictions": "vegetarian",
        "preferred_cuisines": "japanese,mexican,coffee",
        "budget_max_price_level": 2,
        "dining_style": "casual",
        "max_distance_m": 2000
    }

    r = requests.post(f"{BASE_URL}/profile", json=payload)

    # If the server returns an error, print useful debugging info
    if not r.ok:
        print("STATUS:", r.status_code)
        print("BODY:", r.text)
        r.raise_for_status()

    pretty_print("PROFILE UPSERT RESPONSE", r.json())


# -------------------------------------------------------------
# Request restaurant recommendations from the backend
# -------------------------------------------------------------
def recommend(lat, lng, time_available_min, max_distance_m=2000,
              time_of_day="lunch", transport_mode="walk"):
    """
    Calls the /recommend endpoint.

    This represents the core SmartDine use case where the UI asks
    the backend for restaurant suggestions based on the user's
    current situation.

    Parameters simulate context collected by the UI:
    - location (lat/lng)
    - time available
    - distance willing to travel
    - time of day
    - transportation mode
    """

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

    r = requests.post(f"{BASE_URL}/recommend", json=payload)

    # Raise error if server returned failure
    r.raise_for_status()

    data = r.json()

    pretty_print(
        f"RECOMMEND RESPONSE [{time_of_day}, {transport_mode}, {time_available_min} min]",
        data
    )

    return data


# -------------------------------------------------------------
# Log a restaurant visit
# -------------------------------------------------------------
def log_visit(restaurant_id, meal_type="lunch", visit_rating=4):
    """
    Sends a POST request to /visit to record that the user
    actually visited a recommended restaurant.

    This enables the ranking engine to build user history and
    adapt future recommendations.

    If the backend has not implemented /visit yet, the function
    fails gracefully and continues.
    """

    payload = {
        "user_id": USER_ID,
        "restaurant_id": restaurant_id,
        "timestamp": datetime.utcnow().isoformat(),
        "visit_rating": visit_rating,
        "context": {
            "day_of_week": datetime.now().strftime("%A"),
            "meal_type": meal_type
        }
    }

    try:
        r = requests.post(f"{BASE_URL}/visit", json=payload, timeout=5)

        # If /visit endpoint is not implemented, skip cleanly
        if r.status_code == 404:
            print("\n[INFO] /visit endpoint not implemented yet. Skipping visit logging.")
            return

        r.raise_for_status()
        pretty_print("VISIT LOG RESPONSE", r.json())

    except requests.RequestException as e:
        print(f"\n[INFO] Visit logging skipped: {e}")


# -------------------------------------------------------------
# Helper: choose the top recommendation
# -------------------------------------------------------------
def pick_top_restaurant(response_json):
    """
    Extracts the highest ranked restaurant from the recommendation
    response.

    This simulates a user selecting the top recommendation.
    """

    recs = response_json.get("recommendations", [])

    if not recs:
        return None

    return recs[0]["id"]


# -------------------------------------------------------------
# Full demo scenario
# -------------------------------------------------------------
def run_demo():
    """
    Executes several realistic recommendation scenarios.

    Each scenario:
    1. Requests recommendations
    2. Picks the top suggestion
    3. Logs a visit to build user history
    """

    # ---------------------------------------------------------
    # 1) Create or update the user profile
    # ---------------------------------------------------------
    upsert_profile()

    # ---------------------------------------------------------
    # 2) Lunch near campus (moderate time available)
    # ---------------------------------------------------------
    lat, lng = detect_location()

    resp1 = recommend(
        lat,
        lng,
        time_available_min=30,
        max_distance_m=2000,
        time_of_day="lunch",
        transport_mode="walk"
    )

    chosen = pick_top_restaurant(resp1)

    if chosen:
        log_visit(chosen, meal_type="lunch", visit_rating=4)

    # ---------------------------------------------------------
    # 3) Quick snack / coffee break
    # ---------------------------------------------------------
    resp2 = recommend(
        lat=33.6405,
        lng=-117.8443,
        time_available_min=10,
        max_distance_m=1200,
        time_of_day="snack",
        transport_mode="walk"
    )

    chosen = pick_top_restaurant(resp2)

    if chosen:
        log_visit(chosen, meal_type="snack", visit_rating=5)

    # ---------------------------------------------------------
    # 4) Dinner scenario (more time available)
    # ---------------------------------------------------------
    resp3 = recommend(
        lat=33.6405,
        lng=-117.8443,
        time_available_min=60,
        max_distance_m=4000,
        time_of_day="dinner",
        transport_mode="drive"
    )

    chosen = pick_top_restaurant(resp3)

    if chosen:
        log_visit(chosen, meal_type="dinner", visit_rating=4)

    # ---------------------------------------------------------
    # 5) Repeat lunch scenario to observe possible history effects
    # ---------------------------------------------------------
    resp4 = recommend(
        lat=33.6405,
        lng=-117.8443,
        time_available_min=25,
        max_distance_m=2000,
        time_of_day="lunch",
        transport_mode="walk"
    )

    chosen = pick_top_restaurant(resp4)

    if chosen:
        log_visit(chosen, meal_type="lunch", visit_rating=5)


# -------------------------------------------------------------
# Script entry point
# -------------------------------------------------------------
if __name__ == "__main__":
    run_demo()