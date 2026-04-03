# dashboard/api.py
from fastapi import APIRouter
from database import load_all_clients
from database.connection import get_connection

router = APIRouter(prefix="/dashboard")


@router.get("/clients")
def get_clients():
    """Returns all clients for the Clients table and sidebar badge."""
    clients = load_all_clients()
    # load_all_clients() returns {id, business_name, created_at}
    # We need the full input_data too — so fetch it here
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, business_name, created_at, input_data FROM clients ORDER BY created_at DESC"
    ).fetchall()
    conn.close()

    import json
    result = []
    for row in rows:
        data = json.loads(row["input_data"])
        result.append({
            "id":            row["id"],
            "business_name": row["business_name"],
            "created_at":    row["created_at"],
            "offer":         data.get("offer", ""),
            "audience":      data.get("audience", ""),
            "budget":        data.get("budget", ""),
            "goals":         data.get("goals", ""),
        })
    return result


@router.get("/metrics")
def get_metrics():
    """Returns top-level counts for the metric cards."""
    conn = get_connection()

    total_clients  = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    runs_complete  = conn.execute(
        "SELECT COUNT(*) FROM run_logs WHERE status = 'success'"
    ).fetchone()[0]
    in_progress    = conn.execute(
        "SELECT COUNT(*) FROM run_logs WHERE status = 'running'"
    ).fetchone()[0]

    conn.close()
    return {
        "total_clients": total_clients,
        "runs_complete": runs_complete,
        "in_progress":   in_progress,
    }