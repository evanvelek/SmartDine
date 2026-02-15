from typing import List
from schemas import RecommendRequest, RecommendResponse, Recommendation, Restaurant, UserProfile
from repositories.user_repo import get_user_profile
from clients.yelp_client import YelpClient
from normalizers.yelp_normalizer import normalize_yelp
from clients.mock_provider import mock_restaurants
from ranking.simple_ranker import rank_restaurants
from datetime import datetime, timezone

async def recommend(req: RecommendRequest) -> RecommendResponse:
    profile = get_user_profile(req.user_id) or UserProfile(user_id=req.user_id)

    req.context.max_distance_m = min(req.context.max_distance_m, profile.max_distance_m or req.context.max_distance_m)

    yelp = YelpClient()
    price_param = ",".join(str(i) for i in range(1, (profile.budget_max_price_level or 2)+1))
    raw = []
    try:
        raw = await yelp.search(req.context.lat, req.context.lng, radius_m=req.context.max_distance_m, limit=20, price=price_param, open_now=True)
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

    if not candidates:
        candidates = mock_restaurants(req.context.lat, req.context.lng)

    filtered: List[Restaurant] = [r for r in candidates if r.is_open_now is not False]

    ranked = rank_restaurants(filtered, profile, req.context)

    top = [Recommendation(**r.model_dump(), explanation=expl) for r, score, expl in ranked[:3]]

    return RecommendResponse(
        generated_at=datetime.now(timezone.utc).isoformat(),
        recommendations=top
    )
