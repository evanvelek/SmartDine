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
class User:
    pass


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
    pass


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
    pass

'''
Visit History Model:
-visit_id: int
-user_id: int
-restaurant_id: int
-timestamp: datetime
-context: dict of contextual factors at time of visit (meal type, transportation mode, etc.)
-visit_rating: int (1-5) ***optional, if user rates the visit***
'''