"""
ui/sidebar.py
──────────────
Renders the left sidebar with the past-client list.
Sets st.session_state["view_client"] when a client is selected.
"""

import streamlit as st
from database import load_all_clients


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## 📁 Past Clients")
        st.caption("Select a client to view their outputs.")

        clients = load_all_clients()

        if not clients:
            st.info("No clients yet.\nRun your first brief!")
            return

        for row in clients:
            label = f"**{row['business_name']}**\n\n{row['created_at'][:10]}"
            if st.button(label, key=f"sb_{row['id']}", use_container_width=True):
                st.session_state["view_client"] = row["id"]
                # Clear any in-flight session outputs so the saved version loads
                st.session_state.pop("current_outputs", None)
                st.session_state.pop("current_client", None)
