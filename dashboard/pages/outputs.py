"""
dashboard/pages/outputs.py
───────────────────────────
Output Tracker — per-client output completion status.
Matches screenshot: shows 7 output tags per client, coloured by completion.
"""

import json
import streamlit as st
from database import load_clients_with_status, load_client
from database.connection import get_connection
from datetime import datetime


OUTPUT_KEYS = [
    ("strategy",     "Strategy"),
    ("copy",         "Copy"),
    ("media_plan",   "Media Plan"),
    ("funnel",       "Funnel"),
    ("automations",  "Automations"),
    ("creatives",    "Creatives"),
    ("project_plan", "PM Plan"),
]


def _relative(ts: str | None) -> str:
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts)
        diff = (datetime.now() - dt).days
        if diff == 0: return "today"
        if diff == 1: return "yesterday"
        return f"{diff} days ago"
    except Exception:
        return ts[:10]


def _fmt_secs(started: str | None, finished: str | None) -> str:
    try:
        s = datetime.fromisoformat(started)
        f = datetime.fromisoformat(finished)
        secs = int((f - s).total_seconds())
        m, s2 = divmod(secs, 60)
        return f"{m}m {s2:02d}s"
    except Exception:
        return ""


def _load_clients_with_outputs():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT c.id, c.business_name, c.created_at, c.outputs,
               rl.status, rl.started_at, rl.finished_at, rl.error
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
            d["_outputs"] = json.loads(d.get("outputs") or "{}")
        except Exception:
            d["_outputs"] = {}
        result.append(d)
    return result


def render_outputs_page() -> None:
    clients = _load_clients_with_outputs()

    if not clients:
        st.info("No outputs yet. Go to **Clients** and run a brief first.")
        return

    for c in clients:
        status   = c.get("status") or "pending"
        outputs  = c.get("_outputs", {})
        dur      = _fmt_secs(c.get("started_at"), c.get("finished_at"))
        rel      = _relative(c.get("started_at") or c.get("created_at"))

        # subtitle line under client name
        if status in ("success", "complete"):
            subtitle = f"Completed {rel}" + (f" · {dur}" if dur else "")
            sub_color = "#6b7280"
        elif status == "running":
            subtitle = f"Run started {rel} · in progress"
            sub_color = "#6b7280"
        elif status == "error":
            err = c.get("error") or "unknown error"
            stopped_at = "Automation Builder"  # default
            subtitle = f"Failed {rel} · stopped at {stopped_at}"
            sub_color = "#ef4444"
        else:
            subtitle = "Not yet run · brief submitted"
            sub_color = "#6b7280"

        # output chips
        completed_count = 0
        chips_html = ""
        for key, label in OUTPUT_KEYS:
            done = key in outputs and bool(outputs[key])
            if done:
                completed_count += 1
                chips_html += (
                    f'<span style="background:#022c22;color:#10b981;border:1px solid #14532d;'
                    f'border-radius:6px;padding:4px 10px;font-size:0.75rem;font-weight:600;'
                    f'margin-right:6px">{label}</span>'
                )
            else:
                chips_html += (
                    f'<span style="background:#141428;color:#4b4b6b;border:1px solid #1e1e3a;'
                    f'border-radius:6px;padding:4px 10px;font-size:0.75rem;font-weight:600;'
                    f'margin-right:6px">{label}</span>'
                )

        # completion badge colour
        if completed_count == 7:
            badge_color, badge_bg = "#10b981", "#022c22"
        elif status == "error":
            badge_color, badge_bg = "#ef4444", "#2d0a0a"
        elif status == "running":
            badge_color, badge_bg = "#3b82f6", "#0f172a"
        else:
            badge_color, badge_bg = "#f59e0b", "#2d1a00"

        st.markdown(f"""
        <div style="background:#12122a;border:1px solid #1e1e3a;border-radius:12px;
                    padding:18px 22px;margin-bottom:10px;
                    display:flex;align-items:center;justify-content:space-between;gap:12px">
            <div style="min-width:200px">
                <div style="font-weight:700;font-size:0.95rem;color:#fff;margin-bottom:3px">
                    {c['business_name']}
                </div>
                <div style="color:{sub_color};font-size:0.78rem">{subtitle}</div>
            </div>
            <div style="flex:1;display:flex;flex-wrap:wrap;gap:4px">
                {chips_html}
            </div>
            <div style="background:{badge_bg};color:{badge_color};border:1px solid {badge_color}44;
                        border-radius:20px;padding:4px 14px;font-size:0.82rem;font-weight:700;
                        white-space:nowrap;flex-shrink:0">
                ● {completed_count} / 7
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── detail viewer ───────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="color:#6b7280;font-size:0.82rem;margin-bottom:8px">Click to view full output for a client:</div>',
        unsafe_allow_html=True,
    )
    options = {c["business_name"]: c["id"] for c in clients}
    chosen = st.selectbox("Select client", list(options.keys()), label_visibility="collapsed")
    if st.button("📄 Open Full Output", use_container_width=False):
        st.session_state["view_client"] = options[chosen]
        st.session_state["page"] = "output_detail"
        st.rerun()

