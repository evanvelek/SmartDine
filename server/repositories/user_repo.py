from typing import Optional
from db import get_conn
from schemas import UserProfile

def get_user_profile(user_id: str) -> Optional[UserProfile]:
    with get_conn() as con:
        cur = con.cursor()
        cur.execute(
            "SELECT user_id, diet_restrictions, preferred_cuisines, budget_max_price_level, dining_style, max_distance_m FROM user_profiles WHERE user_id=?",
            (user_id,)
        )
        row = cur.fetchone()
        if not row:
            return None
        return UserProfile(
            user_id=row[0],
            diet_restrictions=row[1] or "",
            preferred_cuisines=row[2] or "",
            budget_max_price_level=int(row[3]) if row[3] is not None else 2,
            dining_style=row[4] or "",
            max_distance_m=int(row[5]) if row[5] is not None else 2000
        )

def upsert_user_profile(p: UserProfile) -> None:
    with get_conn() as con:
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO user_profiles (user_id, diet_restrictions, preferred_cuisines, budget_max_price_level, dining_style, max_distance_m)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
              diet_restrictions=excluded.diet_restrictions,
              preferred_cuisines=excluded.preferred_cuisines,
              budget_max_price_level=excluded.budget_max_price_level,
              dining_style=excluded.dining_style,
              max_distance_m=excluded.max_distance_m
            """,
            (p.user_id, p.diet_restrictions, p.preferred_cuisines, p.budget_max_price_level, p.dining_style, p.max_distance_m)
        )
        con.commit()
