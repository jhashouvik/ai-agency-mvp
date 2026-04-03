"""
app.py
───────
Streamlit entry point — Agency OS dashboard.

Run with:
    streamlit run app.py
"""

# onnxruntime / chromadb conflict with streamlit's DLL environment is resolved
# by patching chromadb's CollectionCommon default embedding function to None.
# See: venv/lib/site-packages/chromadb/api/models/CollectionCommon.py

import streamlit as st

from config import settings
from database import init_db
from utils.logger import get_logger
from dashboard import render_dashboard

log = get_logger(__name__)

# ── Page config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Agency OS",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Bootstrap ──────────────────────────────────────────────────────
log.info("App starting — title=%r  model=%r", settings.app_title, settings.openai_model)
init_db()
log.debug("Database initialised")

# ── Render Agency OS dashboard ────────────────────────────────────
render_dashboard()

