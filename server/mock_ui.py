import json
import requests

URL = "http://127.0.0.1:8000/recommend"

payload = {
  "user_id": "demo_user_001",
  "context": {
    #"lat": 33.6405,
    #"lng": -117.8443,
    "lat": 32.963519,
    "lng": -117.202938,
    "time_available_min": 30,
    "max_distance_m": 2000,
    "transport_mode": "walk"
  }
}

def main():
    r = requests.post(URL, json=payload, timeout=15)
    r.raise_for_status()
    print(json.dumps(r.json(), indent=2))

if __name__ == "__main__":
    main()
