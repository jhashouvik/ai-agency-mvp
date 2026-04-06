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
    """Create tables if they do not already exist, and migrate schema."""
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
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id      INTEGER NOT NULL,
            started_at     TEXT    NOT NULL,
            finished_at    TEXT,
            status         TEXT    DEFAULT 'running',
            error          TEXT,
            tokens_input   INTEGER DEFAULT 0,
            tokens_output  INTEGER DEFAULT 0,
            tokens_total   INTEGER DEFAULT 0,
            cost_usd       REAL    DEFAULT 0.0,
            duration_secs  INTEGER DEFAULT 0,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        );
    """)

    # ── migrate existing run_logs if new columns are missing ────────
    existing_cols = {
        row[1] for row in conn.execute("PRAGMA table_info(run_logs)").fetchall()
    }
    migrations = [
        ("tokens_input",  "INTEGER DEFAULT 0"),
        ("tokens_output", "INTEGER DEFAULT 0"),
        ("tokens_total",  "INTEGER DEFAULT 0"),
        ("cost_usd",      "REAL DEFAULT 0.0"),
        ("duration_secs", "INTEGER DEFAULT 0"),
    ]
    for col, defn in migrations:
        if col not in existing_cols:
            conn.execute(f"ALTER TABLE run_logs ADD COLUMN {col} {defn}")
            log.info("Migration: added run_logs.%s", col)

    conn.commit()
    conn.close()
