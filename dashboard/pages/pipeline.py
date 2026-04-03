"""
dashboard/pages/pipeline.py
────────────────────────────
Delivery Pipeline — Kanban board with 5 fulfilment stages.
Matches screenshot: BRIEF SUBMITTED | AI RUNNING | OUTPUTS READY | IN DELIVERY | LAUNCHED
"""

import json
import streamlit as st
from database.connection import get_connection


STAGES = [
    ("BRIEF SUBMITTED", "pending",            "#6b7280"),
    ("AI RUNNING",      "running",             "#3b82f6"),
    ("OUTPUTS READY",   "complete|success",    "#10b981"),
    ("IN DELIVERY",     "in_delivery",         "#7c3aed"),
    ("LAUNCHED",        "launched",            "#f59e0b"),
]


def _load_clients_pipeline():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT c.id, c.business_name, c.input_data,
               COALESCE(rl.status, 'pending') AS status,
               rl.started_at
        FROM clients c
        LEFT JOIN run_logs rl ON rl.id = (
            SELECT id FROM run_logs WHERE client_id=c.id
            ORDER BY started_at DESC LIMIT 1
        )
        ORDER BY c.created_at DESC
        """
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        try:
            inp = json.loads(d.get("input_data") or "{}")
        except Exception:
            inp = {}
        d["offer"]    = inp.get("offer", "")
        d["audience"] = inp.get("audience", "")
        d["budget"]   = inp.get("budget", "")
        result.append(d)
    return result


def _status_badge(status: str, color: str) -> str:
    label_map = {
        "pending":    "Pending",
        "running":    f"● {_agents_done(status)}/7 agents",
        "complete":   "7/7",
        "success":    "7/7",
        "in_delivery":"● Live",
        "launched":   "● Live",
        "error":      "Error",
    }
    label = label_map.get(status, status.capitalize())
    return (
        f'<span style="background:{color}18;color:{color};border:1px solid {color}44;'
        f'border-radius:12px;padding:2px 10px;font-size:0.75rem;font-weight:600">'
        f'{label}</span>'
    )


def _agents_done(status: str) -> int:
    if status in ("success", "complete"): return 7
    if status == "running": return 4
    if status == "error": return 3
    return 0


def _agents_badge(status: str, color: str) -> str:
    n = _agents_done(status)
    if n == 0:
        return ""
    return (
        f'<span style="background:{color}18;color:{color};border:1px solid {color}44;'
        f'border-radius:12px;padding:2px 8px;font-size:0.72rem;font-weight:600">'
        f'● {n}/7 agents</span>'
    )


def _in_stage(client_status: str, stage_key: str) -> bool:
    """Map run_log status to pipeline stage."""
    mapping = {
        "pending":    "pending",
        "running":    "running",
        "success":    "complete|success",
        "complete":   "complete|success",
        "in_delivery":"in_delivery",
        "launched":   "launched",
        "error":      "pending",  # show errored clients back in Brief Submitted
    }
    return mapping.get(client_status, "pending") == stage_key


def render_pipeline_page() -> None:
    clients = _load_clients_pipeline()

    if not clients:
        st.info("No clients yet. Submit a brief to start the pipeline.")
        return

    # ── Kanban columns ──────────────────────────────────────────────
    cols = st.columns(5)

    for col, (stage_label, stage_key, color) in zip(cols, STAGES):
        # pick clients in this stage
        if stage_key == "complete|success":
            stage_clients = [c for c in clients if c["status"] in ("complete", "success")]
        elif stage_key == "pending":
            stage_clients = [c for c in clients if c["status"] in ("pending", "error")]
        else:
            stage_clients = [c for c in clients if c["status"] == stage_key]

        count = len(stage_clients)

        with col:
            # column header
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;
                        margin-bottom:12px;padding-bottom:8px;
                        border-bottom:2px solid {color}">
                <span style="font-size:0.72rem;font-weight:700;letter-spacing:0.1em;
                             text-transform:uppercase;color:#6b7280">{stage_label}</span>
                <span style="background:{color}22;color:{color};border-radius:10px;
                             padding:1px 8px;font-size:0.72rem;font-weight:700">{count}</span>
            </div>
            """, unsafe_allow_html=True)

            if not stage_clients:
                st.markdown(
                    f'<div style="color:#4b4b6b;font-size:0.8rem;font-style:italic;padding:8px 0">'
                    f'No clients {stage_label.lower()} yet</div>',
                    unsafe_allow_html=True,
                )
                continue

            for c in stage_clients:
                name    = c["business_name"]
                offer   = (c.get("offer") or "")[:35]
                aud     = (c.get("audience") or "")[:30]
                budget  = c.get("budget") or ""
                status  = c["status"]
                ab = _agents_badge(status, color)

                # Keep everything on one line inside the flex div so that when
                # ab="" there is no blank line to break Streamlit's HTML block.
                card_html = (
                    '<div style="background:#12122a;border:1px solid #1e1e3a;border-radius:10px;'
                    'padding:14px;margin-bottom:10px;">'
                    f'<div style="font-weight:700;font-size:0.88rem;color:#fff;margin-bottom:4px">{name}</div>'
                    f'<div style="color:#6b7280;font-size:0.75rem;margin-bottom:8px;line-height:1.5">{offer}<br>{aud}</div>'
                    '<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:6px">'
                    f'<span style="color:#a78bfa;font-size:0.75rem;font-weight:600">{budget} budget</span>'
                    f'{ab}'
                    '</div>'
                    '</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)


