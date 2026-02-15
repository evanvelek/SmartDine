from typing import List, Tuple
from schemas import Restaurant, UserProfile, Context
from utils.distance import haversine_m

def rank_restaurants(cands: List[Restaurant], profile: UserProfile, ctx: Context) -> List[Tuple[Restaurant, float, str]]:
    results = []
    for r in cands:
        dist = haversine_m(ctx.lat, ctx.lng, r.lat, r.lng) if (r.lat and r.lng) else 1e9
        r.distance_m = dist
        proximity = max(0.0, 1.0 - (dist / max(ctx.max_distance_m, 1)))
        rating = (r.rating or 0.0) / 5.0
        budget = 1.0
        if r.price_level is not None:
            budget = 1.0 if r.price_level <= profile.budget_max_price_level else 0.2
        open_bonus = 0.2 if (r.is_open_now is True) else 0.0
        score = 0.55*proximity + 0.35*rating + 0.10*budget + open_bonus
        expl = []
        if r.is_open_now is True:
            expl.append("Open now")
        expl.append(f"{int(dist)}m away")
        if r.price_level is not None:
            expl.append("$"*r.price_level)
        if r.rating is not None:
            expl.append(f"{r.rating}★")
        explanation = ", ".join(expl)
        results.append((r, score, explanation))
    results.sort(key=lambda t: t[1], reverse=True)
    return results
