from typing import List
from schemas import Restaurant

def mock_restaurants(lat: float, lng: float) -> List[Restaurant]:
    return [
        Restaurant(id="mock:1", source="mock", name="Campus Cafe", lat=lat+0.001, lng=lng-0.0005, categories=["cafe","sandwiches"], price_level=1, rating=4.2, reviews_count=210, is_open_now=True, address="On Campus"),
        Restaurant(id="mock:2", source="mock", name="Quick Bowl", lat=lat-0.0008, lng=lng+0.0012, categories=["asian","bowls"], price_level=2, rating=4.6, reviews_count=540, is_open_now=True, address="Near Campus"),
        Restaurant(id="mock:3", source="mock", name="Taco Spot", lat=lat+0.0015, lng=lng+0.0009, categories=["mexican"], price_level=1, rating=4.5, reviews_count=900, is_open_now=True, address="Campus Plaza"),
        Restaurant(id="mock:4", source="mock", name="Sit-Down Bistro", lat=lat+0.004, lng=lng-0.003, categories=["american","dinner"], price_level=3, rating=4.4, reviews_count=1200, is_open_now=True, address="Downtown"),
    ]
