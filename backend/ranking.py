'''
weights = {
    'distance': 0.25,
    'price': 0.20,
    'dietary_match': 0.15, #if the user has no dietary restrictions, this weight can be redistributed to other factors
    'time_match': 0.15,
    'preference_score': 0.10,
    'history_score': 0.15 #base it on past behavior and include decay over time
}

Adjust weights overtime based on user
-increase distance weight if time available is low
-increase dietary match weight if user has strong dietary restrictions
-at the start history weight can be redistributed to other factors until we have enough data on the user

__________________________________________________________________________________________________________________________________________
Time Decay: how much recent vs old visits influence ranking
-use exponential decay function to reduce influence of older visits
-decay_rate is 30 days(?)
-weight = 0.5 ^ (days_since_visit / decay_rate)
-require at least 3 visits before we consider it into a pattern because otherwise it might be random visits

history_score(restaurant, user_history, curr_time):
    -Restaurant Score
        -filter user history for visits to this restaurant
        -calculate decay weight for each visit
        -sum and normalize
    -Cuisine Score
        -all restaurants with the same cuisine type
        -temporal decay
        -freq = weighted_visit_count / total_visits
    -Service Style Score
        -similar to cuisine score but based on service style
        -current meal type context can also influence this score (ex: if user prefers quick service for lunch)
    -Contextual Score
        -similar restaurants that match the same context (like Mexican food midday on Fridays)
        -day_of_week + meal_type + cuisine
    
Overall Score:
history_score = (0.35 * restaurant_score) + (0.35 * cuisine_score) + (0.15 * service_style_score) + (0.15 * contextual_score)

calculate_decay_weight(visit_time, current_time, decay_rate = 30):
    days_ago = (current_time - visit_time).days
    weight = 0.5 ** (days_ago / decay_rate)

get_weighted_visit_count(visits, current_time):
    returns the sum of decay weights for a list of visits

get_cuisine_dist(user_history, current_time):
    time decay weighted distribution of cuisines in user history
    recent visits will count more towards the distribution than older visits, but it will still reflect the user's overall preferences over time



__________________________________________________________________________________________________________________________________________
Scoring Functions:
from 0 to 1

distance_score(restaurant, user, context):
    -calculate distance
    -consider transportion mode
    -closer gets a higher score

price_score(restaurant, user_budget):
    -compare restaurant price level to user budget
    -a perfect mathc would be 1
    -if over budget, score decreases significantly
    -under budget is also good 

dietary_match_score(restaurant, dietary_restrictions):
    -restaurant gets a score based on how many of the user's dietary restrictions it meets
    -if it can fully accomadate all restrictions, it gets a 1 and if none then 0

time_match_score(restaurant, context):
    -different time ranges for breakfast, lunch, dinner and sit-down vs quick service
    -typical wait times
    -check if open

preference_score(restaurant, user_preferences):
    -based on cuisine preferences, dining style, etc.
    -if it matches the user's top preferences, it gets a higher score

__________________________________________________________________________________________________________________________________________

Main Ranking Function:
rank_restaurants(restaurants, user, context, history, current_time):
    Inputs:
        -restaurants: list of restaurant objects that are already filterd
        -user: user object with preferences and restrictions
        -context: context obj w current contextual factors
        -history: list of history objects for the user
        -current_time: datetime object for current time to calculate decay
    Process:
        -for each restaurant, calculate each individual score (distance, price, dietary match, time match, preference)
        -calculate history score based on user history and current time, if no history then redstrivute weight
        -apply weights to each score and sum to get overall score
        -sort restaurants by overall score in descending order
__________________________________________________________________________________________________________________________________________
Weights Adjustments:

adjust_weights(base_weights, context, has_history):
    -if time is limited, increase distnace (0.4) and time_match (0.25) and decrease others
    -if no dietary restrictions, redistribute dietary match weight to other factors
    -if no history, redistribute history weight to other factors
    -if user has strong dietary restrictions, increase dietary match weight (0.3) and reduce others proprtionately

__________________________________________________________________________________________________________________________________________
Explanations

ranking_explanation(?):
    -important and supporting factors for choice
    -any historical context that influenced ranking
'''
from datetime import datetime
from collections import defaultdict
import history

BASE_WEIGHTS = {
    'distance': 0.25,
    'price': 0.20,
    'dietary_match': 0.15,
    'time_match': 0.15,
    'preference_score': 0.10,
    'history_score': 0.15
}

