from typing import List
from datetime import datetime, timezone

from schemas import RecommendRequest, RecommendResponse, Recommendation, Restaurant, UserProfile
from repositories.user_repo import get_user_profile
from clients.yelp_client import YelpClient
from normalizers.yelp_normalizer import normalize_yelp
from adapters import (
    build_ranker_user,
    build_ranker_context,
    build_ranker_restaurants,
    build_user_history,
    call_ranker,
)

CUISINE_TO_YELP = {
    "japanese": "japanese",
    "mexican": "mexican",
    "coffee": "coffee",
    "vegan": "vegan",
    "thai": "thai",
    "indian": "indpak",
    "american": "tradamerican",
    "sandwiches": "sandwiches",
    "burgers": "burgers",
}


async def recommend(req: RecommendRequest) -> RecommendResponse:
    profile = get_user_profile(req.user_id) or UserProfile(user_id=req.user_id)

    req.context.max_distance_m = min(
        req.context.max_distance_m,
        profile.max_distance_m or req.context.max_distance_m
    )

    yelp = YelpClient()

    price_param = ",".join(
        str(i) for i in range(1, (profile.budget_max_price_level or 2) + 1)
    )

    categories = None
    if profile.preferred_cuisines:
        if isinstance(profile.preferred_cuisines, list):
            cuisines = [c.strip().lower() for c in profile.preferred_cuisines if c.strip()]
        else:
            cuisines = [c.strip().lower() for c in str(profile.preferred_cuisines).split(",") if c.strip()]

        mapped = [CUISINE_TO_YELP[c] for c in cuisines if c in CUISINE_TO_YELP]
        if mapped:
            categories = mapped

    raw = []
    try:
        raw = await yelp.search(
            req.context.lat,
            req.context.lng,
            radius_m=req.context.max_distance_m,
            limit=20,
            price=price_param,
            categories=categories,
            open_now=True
        )

        # Retry once without categories if the filtered search finds nothing
        if not raw and categories:
            raw = await yelp.search(
                req.context.lat,
                req.context.lng,
                radius_m=req.context.max_distance_m,
                limit=20,
                price=price_param,
                open_now=True
            )

        print("raw Yelp count:", len(raw))

    except Exception as e:
        print("Yelp error:", repr(e))
        raw = []

    candidates: List[Restaurant] = []
    if raw:
        for b in raw:
            try:
                candidates.append(normalize_yelp(b))
            except Exception:
                continue

    print("normalized candidates:", len(candidates))

    # No fake fallback for real behavior
    filtered: List[Restaurant] = [r for r in candidates if r.is_open_now is not False]

    print("filtered candidates:", len(filtered))

    ranker_user = build_ranker_user(profile)
    ranker_context = build_ranker_context(req.context)
    ranker_restaurants, original_lookup = build_ranker_restaurants(filtered)
    user_history = build_user_history(req.user_id)


    ranked = call_ranker(
        restaurants=ranker_restaurants,
        user=ranker_user,
        context=ranker_context,
        user_history=user_history
    )

    print("ranked count:", len(ranked))

    top = []
    for ranker_r, score, score_breakdown in ranked[:3]:
        original = original_lookup.get(ranker_r.restaurant_id)

        if original is None:
            continue

        explanation = (
            f"{original.name}: distance={score_breakdown['distance']:.2f}, "
            f"price={score_breakdown['price']:.2f}, "
            f"diet={score_breakdown['dietary_match']:.2f}, "
            f"time={score_breakdown['time_match']:.2f}, "
            f"pref={score_breakdown['preference_score']:.2f}, "
            f"history={score_breakdown['history_score']:.2f}"
        )

        top.append(
            Recommendation(
                **original.model_dump(),
                explanation=explanation
            )
        )


    return RecommendResponse(
        generated_at=datetime.now(timezone.utc).isoformat(),
        recommendations=top
    )




