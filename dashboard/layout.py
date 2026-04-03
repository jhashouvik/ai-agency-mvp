"""
dashboard/layout.py
────────────────────
Main orchestrator: renders Agency OS header, sidebar nav,
and routes to the correct page based on session state.
"""

import datetime
import streamlit as st

from .styles import inject_css
from .pages import (
    render_home_page,
    render_clients_page,
    render_agents_page,
    render_outputs_page,
    render_pipeline_page,
    render_ghl_page,
    render_database_page,
)
from database import load_all_clients
from ui.input_form import render_input_form
from ui.output_view import render_output_view

# ── page registry ──────────────────────────────────────────────────
PAGES = {
    "dashboard":     ("Dashboard",        "○",  render_home_page),
    "clients":       ("Clients",          "◇",  render_clients_page),
    "agents":        ("Agents",           "●",  render_agents_page),
    "outputs":       ("Outputs",          "□",  render_outputs_page),
    "pipeline":      ("Pipeline",         "▷",  render_pipeline_page),
    "ghl":           ("GHL Status",       "○",  render_ghl_page),
    "new_client":    ("New Client",       "＋", render_input_form),
    "output_detail": ("Output Detail",    "□",  render_output_view),
    "database":      ("Database",          "⬡",  render_database_page),
}

PAGE_ORDER = [
    ("OVERVIEW",  ["dashboard", "clients"]),
    ("AI SYSTEM", ["agents", "outputs"]),
    ("DELIVERY",  ["pipeline", "ghl"]),
    ("ADMIN",     ["database"]),
]

PAGE_META = {
    "dashboard":     ("Agency Dashboard",  "Central ops view — all clients, agents & delivery status"),
    "clients":       ("Clients",           "All client briefs and run history"),
    "agents":        ("AI Agents",         "Performance and run stats per agent role"),
    "outputs":       ("Output Tracker",    "Per-client agent output completion status"),
    "pipeline":      ("Delivery Pipeline", "Client progression through fulfilment stages"),
    "ghl":           ("GHL Status",        "Mock GHL payload status per client — ready for live API connection"),
    "new_client":    ("New Client Brief",  "Submit a new client brief to the AI system"),
    "output_detail": ("Output Detail",     "Full agent outputs for selected client"),
    "database":      ("Database",            "Browse raw database tables and run custom SQL"),
}


def render_sidebar_nav() -> None:
    current = st.session_state.get("page", "dashboard")

    # Logo
    st.sidebar.markdown(
        '<div style="padding:20px 18px 8px 18px;font-size:1.05rem;font-weight:800;'
        'color:#fff;letter-spacing:0.06em;display:flex;align-items:center;gap:8px;">'
        '<span style="width:10px;height:10px;border-radius:50%;background:#7c3aed;'
        'display:inline-block"></span> AGENCY OS</div>',
        unsafe_allow_html=True,
    )

    try:
        client_count = str(len(load_all_clients()))
    except Exception:
        client_count = ""

    for section_label, keys in PAGE_ORDER:
        st.sidebar.markdown(
            f'<div class="nav-section">{section_label}</div>',
            unsafe_allow_html=True,
        )
        for key in keys:
            label, icon, _ = PAGES[key]
            badge = client_count if key == "clients" else ""
            is_active = current == key or (current == "output_detail" and key == "outputs")
            prefix = "◆" if is_active else icon
            btn_label = f"{prefix}  {label}" + (f"  [{badge}]" if badge else "")
            if st.sidebar.button(btn_label, key=f"nav_{key}", use_container_width=True):
                if key == "outputs":
                    st.session_state.pop("view_client", None)
                st.session_state["page"] = key
                st.rerun()


def render_header() -> None:
    clock = datetime.datetime.now().strftime("%H:%M:%S")
    st.markdown(f"""
    <div class="agency-header">
        <div class="agency-logo">
            <span class="dot"></span> AGENCY OS
        </div>
        <div class="header-right">
            <span class="live-badge">System live</span>
            <span class="header-clock">{clock}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str = "", right_widget: str = "") -> None:
    right_html = (
        f'<div style="flex-shrink:0">{right_widget}</div>' if right_widget else ""
    )
    st.markdown(f"""
    <div class="page-header">
        <div>
            <div class="page-title">{title}</div>
            {'<div class="page-subtitle">' + subtitle + '</div>' if subtitle else ''}
        </div>
        {right_html}
    </div>
    """, unsafe_allow_html=True)


def render_dashboard() -> None:
    inject_css()

    if "page" not in st.session_state:
        st.session_state["page"] = "dashboard"

    render_sidebar_nav()

    page_key = st.session_state.get("page", "dashboard")
    title, subtitle = PAGE_META.get(page_key, (page_key.capitalize(), ""))
    _, icon, render_fn = PAGES.get(page_key, PAGES["dashboard"])

    render_header()
    render_page_header(title, subtitle)

    st.markdown('<div class="page-body">', unsafe_allow_html=True)
    render_fn()
    st.markdown('</div>', unsafe_allow_html=True)

