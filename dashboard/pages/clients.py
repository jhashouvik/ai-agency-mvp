"""
dashboard/pages/clients.py
───────────────────────────
Clients table page — mirrors the screenshot design.
"""

import textwrap
from datetime import datetime, timezone
import streamlit as st
from database import load_clients_with_status, load_client
from ui.input_form import render_input_form
from ui.output_view import render_output_view


def _relative_time(ts: str | None) -> str:
    if not ts:
        return "Not run"
    try:
        dt = datetime.fromisoformat(ts)
        # make naive dt UTC-aware for comparison
        now = datetime.now()
        diff = now - dt
        days = diff.days
        if days == 0:
            return "Today"
        elif days == 1:
            return "Yesterday"
        elif days < 7:
            return f"{days} days ago"
        else:
            return dt.strftime("%d %b %Y")
    except Exception:
        return ts[:10] if ts else ""


def _badge(status: str) -> str:
    cls = f"badge-{status.lower()}"
    label = status.capitalize()
    return f'<span class="badge {cls}">{label}</span>'


def _truncate(text: str, n: int = 32) -> str:
    return text[:n] + "…" if len(text) > n else text


def render_clients_page() -> None:
    clients = load_clients_with_status()

    # ── search ──────────────────────────────────────────────────────
    col_search, col_btn = st.columns([4, 1])
    with col_search:
        query = st.text_input(
            "search",
            placeholder="Search clients…",
            label_visibility="collapsed",
        )
    with col_btn:
        if st.button("＋ New Client", use_container_width=True):
            st.session_state["page"] = "new_client"
            st.rerun()

    # filter by search
    if query:
        q = query.lower()
        clients = [
            c for c in clients
            if q in c["business_name"].lower()
            or q in c.get("audience", "").lower()
            or q in c.get("goals", "").lower()
        ]

    # ── table ───────────────────────────────────────────────────────
    if not clients:
        st.info("No clients found. Click **＋ New Client** to add one.")
        return

    rows_html = ""
    for c in clients:
        name    = c["business_name"]
        offer   = _truncate(c.get("offer", ""), 38)
        aud     = _truncate(c.get("audience", "—"), 28)
        budget  = c.get("budget", "—")
        goals   = _truncate(c.get("goals", "—"), 30)
        status  = c.get("status", "pending")
        last_run = _relative_time(c.get("last_run") or c.get("created_at"))
        badge   = _badge(status)
        client_id = c["id"]

        rows_html += (
            "<tr>"
            "<td>"
            f'<div class="client-name">{name}</div>'
            f'<div class="client-sub">{offer}</div>'
            "</td>"
            f"<td>{aud}</td>"
            f"<td>{budget}</td>"
            f"<td>{goals}</td>"
            f"<td>{badge}</td>"
            f'<td style="color:#6b7280">{last_run}</td>'
            "</tr>"
        )

    table_html = (
        '<table class="clients-table">'
        "<thead><tr>"
        "<th>Client</th><th>Audience</th><th>Budget</th>"
        "<th>Goals</th><th>Status</th><th>Last Run</th>"
        "</tr></thead>"
        f"<tbody>{rows_html}</tbody>"
        "</table>"
    )
    st.markdown(table_html, unsafe_allow_html=True)

    # ── click to view client ────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    if clients:
        st.caption("Select a client to view their full output:")
        options = {f"{c['business_name']} ({c['created_at'][:10]})": c["id"] for c in clients}
        chosen_label = st.selectbox(
            "Open client",
            list(options.keys()),
            label_visibility="collapsed",
        )
        if st.button("📄 View Output", use_container_width=False):
            st.session_state["view_client"] = options[chosen_label]
            st.session_state["page"] = "outputs"
            st.rerun()