async def debug_recommend(req: RecommendRequest) -> dict:
    profile = get_user_profile(req.user_id) or UserProfile(user_id=req.user_id)

    req.context.max_distance_m = min(
        req.context.max_distance_m,
        profile.max_distance_m or req.context.max_distance_m
    )

    yelp = YelpClient()

    price_param = ",".join(
        str(i) for i in range(1, (profile.budget_max_price_level or 2) + 1)
    )

    categories = None
    if profile.preferred_cuisines:
        if isinstance(profile.preferred_cuisines, list):
            cuisines = [c.strip().lower() for c in profile.preferred_cuisines if c.strip()]
        else:
            cuisines = [c.strip().lower() for c in str(profile.preferred_cuisines).split(",") if c.strip()]

        mapped = [CUISINE_TO_YELP[c] for c in cuisines if c in CUISINE_TO_YELP]
        if mapped:
            categories = mapped

    raw = []
    try:
        raw = await yelp.search(
            req.context.lat,
            req.context.lng,
            radius_m=req.context.max_distance_m,
            limit=20,
            price=price_param,
            categories=categories,
            open_now=True
        )

        if not raw and categories:
            raw = await yelp.search(
                req.context.lat,
                req.context.lng,
                radius_m=req.context.max_distance_m,
                limit=20,
                price=price_param,
                open_now=True
            )

    except Exception as e:
        print("Yelp error:", repr(e))
        raw = []

    candidates: List[Restaurant] = []
    if raw:
        for b in raw:
            try:
                candidates.append(normalize_yelp(b))
            except Exception:
                continue

    filtered: List[Restaurant] = [r for r in candidates if r.is_open_now is not False]

    ranker_user = build_ranker_user(profile)
    ranker_context = build_ranker_context(req.context)
    ranker_restaurants, original_lookup = build_ranker_restaurants(filtered)
    user_history = build_user_history(req.user_id)

    ranked = call_ranker(
        restaurants=ranker_restaurants,
        user=ranker_user,
        context=ranker_context,
        user_history=user_history
    )

    def serialize_ranker_restaurant(r):
        return {
            "restaurant_id": r.restaurant_id,
            "name": r.name,
            "cuisine_type": r.cuisine_type,
            "price_level": r.price_level,
            "location": r.location,
            "hours": r.hours,
            "rating": r.rating,
            "dietary_options": r.dietary_options,
            "service_style": r.service_style,
        }

    return {
        "request_context": req.context.model_dump(),
        "user_profile": profile.model_dump(),
        "yelp_request": {
            "lat": req.context.lat,
            "lng": req.context.lng,
            "radius_m": req.context.max_distance_m,
            "limit": 20,
            "price": price_param,
            "categories": categories,
            "open_now": True,
        },
        "raw_yelp_count": len(raw),
        "raw_yelp_sample": raw[:3],
        "normalized_candidates": [r.model_dump() for r in candidates],
        "filtered_candidates": [r.model_dump() for r in filtered],
        "ranker_input": {
            "user": {
                "user_id": ranker_user.user_id,
                "dietary_restrictions": ranker_user.dietary_restrictions,
                "cuisine_preferences": ranker_user.cuisine_preferences,
                "budget_level": ranker_user.budget_level,
                "dining_style": ranker_user.dining_style,
                "max_distance": ranker_user.max_distance,
            },
            "context": {
                "current_time": str(ranker_context.current_time),
                "current_location": ranker_context.current_location,
                "available_time": ranker_context.available_time,
                "transportation_mode": ranker_context.transportation_mode,
            },
            "restaurants": [serialize_ranker_restaurant(r) for r in ranker_restaurants],
            "user_history": [],
        },
        "ranker_output": [
            {
                "restaurant_id": r.restaurant_id,
                "name": r.name,
                "overall_score": score,
                "score_breakdown": breakdown,
            }
            for r, score, breakdown in ranked
        ],
    }