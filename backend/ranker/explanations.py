#Thresholds
HIGH = 0.75
MID  = 0.45


def _bucket(score: float) -> str:
    if score >= HIGH:
        return "high"
    elif score >= MID:
        return "mid"
    else:
        return "low"


#each factor explanation fragments
def _distance_fragment(score: float, restaurant, context=None):
    b = _bucket(score)
    if b == "high":
        return "very close to you"
    elif b == "mid":
        return "a reasonable distance away"
    else:
        return None


def _price_fragment(score: float, restaurant=None, user=None):
    if restaurant is None or user is None:
        return None

    diff = restaurant.price_level - user.budget_level
    if diff == 0:
        return "right in your budget"
    elif diff < 0:
        return "under your budget"
    elif diff == 1:
        return "slightly above your budget"
    else:
        return None


def _dietary_fragment(score: float, restaurant=None, user=None):
    if user is None or not user.dietary_restrictions:
        return None  # no restrictions means this factor isn't relevant
    b = _bucket(score)
    if b == "high":
        restrictions = ", ".join(user.dietary_restrictions)
        return f"accommodates your dietary needs ({restrictions})"
    elif b == "mid":
        return "partially accommodates your dietary restrictions"
    else:
        return None


def _time_fragment(score: float, context=None):
    b = _bucket(score)
    if context and context.available_time < 45:
        if b == "high":
            return "fits within your limited time"
        elif b == "mid":
            return "should be manageable in your available time"
        else:
            return None
    else:
        if b == "high":
            return f"a good fit for {context.meal_type if context else 'this meal'}"
        else:
            return None


def _preference_fragment(score: float, restaurant=None, user=None):
    if restaurant is None or user is None:
        return None
    b = _bucket(score)
    if b != "high":
        return None

    matched_cuisines = []
    if user.cuisine_preferences:
        matched_cuisines = [c for c in restaurant.cuisine_type if c in user.cuisine_preferences]

    style_match = (
        user.dining_style and
        restaurant.service_style and
        restaurant.service_style.lower() == user.dining_style.lower()
    )

    parts = []
    if matched_cuisines:
        parts.append(f"matches your {'/'.join(matched_cuisines)} preference")
    if style_match:
        parts.append(f"fits your {user.dining_style} dining style")

    return " and ".join(parts) if parts else "aligns with your preferences"


def _history_fragment(score: float, restaurant=None, context=None):
    b = _bucket(score)
    if b == "high":
        if restaurant:
            return f"you've enjoyed similar spots before"
        return "matches your past dining patterns"
    elif b == "mid":
        return "somewhat consistent with your dining history"
    else:
        return None

def generate_explanation(restaurant, user, context, score_breakdown, overall_score: float | None = None,):

    fragments = []
    fns = [
        ("preference_score", _preference_fragment,
         dict(restaurant=restaurant, user=user)),
        ("distance",         _distance_fragment,
         dict(restaurant=restaurant, context=context)),
        ("dietary_match",    _dietary_fragment,
         dict(restaurant=restaurant, user=user)),
        ("time_match",       _time_fragment,
         dict(context=context)),
        ("price",            _price_fragment,
         dict(restaurant=restaurant, user=user)),
        ("history_score",    _history_fragment,
         dict(restaurant=restaurant, context=context)),
    ]

    for key, fn, kwargs in fns:
        score = score_breakdown.get(key, 0.0)
        fragment = fn(score, **kwargs)
        if fragment:
            fragments.append(fragment)

    name = restaurant.name if restaurant else "This restaurant"

    if not fragments:
        return f"{name} is a solid nearby option."

    #use 3 fragments so explanations aren't too long
    fragments = fragments[:3]

    if len(fragments) == 1:
        return f"{name} is recommended because it's {fragments[0]}."
    elif len(fragments) == 2:
        return f"{name} is recommended because it's {fragments[0]} and {fragments[1]}."
    else:
        joined = ", ".join(fragments[:-1]) + f", and {fragments[-1]}"
        return f"{name} is recommended because it's {joined}."