#not sure if it should be more?
MIN_VISITS_FOR_PATTERN = 3


def calculate_decay_weight(visit_time, current_time, decay_rate=30):
    days_ago = (current_time - visit_time).days
    weight = 0.5 ** (days_ago / decay_rate)
    return weight


def get_weighted_visit_count(visits, current_time, decay_rate=30):
    total_weight = 0.0
    for visit in visits:
        weight = calculate_decay_weight(visit.timestamp, current_time, decay_rate)
        total_weight += weight
    return total_weight


def get_cuisine_dist(user_history, restaurants_dict, current_time, decay_rate=30):
    cuisine_weights = defaultdict(float)
    total_weight = 0.0
    
    for visit in user_history:
        weight = calculate_decay_weight(visit.timestamp, current_time, decay_rate)
        
        restaurant = restaurants_dict.get(visit.restaurant_id)
        if restaurant:
            for cuisine in restaurant.cuisine_type:
                cuisine_weights[cuisine] += weight
                total_weight += weight
    
    if total_weight > 0:
        return {cuisine: w / total_weight for cuisine, w in cuisine_weights.items()}
    return {}


#scoring functions for each factor, all return a score between 0 and 1

def distance_score(restaurant, user, context):
    #closer is better
    distance = restaurant.distance_from(context.current_location)
    max_distance = user.max_distance
    
    if distance > max_distance:
        return 0.0

    #score of 1.0 at 0 miles, ~0.37 at half max distance, ~0.14 at max distance
    score = 2.71828 ** (-(distance / max_distance) * 2)
    return score


def price_score(restaurant, user_budget):
    price_diff = abs(restaurant.price_level - user_budget)
    
    if restaurant.price_level > user_budget:
        #over budget - penalize heavily
        return max(0, 1.0 - (price_diff * 0.4))
    elif restaurant.price_level == user_budget:
        #perfect match
        return 1.0
    else:
        #under budget is still good but slightly prefer exact match
        return max(0.6, 1.0 - (price_diff * 0.1))


def dietary_match_score(restaurant, dietary_restrictions):
    if not dietary_restrictions:
        return 1.0  #no restrictions, all restaurants compatible
    
    met_restrictions = 0
    for restriction in dietary_restrictions:
        if restriction in restaurant.dietary_options:
            met_restrictions += 1
    
    return met_restrictions / len(dietary_restrictions)


def time_match_score(restaurant, context):
    #check if open
    if not restaurant.is_open_at(context.current_time):
        return 0.0
    
    base_score = 0.7
    
    if context.meal_type == 'lunch':
        if restaurant.service_style in ['fast_casual', 'casual', 'quick_service']:
            base_score = 1.0
        elif restaurant.service_style == 'fine_dining':
            base_score = 0.4  #normnally don't do fine dining at lunch
    elif context.meal_type == 'dinner':
        #flexible for dinner
        if restaurant.service_style == 'fine_dining':
            base_score = 0.9
        else:
            base_score = 0.85
    
    if context.available_time < 45:
        #penalize slow service
        if restaurant.service_style in ['fine_dining', 'upscale']:
            base_score *= 0.5
    
    return min(1.0, base_score)


def preference_score(restaurant, user_preferences):
    score = 0.5  #neutral score

    if user_preferences.cuisine_preferences:
        cuisine_matches = any(cuisine in user_preferences.cuisine_preferences 
                            for cuisine in restaurant.cuisine_type)
        if cuisine_matches:
            score += 0.3
    
    if restaurant.service_style == user_preferences.dining_style:
        score += 0.2
    
    return min(1.0, score)


