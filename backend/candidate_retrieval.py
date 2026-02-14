from models import Restaurant
from collections import defaultdict

def filter_by_basic_criteria(restaurants, user, context):
    candidates = []
    
    for restaurant in restaurants:
        if restaurant.meets_filter_criteria(user, context):
            candidates.append(restaurant)
    
    return candidates


def filter_by_dietary_restrictions(restaurants, dietary_restrictions):
    if not dietary_restrictions:
        return restaurants
    
    compatible = []
    for restaurant in restaurants:
        can_accommodate = all(
            restriction in restaurant.dietary_options 
            for restriction in dietary_restrictions
        )
        if can_accommodate:
            compatible.append(restaurant)
    
    return compatible


def filter_by_cuisine(restaurants, preferred_cuisines):
    if not preferred_cuisines:
        return restaurants
    
    matching = []
    for restaurant in restaurants:
        if any(cuisine in preferred_cuisines for cuisine in restaurant.cuisine_type):
            matching.append(restaurant)
    
    return matching


def filter_by_price(restaurants, max_price_level):
    return [r for r in restaurants if r.price_level <= max_price_level]


def filter_by_distance(restaurants, location, max_distance):
    nearby = []
    for restaurant in restaurants:
        distance = restaurant.distance_from(location)
        if distance <= max_distance:
            nearby.append(restaurant)
    
    return nearby


def filter_by_open_hours(restaurants, check_time):
    return [r for r in restaurants if r.is_open_at(check_time)]


def filter_by_service_style(restaurants, preferred_style):
    if not preferred_style:
        return restaurants
    
    return [r for r in restaurants if r.service_style == preferred_style]

#might want all candidates for ranking, so could get rid of soft filters or make them optional
def get_candidates(all_restaurants, user, context, apply_soft_filters=True):
    candidates = filter_by_basic_criteria(all_restaurants, user, context)
    if apply_soft_filters:
        #if user has cuisine preferences, prefer those but don't exclude others
        if user.cuisine_preferences:
            preferred = filter_by_cuisine(candidates, user.cuisine_preferences)
            #onlyy use cuisine filter if it doesn't eliminate too many options
            if len(preferred) >= 3:
                candidates = preferred

        if user.dining_style:
            styled = filter_by_service_style(candidates, user.dining_style)
            if len(styled) >= 3:
                candidates = styled
    
    return candidates


def search_by_name(restaurants, search_term):
    #case-insensitive partial match
    search_term = search_term.lower()
    return [r for r in restaurants if search_term in r.name.lower()]


def get_nearby_restaurants(all_restaurants, location, radius_miles, limit=20):
    nearby = []
    
    for restaurant in all_restaurants:
        distance = restaurant.distance_from(location)
        if distance <= radius_miles:
            nearby.append((restaurant, distance))
    nearby.sort(key=lambda x: x[1])
    
    return nearby[:limit]


def get_top_rated_restaurants(restaurants, min_rating=4.0, limit=10):
    high_rated = [r for r in restaurants if r.rating >= min_rating]
    high_rated.sort(key=lambda r: r.rating, reverse=True)
    return high_rated[:limit]


#don't want to show too many of the same cuisine type unless that is specified, can get rid of this function
def variety_candidates(candidates, max_per_cuisine=3):
    
    cuisine_counts = defaultdict(int)
    varieties = []
    
    for restaurant in candidates:
        can_add = True
        for cuisine in restaurant.cuisine_type:
            if cuisine_counts[cuisine] >= max_per_cuisine:
                can_add = False
                break
        
        if can_add:
            varieties.append(restaurant)
            for cuisine in restaurant.cuisine_type:
                cuisine_counts[cuisine] += 1
    
    return varieties