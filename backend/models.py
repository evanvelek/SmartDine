'''
User Model:
-user_id: int
-dietary_restrictions: list (vegan, gluten-free, etc.)
-cuisine_preferences: list (Italian, Mexican, etc.)
-budget_level: int (1-5) or however it is represented in the chosen API
-dining_style: str (casual, fine dining, etc.)
-max_distance: int (in miles or kilometers)
-preferred_meal_times: dict (breakfast, lunch, dinner each w a time range)

-check if restaurant matches dietary needs
-price fits budget
-overall preference score?
'''
from datetime import datetime, time
import math


class User:
    def __init__(self, user_id, dietary_restrictions=None, cuisine_preferences=None, budget_level=2, dining_style="casual", max_distance=5.0, preferred_meal_times=None):
        self.user_id = user_id
        self.dietary_restrictions = dietary_restrictions if dietary_restrictions else []
        self.cuisine_preferences = cuisine_preferences if cuisine_preferences else []
        self.budget_level = budget_level  #1-5 scale
        self.dining_style = dining_style
        self.max_distance = max_distance  #in miles (allow user to specify in miles or km, but convert to miles for consistency??)
        
        #default meal times if not provided
        if preferred_meal_times is None:
            self.preferred_meal_times = {
                'breakfast': {'start': time(7, 0), 'end': time(11, 0)},
                'lunch': {'start': time(11, 0), 'end': time(15, 0)},
                'dinner': {'start': time(17, 0), 'end': time(22, 0)}
            }
        else:
            self.preferred_meal_times = preferred_meal_times
    
    def check_dietary_compatibility(self, restaurant):
        if not self.dietary_restrictions:
            return True
        
        for restriction in self.dietary_restrictions:
            if restriction not in restaurant.dietary_options:
                return False
        return True
    
    def check_price_fit(self, restaurant):
        #allow restaurants <= budget level
        return restaurant.price_level <= self.budget_level



'''
Restaurant Model:
-restaurant_id: int
-name: str
-cuisine_type: list of str
-price_level: int (1-5)
-location: dict (latitude, longitude)
-hours: dict (day: {open_time, close_time})
-rating: float (1-5)
-dietary_options: list of str (vegan, gluten-free, etc.)
-service_style: str (casual, fine dining, etc.)

-check if open at certain time
-distance from user
-meets all filter criteria
'''
class Restaurant:
    def __init__(self, restaurant_id, name, cuisine_type, price_level, location, hours, rating=0.0, dietary_options=None, service_style=None):
        self.restaurant_id = restaurant_id
        self.name = name
        self.cuisine_type = cuisine_type if isinstance(cuisine_type, list) else [cuisine_type]
        self.price_level = price_level  # 1-5 scale
        self.location = location
        self.hours = hours
        self.rating = rating
        self.dietary_options = dietary_options if dietary_options else []
        self.service_style = service_style
    
    #check if restaurant is open at a certain time
    def is_open_at(self, check_time):
        day_of_week = check_time.strftime('%A') #convert to day of week string
        
        if day_of_week not in self.hours:
            return False
        
        hours_today = self.hours[day_of_week]
        if hours_today is None:  #closed all day
            return False
        
        current_time = check_time.time()
        open_time = hours_today['open']
        close_time = hours_today['close']
        
        #for restaurants that close after midnight
        if close_time < open_time:
            return current_time >= open_time or current_time <= close_time
        else:
            return open_time <= current_time <= close_time

    #might not need this based on the api's distance calculation, but could be useful for filtering before making API calls
    def distance_from(self, location):
        #haversine formula to calculate distance between two lat/lon points on a sphere
        lat1 = math.radians(self.location['latitude'])
        lon1 = math.radians(self.location['longitude'])
        lat2 = math.radians(location['latitude'])
        lon2 = math.radians(location['longitude'])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))

        distance = 3959 * c
        
        return distance
    
    def meets_filter_criteria(self, user, context):
        if not user.check_dietary_compatibility(self):
            return False

        if not user.check_price_fit(self):
            return False

        distance = self.distance_from(context.current_location)
        if distance > user.max_distance:
            return False

        if not self.is_open_at(context.current_time):
            return False
        
        return True

'''
Context Model:
-current_time: datetime
-current_location: dict (latitude, longitude)
-available_time: int (how much time user has for dining)
-day_of_week: str (Monday, Tuesday, etc.)
-meal_type: str (inferred from time)
-transportation_mode: str (walking, driving, public transit)

-find max distance based on transportation mode and available time
'''
class Context:
    TRANSPORT_SPEEDS = {
        'walking': 3.0,
        'driving': 30.0,
        'public_transit': 15.0,
        'biking': 12.0
    }

    #not sure if we should default to driving or require user to specify?
    def __init__(self, current_time, current_location, available_time=60, transportation_mode='driving'):
        self.current_time = current_time
        self.current_location = current_location
        self.available_time = available_time  #in minutes
        self.day_of_week = current_time.strftime('%A')
        self.meal_type = self._infer_meal_type()
        self.transportation_mode = transportation_mode

    def _infer_meal_type(self):
        current_hour = self.current_time.hour
        if 7 <= current_hour < 11:
            return 'breakfast'
        elif 11 <= current_hour < 15:
            return 'lunch'
        elif 17 <= current_hour < 22:
            return 'dinner'
        else:
            return 'late_night'
    
    #calculate max distance based on transportation mode and available time
    def get_max_distance(self):
        speed = self.TRANSPORT_SPEEDS.get(self.transportation_mode, 3.0)
        travel_time = max(0, self.available_time - 40)
        max_distance = (speed * travel_time / 60) / 2
        return max_distance
'''
Visit History Model:
-visit_id: int
-user_id: int
-restaurant_id: int
-timestamp: datetime
-context: dict of contextual factors at time of visit (meal type, transportation mode, etc.)
-visit_rating: int (1-5) ***optional, if user rates the visit***
'''
class VisitHistory:
    def __init__(self, visit_id, user_id, restaurant_id, timestamp, context=None, visit_rating=None):
        self.visit_id = visit_id
        self.user_id = user_id
        self.restaurant_id = restaurant_id
        self.timestamp = timestamp
        self.context = context if context else {}
        self.visit_rating = visit_rating  #optional

    def set_rating(self, rating):
        if 1 <= rating <= 5:
            self.visit_rating = rating
        else:
            raise ValueError("Rating must be between 1 and 5")