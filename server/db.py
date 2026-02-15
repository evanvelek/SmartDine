import os
import sqlite3
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "./smartdine.sqlite3")

def init_db() -> None:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_profiles (
        user_id TEXT PRIMARY KEY,
        diet_restrictions TEXT,
        preferred_cuisines TEXT,
        budget_max_price_level INTEGER,
        dining_style TEXT,
        max_distance_m INTEGER
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        place_id TEXT NOT NULL,
        source TEXT NOT NULL,
        selected_at TEXT NOT NULL
    );
    """)
    con.commit()
    con.close()

@contextmanager
def get_conn():
    con = sqlite3.connect(DB_PATH)
    try:
        yield con
    finally:
        con.close()
