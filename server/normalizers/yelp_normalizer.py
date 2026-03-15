from typing import Any, Dict
from schemas import Restaurant

def normalize_yelp(b: Dict[str, Any]) -> Restaurant:
    coords = b.get("coordinates") or {}

    cats = [c.get("alias") or c.get("title") for c in (b.get("categories") or [])]
    cats = [c for c in cats if c]

    # NEW: detect dietary options from categories
    dietary_options = []
    for c in cats:
        c_lower = c.lower()

        if "vegetarian" in c_lower:
            dietary_options.append("vegetarian")

        elif "vegan" in c_lower:
            dietary_options.append("vegan")

        elif "gluten" in c_lower:
            dietary_options.append("gluten-free")

        elif "pescatarian" in c_lower:
            dietary_options.append("pescatarian")

        elif "keto" in c_lower:
            dietary_options.append("keto")

        elif "halal" in c_lower:
            dietary_options.append("halal")

        elif "kosher" in c_lower:
            dietary_options.append("kosher")

    price_level = None
    price = b.get("price")
    if isinstance(price, str):
        price_level = len(price)

    is_open_now = None
    if "is_closed" in b:
        is_open_now = not b["is_closed"]

    address = ", ".join((b.get("location") or {}).get("display_address") or []) or None

    rating = b.get("rating")
    reviews = b.get("review_count")

    # Build description text
    description_parts = []

    if cats:
        description_parts.append(", ".join(cats[:3]))

    if price:
        description_parts.append(f"Price: {price}")

    if rating is not None and reviews is not None:
        description_parts.append(f"Rated {rating}/5 from {reviews} reviews")
    elif rating is not None:
        description_parts.append(f"Rated {rating}/5")

    if address:
        description_parts.append(address)

    description = " • ".join(description_parts) if description_parts else None

    return Restaurant(
        id=f"yelp:{b.get('id', 'unknown')}",
        source="yelp",
        name=b.get("name") or "Unknown",
        lat=float(coords.get("latitude") or 0.0),
        lng=float(coords.get("longitude") or 0.0),
        categories=cats,
        dietary_options=dietary_options,   # NEW
        price_level=price_level,
        rating=rating,
        reviews_count=reviews,
        is_open_now=is_open_now,
        address=address,
        description=description
    )
