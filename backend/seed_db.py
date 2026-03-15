from db import init_db
from repositories.user_repo import upsert_user_profile
from schemas import UserProfile

def main():
    init_db()
    upsert_user_profile(UserProfile(
        user_id="demo_user_001",
        diet_restrictions="",
        preferred_cuisines="mexican, japanese, sandwiches",
        budget_max_price_level=2,
        dining_style="fast, takeout",
        max_distance_m=2000
    ))
    print("Seeded demo_user_001 into user_profiles.")

if __name__ == "__main__":
    main()
