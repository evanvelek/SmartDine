# server/adapters.py

import json
from datetime import datetime
from ranker.models import User, Restaurant, Context
from ranker.ranking import rank_restaurants
from ranker.models import VisitHistory
from repositories.user_repo import get_user_history

METER_TO_MILES = 1 / 1609.34


def _split_csv(value):
    if not value:
        return []
    if isinstance(value, list):
        return value
    return [x.strip() for x in str(value).split(",") if x.strip()]


def build_ranker_user(profile):
    return User(
        user_id=int(profile.user_id) if str(profile.user_id).isdigit() else abs(hash(profile.user_id)) % (10**8),
        dietary_restrictions=_split_csv(profile.diet_restrictions),
        cuisine_preferences=_split_csv(profile.preferred_cuisines),
        budget_level=profile.budget_max_price_level or 2,
        dining_style=profile.dining_style or "casual",
        max_distance=(profile.max_distance_m or 2000) * METER_TO_MILES
    )


def build_ranker_context(ctx):
    transport = ctx.transport_mode or "walking"
    if transport == "walk":
        transport = "walking"
    elif transport == "drive":
        transport = "driving"

    return Context(
        current_time=datetime.now(),
        current_location={
            "latitude": ctx.lat,
            "longitude": ctx.lng
        },
        available_time=ctx.time_available_min,
        transportation_mode=transport
    )


def build_ranker_restaurants(restaurants):
    ranker_restaurants = []
    original_lookup = {}

    for r in restaurants:
        rid = abs(hash(r.id)) % (10**8)

        ranker_r = Restaurant(
            restaurant_id=rid,
            name=r.name,
            cuisine_type=r.categories or [],
            price_level=r.price_level or 2,
            location={
                "latitude": r.lat,
                "longitude": r.lng
            },
            hours={},
            rating=r.rating or 0.0,
            dietary_options=[],
            service_style="casual"
        )

        ranker_restaurants.append(ranker_r)
        original_lookup[rid] = r

    return ranker_restaurants, original_lookup


def build_restaurants_dict(restaurants):
    return {r.restaurant_id: r for r in restaurants}


def build_user_history():
    return []


def call_ranker(restaurants, user, context, user_history):
    restaurants_dict = build_restaurants_dict(restaurants)

    return rank_restaurants(
        restaurants=restaurants,
        user=user,
        context=context,
        user_history=user_history,
        restaurants_dict=restaurants_dict,
        current_time=context.current_time
    )


def build_user_history(user_id: str):
    rows = get_user_history(user_id)
    visits = []

    for row in rows:
        visits.append(
            VisitHistory(
                visit_id=row["visit_id"] if isinstance(row, dict) else row[0],
                user_id=int(row["user_id"]) if isinstance(row, dict) and str(row["user_id"]).isdigit()
                       else abs(hash(row["user_id"] if isinstance(row, dict) else row[1])) % (10**8),
                restaurant_id=abs(hash(row["restaurant_id"] if isinstance(row, dict) else row[2])) % (10**8),
                timestamp=datetime.fromisoformat(row["timestamp"] if isinstance(row, dict) else row[3]),
                visit_rating=row["visit_rating"] if isinstance(row, dict) else row[4],
                context=json.loads(row["context_json"] if isinstance(row, dict) else row[5]) if (row["context_json"] if isinstance(row, dict) else row[5]) else {}
            )
        )

    return visits