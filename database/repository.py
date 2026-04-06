"""
database/repository.py
───────────────────────
All database read/write operations live here.
UI and crew modules never call SQL directly — they use these functions.
"""

import json
from datetime import datetime
from .connection import get_connection
from utils.logger import get_logger

log = get_logger(__name__)


# ── Write ──────────────────────────────────────────────────────────

def save_client(client_data: dict, outputs: dict) -> int:
    """
    Persist a completed client run.
    Returns the new client row id.
    """
    log.info("Saving client to DB — business_name=%r", client_data.get("business_name"))
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO clients (business_name, created_at, input_data, outputs)
        VALUES (?, ?, ?, ?)
        """,
        (
            client_data["business_name"],
            datetime.now().isoformat(timespec="seconds"),
            json.dumps(client_data),
            json.dumps(outputs),
        ),
    )
    client_id = cursor.lastrowid
    conn.commit()
    conn.close()
    log.info("Client saved — id=%d", client_id)
    return client_id


def log_run_start(client_id: int) -> int:
    """Insert a run_log row when a crew job starts. Returns log id."""
    log.debug("log_run_start — client_id=%d", client_id)
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO run_logs (client_id, started_at, status) VALUES (?, ?, 'running')",
        (client_id, datetime.now().isoformat(timespec="seconds")),
    )
    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    log.debug("run_log created — log_id=%d", log_id)
    return log_id


def log_run_finish(log_id: int, status: str = "success", error: str = "") -> None:
    """Update a run_log row when a crew job completes or errors."""
    log.debug("log_run_finish — log_id=%d  status=%s", log_id, status)
    conn = get_connection()
    conn.execute(
        """
        UPDATE run_logs
        SET finished_at = ?, status = ?, error = ?
        WHERE id = ?
        """,
        (datetime.now().isoformat(timespec="seconds"), status, error, log_id),
    )
    conn.commit()
    conn.close()


def log_completed_run(
    client_id: int,
    started_at: str,
    finished_at: str,
    status: str = "success",
    error: str = "",
    tokens_input: int = 0,
    tokens_output: int = 0,
    tokens_total: int = 0,
    cost_usd: float = 0.0,
    duration_secs: int = 0,
) -> None:
    """Insert a fully-timed run_log entry including real token and cost data."""
    log.debug("log_completed_run — client_id=%d  status=%s  tokens=%d  cost=$%.4f",
              client_id, status, tokens_total, cost_usd)
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO run_logs
            (client_id, started_at, finished_at, status, error,
             tokens_input, tokens_output, tokens_total, cost_usd, duration_secs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (client_id, started_at, finished_at, status, error,
         tokens_input, tokens_output, tokens_total, cost_usd, duration_secs),
    )
    conn.commit()
    conn.close()


# ── Read ───────────────────────────────────────────────────────────

def load_all_clients() -> list[dict]:
    """
    Return summary rows for the sidebar client list.
    Each row: {id, business_name, created_at}
    """
    log.debug("load_all_clients called")
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, business_name, created_at FROM clients ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def load_clients_with_status() -> list[dict]:
    """
    Return rich rows for the dashboard Clients table.
    Each row: {id, business_name, offer, audience, budget, goals,
               status, last_run, created_at}
    status is the most-recent run_log status, or 'pending' if never run.
    """
    log.debug("load_clients_with_status called")
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT
            c.id,
            c.business_name,
            c.created_at,
            c.input_data,
            COALESCE(rl.status, 'pending')    AS status,
            rl.started_at                      AS last_run
        FROM clients c
        LEFT JOIN run_logs rl
            ON rl.id = (
                SELECT id FROM run_logs
                WHERE client_id = c.id
                ORDER BY started_at DESC
                LIMIT 1
            )
        ORDER BY c.created_at DESC
        """
    ).fetchall()
    conn.close()

    result = []
    for r in rows:
        d = dict(r)
        try:
            inp = json.loads(d.pop("input_data", "{}"))
        except Exception:
            inp = {}
        d["offer"]    = inp.get("offer", "")
        d["audience"] = inp.get("audience", "")
        d["budget"]   = inp.get("budget", "")
        d["goals"]    = inp.get("goals", "")
        result.append(d)
    return result


def load_token_stats() -> dict:
    """
    Return aggregate token and cost figures across all successful runs.
    Keys: total_tokens, tokens_input, tokens_output, total_cost_usd, avg_duration_secs
    """
    conn = get_connection()
    row = conn.execute(
        """
        SELECT
            COALESCE(SUM(tokens_total),  0)   AS total_tokens,
            COALESCE(SUM(tokens_input),  0)   AS tokens_input,
            COALESCE(SUM(tokens_output), 0)   AS tokens_output,
            COALESCE(SUM(cost_usd),      0.0) AS total_cost_usd,
            COALESCE(AVG(NULLIF(duration_secs, 0)), 0) AS avg_duration_secs
        FROM run_logs
        WHERE status IN ('success', 'complete')
        """
    ).fetchone()
    conn.close()
    return dict(row)


def load_client(client_id: int) -> tuple[dict | None, dict | None]:
    """
    Load a single client's input data and outputs by id.
    Returns (input_dict, outputs_dict) or (None, None) if not found.
    """
    log.debug("load_client — id=%d", client_id)
    conn = get_connection()
    row = conn.execute(
        "SELECT input_data, outputs FROM clients WHERE id = ?",
        (client_id,),
    ).fetchone()
    conn.close()

    if row:
        return json.loads(row["input_data"]), json.loads(row["outputs"])
    return None, None