def history_score(restaurant, user_history, restaurants_dict, context, current_time, decay_rate=30):
    if len(user_history) < MIN_VISITS_FOR_PATTERN:
        return 0.0
    
    #restaurant-specific score
    restaurant_visits = [v for v in user_history if v.restaurant_id == restaurant.restaurant_id]
    restaurant_weight = get_weighted_visit_count(restaurant_visits, current_time, decay_rate)
    total_weight = get_weighted_visit_count(user_history, current_time, decay_rate)
    restaurant_score = min(1.0, restaurant_weight / max(1, total_weight) * 5)
    
    #cuisine score
    cuisine_dist = get_cuisine_dist(user_history, restaurants_dict, current_time, decay_rate)
    cuisine_score = 0.0
    for cuisine in restaurant.cuisine_type:
        cuisine_score = max(cuisine_score, cuisine_dist.get(cuisine, 0.0))
    
    #service style score
    style_weights = defaultdict(float)
    for visit in user_history:
        weight = calculate_decay_weight(visit.timestamp, current_time, decay_rate)
        rest = restaurants_dict.get(visit.restaurant_id)
        if rest:
            style_weights[rest.service_style] += weight
    
    if total_weight > 0:
        service_style_score = style_weights.get(restaurant.service_style, 0.0) / total_weight
    else:
        service_style_score = 0.0
    
    #contect score
    contextual_weight = 0.0
    contextual_total = 0.0
    
    for visit in user_history:
        if not visit.context:
            continue
        
        weight = calculate_decay_weight(visit.timestamp, current_time, decay_rate)
        same_day = visit.context.get('day_of_week') == context.day_of_week
        same_meal = visit.context.get('meal_type') == context.meal_type
        
        rest = restaurants_dict.get(visit.restaurant_id)
        if rest and same_day and same_meal:
            if any(c in rest.cuisine_type for c in restaurant.cuisine_type):
                contextual_weight += weight
        
        if same_day and same_meal:
            contextual_total += weight
    
    if contextual_total > 0:
        contextual_score = contextual_weight / contextual_total
    else:
        contextual_score = 0.0
    
    #combine
    overall_score = (
        0.35 * restaurant_score +
        0.35 * cuisine_score +
        0.15 * service_style_score +
        0.15 * contextual_score
    )
    
    return overall_score

def adjust_weights(base_weights, context, user, has_history):
    #adjust weights based on context and user characteristics

    weights = base_weights.copy()
    
    #if less time, prioritize distance and time match
    if context.available_time < 60:
        weights['distance'] = 0.40
        weights['time_match'] = 0.25
        weights['price'] = 0.15
        weights['dietary_match'] = 0.10
        weights['preference_score'] = 0.05
        weights['history_score'] = 0.05
    
    #if no dietary restrictions, redistribute that weight
    elif not user.dietary_restrictions:
        extra_weight = weights['dietary_match']
        weights['dietary_match'] = 0.0
        weights['preference_score'] += extra_weight * 0.4
        weights['price'] += extra_weight * 0.3
        weights['history_score'] += extra_weight * 0.3
    
    #if strong dietary restrictions, increase dietary match weight
    elif len(user.dietary_restrictions) >= 2:
        weights['dietary_match'] = 0.30
        total_other = 1.0 - weights['dietary_match']
        for key in weights:
            if key != 'dietary_match':
                weights[key] = (BASE_WEIGHTS[key] / 0.85) * total_other
    
    #if no history, redistribute history weight
    if not has_history:
        extra_weight = weights['history_score']
        weights['history_score'] = 0.0
        weights['preference_score'] += extra_weight * 0.4
        weights['distance'] += extra_weight * 0.3
        weights['price'] += extra_weight * 0.3

    total = sum(weights.values())
    if total > 0:
        weights = {k: v / total for k, v in weights.items()}
    
    return weights

def rank_restaurants(restaurants, user, context, user_history, restaurants_dict, current_time):
    has_history = len(user_history) >= MIN_VISITS_FOR_PATTERN
    
    #adjust weights based on context and user characteristics
    weights = adjust_weights(BASE_WEIGHTS, context, user, has_history)
    
    ranked = []
    
    for restaurant in restaurants:
        #calc individual scores
        dist_score = distance_score(restaurant, user, context)
        pr_score = price_score(restaurant, user.budget_level)
        diet_score = dietary_match_score(restaurant, user.dietary_restrictions)
        time_score = time_match_score(restaurant, context)
        pref_score = preference_score(restaurant, user)
        hist_score = history_score(restaurant, user_history, restaurants_dict, 
                                   context, current_time)
        
        #scores for explanation
        score_breakdown = {
            'distance': dist_score,
            'price': pr_score,
            'dietary_match': diet_score,
            'time_match': time_score,
            'preference_score': pref_score,
            'history_score': hist_score
        }
        
        #weighted overall score
        overall_score = (
            weights['distance'] * dist_score +
            weights['price'] * pr_score +
            weights['dietary_match'] * diet_score +
            weights['time_match'] * time_score +
            weights['preference_score'] * pref_score +
            weights['history_score'] * hist_score
        )
        
        ranked.append((restaurant, overall_score, score_breakdown))

    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked
