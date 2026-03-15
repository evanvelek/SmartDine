import json
from datetime import datetime, timezone
from typing import Optional
from db import get_conn
from schemas import UserProfile

def get_user_profile(user_id: str) -> Optional[UserProfile]:
    with get_conn() as con:
        cur = con.cursor()
        cur.execute(
            """
            SELECT user_id, diet_restrictions, preferred_cuisines,
                   budget_max_price_level, dining_style, max_distance_m
            FROM user_profiles
            WHERE user_id = ?
            """,
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
            INSERT INTO user_profiles (
                user_id, diet_restrictions, preferred_cuisines,
                budget_max_price_level, dining_style, max_distance_m
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                diet_restrictions = excluded.diet_restrictions,
                preferred_cuisines = excluded.preferred_cuisines,
                budget_max_price_level = excluded.budget_max_price_level,
                dining_style = excluded.dining_style,
                max_distance_m = excluded.max_distance_m
            """,
            (
                p.user_id,
                p.diet_restrictions,
                p.preferred_cuisines,
                p.budget_max_price_level,
                p.dining_style,
                p.max_distance_m
            )
        )
        con.commit()


def log_visit(v) -> None:
    with get_conn() as con:
        con.execute(
            """
            INSERT INTO visit_history (
                user_id, restaurant_id, timestamp, visit_rating, context_json
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                v.user_id,
                v.restaurant_id,
                v.timestamp,
                v.visit_rating,
                json.dumps(v.context)
            )
        )
        con.commit()


def get_user_history(user_id: str):
    with get_conn() as con:
        rows = con.execute(
            """
            SELECT visit_id, user_id, restaurant_id, timestamp, visit_rating, context_json
            FROM visit_history
            WHERE user_id = ?
            ORDER BY timestamp ASC
            """,
            (user_id,)
        ).fetchall()

    return rows


def delete_user_profile(user_id: str) -> bool:
    with get_conn() as con:
        cur = con.cursor()

        cur.execute(
            """
            DELETE FROM favorites
            WHERE user_id = ?
            """,
            (user_id,)
        )

        cur.execute(
            """
            DELETE FROM visit_history
            WHERE user_id = ?
            """,
            (user_id,)
        )

        cur.execute(
            """
            DELETE FROM user_history
            WHERE user_id = ?
            """,
            (user_id,)
        )

        cur.execute(
            """
            DELETE FROM user_profiles
            WHERE user_id = ?
            """,
            (user_id,)
        )

        deleted_profile = cur.rowcount > 0
        con.commit()
        return deleted_profile


def add_favorite(
    user_id: str,
    restaurant_id: str,
    name: str,
    address: str | None = None,
    rating: float | None = None,
    description: str | None = None,
) -> None:
    with get_conn() as con:
        con.execute(
            """
            INSERT INTO favorites (
                user_id, restaurant_id, created_at, name, address, rating, description
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, restaurant_id) DO UPDATE SET
                created_at = excluded.created_at,
                name = excluded.name,
                address = excluded.address,
                rating = excluded.rating,
                description = excluded.description
            """,
            (
                user_id,
                restaurant_id,
                datetime.now(timezone.utc).isoformat(),
                name,
                address,
                rating,
                description,
            )
        )
        con.commit()


def get_user_favorites(user_id: str):
    with get_conn() as con:
        rows = con.execute(
            """
            SELECT restaurant_id, name, address, rating, description
            FROM favorites
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,)
        ).fetchall()

    return [
        {
            "id": row[0],
            "name": row[1],
            "address": row[2],
            "rating": row[3],
            "description": row[4],
        }
        for row in rows
    ]
