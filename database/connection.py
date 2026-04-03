"""
database/connection.py
───────────────────────
Provides a single function that returns a SQLite connection.
All repository functions call get_connection() — swap to
Postgres/Supabase here without touching any other module.
"""

import sqlite3
from config import settings


def get_connection() -> sqlite3.Connection:
    """Return a configured SQLite connection."""
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row   # Rows accessible by column name
    return conn
