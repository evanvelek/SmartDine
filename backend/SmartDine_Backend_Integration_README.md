
# SmartDine Backend – Integration Update

## 1. Datetime crash in ranking engine
Fix: Resolved the error "TypeError: can't subtract offset-naive and offset-aware datetimes" in the ranking history decay calculation.  
Result: Visit history weighting now works correctly and no longer crashes the server.

---

## 2. Restaurant description field
Added: `description` field to the `Restaurant` schema and Yelp normalization layer.  
Result: The UI now receives human-readable descriptions for restaurants.

---

## 3. Dietary options pipeline
Added: `dietary_options` field to the `Restaurant` model and propagated it through the recommendation pipeline.  
Result: The ranker can now receive dietary metadata for restaurants when available.

---

## 4. Yelp dietary keyword extraction
Added: Detection of dietary-related keywords from Yelp categories:

- vegetarian
- vegan
- gluten-free
- pescatarian
- keto
- halal
- kosher

Result: Restaurants are tagged with dietary options the ranker can use.

---

## 5. User dietary preferences handled via profile
Change: Dietary preferences are stored in the user profile (`diet_restrictions`) instead of being inferred by the server.  
Result: Recommendation behavior is now derived from the user profile settings.

---

## 6. Favorites feature implementation

### Added endpoints

POST `/favorites`  
GET `/favorites/{user_id}`

Result: Users can save and retrieve favorite restaurants.

Favorites now store:

- restaurant_id
- name
- address
- rating
- description

---

## 7. Human-readable favorites responses
Improvement: Favorites endpoint now returns restaurant metadata instead of only IDs.

Example response:

{
  "favorites": [
    {
      "restaurant_id": "yelp:cqPZyKKl1iJB_NiKj5m43w",
      "name": "Blue Bowl Superfoods",
      "rating": 4.6,
      "description": "acai bowls • healthy • rated 4.6"
    }
  ]
}

Result: The UI can display favorites directly.

---

## 8. Debug recommendation endpoint

Added endpoint:

POST `/debug/recommend`

Purpose: Allows inspection of the restaurant data sent to the ranker.

---

## 9. Full backend API integration tester

`mock_ui_full.py` now acts as a complete backend test client.

It tests:

- profile creation
- recommendation requests
- ranker debug inspection
- visit logging
- favorites storage
- favorites retrieval
- user deletion
- full system pipeline

---

## 10. Dietary filtering depends on user profile

Example:

"diet_restrictions": "vegetarian"

If the field is empty, dietary scoring is skipped.

