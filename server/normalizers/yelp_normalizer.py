from typing import Any, Dict
from schemas import Restaurant

def normalize_yelp(b: Dict[str, Any]) -> Restaurant:
    coords = b.get("coordinates") or {}
    cats = [c.get("alias") or c.get("title") for c in (b.get("categories") or [])]
    cats = [c for c in cats if c]

    price_level = None
    price = b.get("price")
    if isinstance(price, str):
        price_level = len(price)

    is_open_now = None
    if "is_closed" in b:
        is_open_now = not b["is_closed"]

    return Restaurant(
        id=f"yelp:{b.get('id', 'unknown')}",
        source="yelp",
        name=b.get("name") or "Unknown",
        lat=float(coords.get("latitude") or 0.0),
        lng=float(coords.get("longitude") or 0.0),
        categories=cats,
        price_level=price_level,
        rating=b.get("rating"),
        reviews_count=b.get("review_count"),
        is_open_now=is_open_now,
        address=", ".join((b.get("location") or {}).get("display_address") or []) or None,
    )
