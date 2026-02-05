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

weights = {}