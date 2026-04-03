"""
dashboard/pages/ghl.py
───────────────────────
GHL Status page — client cards grid with payload status.
Matches screenshot: 3-col grid, fields: Contact/Pipeline stage/Workflow/Funnel pages/Tags
"""

import json
import os
import streamlit as st
from database import load_all_clients, load_client
from database.connection import get_connection


def _run_status(client_id: int) -> str:
    """Return the latest run_log status for a client, or 'pending' if none."""
    conn = get_connection()
    row = conn.execute(
        "SELECT status FROM run_logs WHERE client_id=? ORDER BY started_at DESC LIMIT 1",
        (client_id,),
    ).fetchone()
    conn.close()
    return row["status"] if row else "pending"


def _field_row(label: str, value: str, value_color: str = "#e2e2f0") -> str:
    return (
        f'<div style="display:flex;justify-content:space-between;align-items:center;'
        f'padding:5px 0;border-bottom:1px solid #1e1e3a;">'
        f'<span style="color:#6b7280;font-size:0.78rem">{label}</span>'
        f'<span style="color:{value_color};font-size:0.78rem;font-weight:600">{value}</span>'
        f'</div>'
    )


def render_ghl_page() -> None:
    # ── Mock mode badge ─────────────────────────────────────────────
    api_key_set = bool(os.getenv("GHL_API_KEY", ""))
    if not api_key_set:
        st.markdown(
            '<div style="float:right;background:#2d1a00;color:#f59e0b;border:1px solid #92400e;'
            'border-radius:20px;padding:4px 14px;font-size:0.78rem;font-weight:600;margin-bottom:12px">'
            '● Mock mode — API key not set</div>',
            unsafe_allow_html=True,
        )

    clients = load_all_clients()

    if not clients:
        st.info("No clients yet. Run a brief first to see GHL payloads here.")
        return

    # ── 3-column grid ───────────────────────────────────────────────
    for i in range(0, len(clients), 3):
        row = clients[i:i+3]
        cols = st.columns(3)

        for col, c in zip(cols, row):
            _input, outputs = load_client(c["id"])
            run_status = _run_status(c["id"])

            # ── Determine card status badge ──────────────────────────
            ghl = (outputs or {}).get("_ghl") or {}
            has_outputs = bool(outputs)
            is_running  = run_status == "running"
            is_complete = run_status in ("success", "complete")
            is_error    = run_status == "error"

            if is_running:
                status_label, s_color, s_bg = "Generating...", "#6366f1", "#1e1b4b"
            elif ghl:
                status_label, s_color, s_bg = "Payload ready", "#10b981", "#022c22"
            elif is_complete and has_outputs:
                status_label, s_color, s_bg = "Outputs ready", "#10b981", "#022c22"
            elif is_error:
                status_label, s_color, s_bg = "Run error", "#ef4444", "#2d0a0a"
            elif has_outputs:
                status_label, s_color, s_bg = "Outputs ready", "#10b981", "#022c22"
            else:
                status_label, s_color, s_bg = "Not run", "#6b7280", "#1a1a2e"

            # ── Field values ─────────────────────────────────────────
            if ghl:
                contact_val, contact_color    = "MOCK", "#f59e0b"
                pipeline_val, pipeline_color  = "Strategy Approved", "#e2e2f0"
                workflow_val, workflow_color  = "Onboarding Seq.", "#e2e2f0"
                funnel_val, funnel_color      = "4 pages · draft", "#e2e2f0"
                tags_val, tags_color          = "AI-Generated", "#e2e2f0"
            elif is_complete and has_outputs:
                # Crew ran successfully — extract real data from AI outputs
                funnel_text = (outputs or {}).get("funnel", "")
                auto_text   = (outputs or {}).get("automations", "")
                contact_val, contact_color    = "Ready to push", "#a78bfa"
                pipeline_val, pipeline_color  = "Outputs ready", "#a78bfa"
                workflow_val, workflow_color  = ("Defined" if auto_text else "—"), ("#e2e2f0" if auto_text else "#6b7280")
                funnel_val, funnel_color      = ("Spec ready" if funnel_text else "—"), ("#e2e2f0" if funnel_text else "#6b7280")
                tags_val, tags_color          = "AI-Generated", "#e2e2f0"
            elif is_running:
                contact_val, contact_color    = "Pending", "#f59e0b"
                pipeline_val = workflow_val = funnel_val = tags_val = "—"
                pipeline_color = workflow_color = funnel_color = tags_color = "#6b7280"
            elif is_error:
                contact_val, contact_color    = "Failed", "#ef4444"
                pipeline_val = workflow_val = funnel_val = tags_val = "—"
                pipeline_color = workflow_color = funnel_color = tags_color = "#6b7280"
            else:
                contact_val = pipeline_val = workflow_val = funnel_val = tags_val = "—"
                contact_color = pipeline_color = workflow_color = funnel_color = tags_color = "#6b7280"

            with col:
                card_html = (
                    '<div style="background:#12122a;border:1px solid #1e1e3a;border-radius:12px;padding:18px;margin-bottom:14px">'
                    '<div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:4px">'
                    f'<div><div style="font-weight:700;font-size:0.95rem;color:#fff">{c["business_name"]}</div>'
                    '<div style="color:#6b7280;font-size:0.75rem;margin-top:2px">Contact · Pipeline · Automation</div></div>'
                    f'<span style="background:{s_bg};color:{s_color};border:1px solid {s_color}44;border-radius:12px;'
                    f'padding:3px 10px;font-size:0.72rem;font-weight:600;white-space:nowrap;margin-left:8px">● {status_label}</span>'
                    '</div>'
                    '<div style="margin-top:10px">'
                    + _field_row("Contact", contact_val, contact_color)
                    + _field_row("Pipeline stage", pipeline_val, pipeline_color)
                    + _field_row("Workflow", workflow_val, workflow_color)
                    + _field_row("Funnel pages", funnel_val, funnel_color)
                    + _field_row("Tags", tags_val, tags_color)
                    + '</div></div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)


