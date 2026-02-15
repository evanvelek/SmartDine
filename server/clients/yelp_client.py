import os
from typing import Any, Dict, List, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()
YELP_API_KEY = os.getenv("YELP_API_KEY", "")

class YelpClient:
    BASE = "https://api.yelp.com/v3"

    def __init__(self, api_key: Optional[str] = None, timeout_s: float = 10.0):
        self.api_key = api_key or YELP_API_KEY
        self.timeout_s = timeout_s

    async def search(self, lat: float, lng: float, radius_m: int, limit: int = 20,
                     price: Optional[str] = None, open_now: bool = True) -> List[Dict[str, Any]]:
        if not self.api_key:
            return []
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {
            "latitude": lat,
            "longitude": lng,
            "categories": "restaurants",
            "sort_by": "distance",
            "radius": min(radius_m, 40000),
            "limit": min(max(limit, 1), 50),
        }
        if price:
            params["price"] = price
        if open_now:
            params["open_now"] = True
        url = f"{self.BASE}/businesses/search"
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            r = await client.get(url, headers=headers, params=params)
            r.raise_for_status()
            data = r.json()
            return data.get("businesses", [])
