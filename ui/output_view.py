"""
ui/output_view.py
──────────────────
Renders the "View Output" tab.
Loads client data from session state or database,
displays metric cards, per-agent tabs, mock GHL payload,
and a JSON download button.
"""

import json
import streamlit as st

from database import load_client
from ghl import render_ghl_json


# Maps output dict keys → display labels
AGENT_TABS: list[tuple[str, str]] = [
    ("strategy",     "🧠 Strategy"),
    ("copy",         "✍️ Copy"),
    ("media_plan",   "📣 Media Plan"),
    ("funnel",       "🏗️ Funnel Spec"),
    ("automations",  "⚙️ Automations"),
    ("creatives",    "🎨 Creatives"),
    ("project_plan", "📋 Project Plan"),
    ("_ghl",         "🔌 Mock GHL"),
]


def render_output_view() -> None:
    client_data, outputs = _resolve_data()

    if not outputs or not client_data:
        st.info(
            "Run a client brief from the **New Client Brief** tab, "
            "or select a past client from the sidebar."
        )
        return

    _render_header(client_data)
    _render_metric_cards(client_data)
    st.divider()
    _render_agent_tabs(client_data, outputs)
    st.divider()
    _render_download(client_data, outputs)


# ── Private helpers ────────────────────────────────────────────────

def _resolve_data() -> tuple[dict | None, dict | None]:
    """
    Priority:
    1. Freshly run outputs in session state
    2. Client selected from sidebar (load from DB)
    """
    if "current_outputs" in st.session_state:
        return (
            st.session_state.get("current_client"),
            st.session_state.get("current_outputs"),
        )
    if "view_client" in st.session_state:
        return load_client(st.session_state["view_client"])
    return None, None


def _render_header(client_data: dict) -> None:
    st.subheader(f"📊 {client_data['business_name']} — Full Output")


def _render_metric_cards(client_data: dict) -> None:
    cols = st.columns(4)
    cols[0].metric("Business",   client_data["business_name"])
    cols[1].metric("Budget",     client_data["budget"])
    cols[2].metric("Agents Run", "7 / 7")
    cols[3].metric("Status",     "✅ Complete")


def _render_agent_tabs(client_data: dict, outputs: dict) -> None:
    tab_labels = [label for _, label in AGENT_TABS]
    tabs = st.tabs(tab_labels)

    for tab_ui, (key, label) in zip(tabs, AGENT_TABS):
        with tab_ui:
            if key == "_ghl":
                st.markdown("### Mock GHL Payload")
                st.caption(
                    "This mirrors the real GHL API request bodies. "
                    "In production, swap `push_to_ghl()` in `ghl/formatter.py` "
                    "with live REST calls."
                )
                st.code(render_ghl_json(client_data, outputs), language="json")
            else:
                friendly = label.split(" ", 1)[-1]   # strip the emoji
                st.markdown(f"### {friendly}")
                content = outputs.get(key, "")
                if content:
                    st.markdown(content)
                else:
                    st.warning("No output recorded for this agent.")


def _render_download(client_data: dict, outputs: dict) -> None:
    payload = json.dumps(
        {"client": client_data, "outputs": outputs},
        indent=2,
        ensure_ascii=False,
    )
    filename = client_data["business_name"].replace(" ", "_") + "_outputs.json"
    st.download_button(
        label="⬇️ Download All Outputs (JSON)",
        data=payload,
        file_name=filename,
        mime="application/json",
        use_container_width=True,
    )
