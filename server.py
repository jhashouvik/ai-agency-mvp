"""
server.py
──────────
FastAPI side-car — serves REST API endpoints alongside the Streamlit app.

Run with:
    uvicorn server:app --port 8000

This is separate from app.py so that `streamlit run app.py`
does not require fastapi to be installed.
"""

from fastapi import FastAPI
from dashboard.api import router as dashboard_router

app = FastAPI(title="Agency OS API")
app.include_router(dashboard_router)
