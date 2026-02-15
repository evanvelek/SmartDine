from __future__ import annotations
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

class Context(BaseModel):
    lat: float
    lng: float
    time_available_min: int = Field(ge=1, le=180)
    max_distance_m: int = Field(default=2000, ge=100, le=20000)
    time_of_day: Optional[Literal["breakfast","lunch","dinner","snack"]] = None
    transport_mode: Optional[Literal["walk","drive"]] = "walk"

class RecommendRequest(BaseModel):
    user_id: str
    context: Context

class UserProfile(BaseModel):
    user_id: str
    diet_restrictions: str = ""
    preferred_cuisines: str = ""
    budget_max_price_level: int = 2
    dining_style: str = ""
    max_distance_m: int = 2000

class Restaurant(BaseModel):
    id: str
    source: Literal["yelp","google","mock"]
    name: str
    lat: float
    lng: float
    categories: List[str] = []
    price_level: Optional[int] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    is_open_now: Optional[bool] = None
    address: Optional[str] = None
    distance_m: Optional[float] = None
    eta_min: Optional[int] = None
    raw: Optional[Dict[str, Any]] = None

class Recommendation(Restaurant):
    explanation: str = ""

class RecommendResponse(BaseModel):
    generated_at: str
    recommendations: List[Recommendation]
