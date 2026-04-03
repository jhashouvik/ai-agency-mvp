"""
dashboard/styles.py
────────────────────
Injects the Agency OS dark-theme CSS once per page load.
Call inject_css() at the top of every dashboard page.
"""

import streamlit as st

# ── palette ────────────────────────────────────────────────────────
BG_PAGE    = "#0a0a18"
BG_SIDEBAR = "#0e0e1c"
BG_CARD    = "#12122a"
BG_TABLE   = "#0f0f22"
BG_ROW_ALT = "#13132a"
BORDER     = "#1e1e3a"
ACCENT     = "#7c3aed"
ACCENT_DIM = "#1e1b4b"

TEXT_PRIMARY = "#e2e2f0"
TEXT_MUTED   = "#6b7280"
TEXT_HEADING = "#ffffff"

STATUS_COLORS = {
    "running":  ("#3b82f6", "#0f172a"),
    "success":  ("#10b981", "#022c22"),
    "complete": ("#10b981", "#022c22"),
    "error":    ("#ef4444", "#2d0a0a"),
    "pending":  ("#f59e0b", "#2d1a00"),
}

CSS = f"""
<style>
/* ── global reset ── */
#MainMenu, header, footer {{ visibility: hidden; }}
.block-container {{ padding: 0 !important; max-width: 100% !important; }}
[data-testid="stAppViewContainer"] {{ background: {BG_PAGE}; }}
[data-testid="stSidebar"] {{
    background: {BG_SIDEBAR} !important;
    border-right: 1px solid {BORDER};
    padding-top: 0 !important;
}}
[data-testid="stSidebar"] .block-container {{ padding: 0 !important; }}

/* ── top header bar ── */
.agency-header {{
    background: {BG_SIDEBAR};
    border-bottom: 1px solid {BORDER};
    padding: 14px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}
.agency-logo {{
    font-size: 1.1rem;
    font-weight: 700;
    color: {TEXT_HEADING};
    letter-spacing: 0.05em;
    display: flex;
    align-items: center;
    gap: 8px;
}}
.agency-logo span.dot {{
    width: 10px; height: 10px;
    border-radius: 50%;
    background: {ACCENT};
    display: inline-block;
}}
.header-right {{
    display: flex; align-items: center; gap: 16px;
}}
.live-badge {{
    background: #0d2d1a;
    color: #10b981;
    border: 1px solid #10b981;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.78rem;
    font-weight: 600;
    display: flex; align-items: center; gap: 6px;
}}
.live-badge::before {{
    content: '';
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #10b981;
    display: inline-block;
}}
.header-clock {{
    font-size: 0.9rem;
    color: {TEXT_MUTED};
    font-family: monospace;
}}

/* ── sidebar nav sections ── */
.nav-section {{
    padding: 18px 16px 4px 16px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: {TEXT_MUTED};
}}
.nav-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 18px;
    margin: 1px 8px;
    border-radius: 8px;
    font-size: 0.9rem;
    color: {TEXT_PRIMARY};
    cursor: pointer;
    transition: background 0.15s;
    border: none;
    background: transparent;
    text-decoration: none;
}}
.nav-item:hover {{ background: {ACCENT_DIM}; }}
.nav-item.active {{
    background: {ACCENT_DIM};
    color: #c4b5fd;
    font-weight: 600;
    border-left: 3px solid {ACCENT};
    padding-left: 15px;
}}
.nav-badge {{
    margin-left: auto;
    background: {ACCENT};
    color: #fff;
    border-radius: 12px;
    padding: 1px 8px;
    font-size: 0.72rem;
    font-weight: 700;
}}

/* ── page content area ── */
.page-header {{
    padding: 28px 32px 20px 32px;
    border-bottom: 1px solid {BORDER};
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
}}
.page-title {{
    font-size: 2rem;
    font-weight: 800;
    color: {TEXT_HEADING};
    margin: 0 0 4px 0;
    font-family: 'Courier New', monospace;
    letter-spacing: -0.02em;
}}
.page-subtitle {{
    color: {TEXT_MUTED};
    font-size: 0.88rem;
    margin: 0;
    font-family: 'Courier New', monospace;
}}
.page-body {{
    padding: 24px 32px;
}}

/* ── search + action bar ── */
.action-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    gap: 16px;
}}
.search-wrap input {{
    background: {BG_CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    color: {TEXT_PRIMARY} !important;
    padding: 8px 14px !important;
}}
.btn-primary {{
    background: {ACCENT};
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 9px 20px;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    white-space: nowrap;
}}
.btn-primary:hover {{ background: #6d28d9; }}

/* ── clients table ── */
.clients-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
}}
.clients-table th {{
    text-align: left;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: {TEXT_MUTED};
    padding: 10px 16px;
    border-bottom: 1px solid {BORDER};
    background: {BG_TABLE};
}}
.clients-table td {{
    padding: 14px 16px;
    border-bottom: 1px solid {BORDER};
    color: {TEXT_PRIMARY};
    vertical-align: middle;
}}
.clients-table tr:hover td {{ background: #13132e; }}
.client-name {{ font-weight: 600; color: {TEXT_HEADING}; margin-bottom: 2px; }}
.client-sub  {{ font-size: 0.8rem; color: {TEXT_MUTED}; font-family: monospace; }}

/* ── status badges ── */
.badge {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.78rem;
    font-weight: 600;
    border: 1px solid transparent;
}}
.badge::before {{
    content: '';
    width: 6px; height: 6px;
    border-radius: 50%;
    background: currentColor;
}}
.badge-running  {{ color: #3b82f6; background: #0f172a; border-color: #1e3a5f; }}
.badge-complete {{ color: #10b981; background: #022c22; border-color: #14532d; }}
.badge-success  {{ color: #10b981; background: #022c22; border-color: #14532d; }}
.badge-error    {{ color: #ef4444; background: #2d0a0a; border-color: #7f1d1d; }}
.badge-pending  {{ color: #f59e0b; background: #2d1a00; border-color: #92400e; }}

/* ── stat cards ── */
.stat-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}}
.stat-card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 20px 22px;
}}
.stat-label {{
    font-size: 0.78rem;
    color: {TEXT_MUTED};
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 8px;
}}
.stat-value {{
    font-size: 1.8rem;
    font-weight: 800;
    color: {TEXT_HEADING};
}}
.stat-delta {{
    font-size: 0.78rem;
    color: #10b981;
    margin-top: 4px;
}}

/* ── streamlit widget overrides ── */
.stTextInput > div > div > input {{
    background: {BG_CARD} !important;
    border: 1px solid {BORDER} !important;
    color: {TEXT_PRIMARY} !important;
    border-radius: 8px !important;
}}
.stButton > button {{
    background: {ACCENT} !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}}
.stButton > button:hover {{ background: #6d28d9 !important; }}
[data-testid="stSidebarNav"] {{ display: none; }}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
