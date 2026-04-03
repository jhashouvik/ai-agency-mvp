"""
database/schema.py
───────────────────
Creates all required tables on first run.
Call init_db() once at app startup.
"""

from .connection import get_connection
from utils.logger import get_logger

log = get_logger(__name__)


def init_db() -> None:
    """Create tables if they do not already exist."""
    log.info("init_db — ensuring schema is up to date")
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS clients (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name   TEXT    NOT NULL,
            created_at      TEXT    NOT NULL,
            input_data      TEXT    NOT NULL,
            outputs         TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS run_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id   INTEGER NOT NULL,
            started_at  TEXT    NOT NULL,
            finished_at TEXT,
            status      TEXT    DEFAULT 'running',
            error       TEXT,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        );
    """)
    conn.commit()
    conn.close()
