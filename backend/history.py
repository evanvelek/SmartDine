'''
record_visit(user_id, restaurant_id, timestamp, visit_rating=None):
    -record a visit to the db

update_visit_rating(visit_id, user_rating):
    -update the rating for a visit in the db

get_user_history(user_id):

get_restaurant_visits(restaurant_id, user_id):
    -all visits to specific restaurant by a user

get_cuisine_pref(user_id, current_time, decay_rate=30):
    -get all user visits
    -group by cuisine type
    -decay to each visit
    -calculate weighted freq distr

get_favorite_restaurants(user_id, current_time, top_n=5):
    -group user visits by restaurant
    -calculate weighted visit count for each restaurant
    -sort & return 
'''
from datetime import datetime
from models import VisitHistory
from collections import defaultdict

#temp storage for visit history, need to replace with actual db calls
visit_storage = {}
visit_counter = 0


def record_visit(user_id, restaurant_id, timestamp, visit_rating=None, context=None):
    global visit_counter
    visit_counter += 1
    
    visit = VisitHistory(
        visit_id=visit_counter,
        user_id=user_id,
        restaurant_id=restaurant_id,
        timestamp=timestamp,
        context=context,
        visit_rating=visit_rating
    )
    
    visit_storage[visit_counter] = visit
    return visit_counter

def update_visit_rating(visit_id, user_rating):
    if visit_id not in visit_storage:
        raise ValueError(f"Visit ID {visit_id} not found")
    
    if not (1 <= user_rating <= 5):
        raise ValueError("Rating must be between 1 and 5")
    
    visit_storage[visit_id].visit_rating = user_rating
    return True

def get_user_history(user_id):
    user_visits = []
    for visit in visit_storage.values():
        if visit.user_id == user_id:
            user_visits.append(visit)
    
    #most recent first
    user_visits.sort(key=lambda v: v.timestamp, reverse=True)
    return user_visits

#all visits to specific restaurant by a user
def get_restaurant_visits(restaurant_id, user_id):
    restaurant_visits = []
    for visit in visit_storage.values():
        if visit.user_id == user_id and visit.restaurant_id == restaurant_id:
            restaurant_visits.append(visit)
    
    #most recent first
    restaurant_visits.sort(key=lambda v: v.timestamp, reverse=True)
    return restaurant_visits

def get_cuisine_pref(user_id, restaurants_dict, current_time, decay_rate=30):
    #weighted cuisine preferences based on user history
    #maps cuisine type -> weighted frequency
    user_visits = get_user_history(user_id)
    
    if not user_visits:
        return {}
    
    #weighted visits per cuisine
    cuisine_weights = defaultdict(float)
    total_weight = 0.0
    
    for visit in user_visits:
        #decay weight
        days_ago = (current_time - visit.timestamp).days
        weight = 0.5 ** (days_ago / decay_rate)
        
        #get cuisines
        restaurant = restaurants_dict.get(visit.restaurant_id)
        if restaurant:
            for cuisine in restaurant.cuisine_type:
                cuisine_weights[cuisine] += weight
                total_weight += weight
    
    # Normalize to get frequency distribution
    if total_weight > 0:
        cuisine_dist = {cuisine: weight / total_weight for cuisine, weight in cuisine_weights.items()}
    else:
        cuisine_dist = {}
    
    return cuisine_dist

def get_favorite_restaurants(user_id, current_time, top_n=5, decay_rate=30):
    #get fav restaurants based on weighted visit frequency
    user_visits = get_user_history(user_id)
    
    if not user_visits:
        return []

    restaurant_weights = defaultdict(float)
    
    for visit in user_visits:
        days_ago = (current_time - visit.timestamp).days
        weight = 0.5 ** (days_ago / decay_rate)
        restaurant_weights[visit.restaurant_id] += weight

    sorted_restaurants = sorted(restaurant_weights.items(), key=lambda x: x[1], reverse=True)
    
    return sorted_restaurants[:top_n]

#like cuisine pref but for service styles
def get_service_style_pref(user_id, restaurants_dict, current_time, decay_rate=30):
    user_visits = get_user_history(user_id)
    
    if not user_visits:
        return {}
    
    style_weights = defaultdict(float)
    total_weight = 0.0
    
    for visit in user_visits:
        days_ago = (current_time - visit.timestamp).days
        weight = 0.5 ** (days_ago / decay_rate)
        
        restaurant = restaurants_dict.get(visit.restaurant_id)
        if restaurant:
            style_weights[restaurant.service_style] += weight
            total_weight += weight

    if total_weight > 0:
        style_dist = {style: weight / total_weight 
                     for style, weight in style_weights.items()}
    else:
        style_dist = {}
    
    return style_dist

#might need to tweak this based on what context we want to capture, but could be useful for filtering before making API calls
def get_contextual_patterns(user_id, restaurants_dict, current_time, decay_rate=30):
    user_visits = get_user_history(user_id)
    
    if not user_visits:
        return {}
    
    #day_of_week, meal_type, cuisine
    pattern_weights = defaultdict(float)
    
    for visit in user_visits:
        if not visit.context:
            continue
        
        days_ago = (current_time - visit.timestamp).days
        weight = 0.5 ** (days_ago / decay_rate)
        
        restaurant = restaurants_dict.get(visit.restaurant_id)
        if restaurant:
            day_of_week = visit.context.get('day_of_week', '')
            meal_type = visit.context.get('meal_type', '')
            
            for cuisine in restaurant.cuisine_type:
                pattern = (day_of_week, meal_type, cuisine)
                pattern_weights[pattern] += weight
    
    return pattern_weights