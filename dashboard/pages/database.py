"""
dashboard/pages/database.py
────────────────────────────
Raw database inspector — browse clients and run_logs tables live.
"""

import json
import streamlit as st
from database.connection import get_connection


def _query(sql: str, params: tuple = ()) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def render_database_page() -> None:
    # ── top stats ────────────────────────────────────────────────────
    clients  = _query("SELECT * FROM clients ORDER BY created_at DESC")
    run_logs = _query("SELECT * FROM run_logs ORDER BY id DESC")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Clients",  len(clients))
    c2.metric("Total Run Logs", len(run_logs))
    c3.metric("Successful Runs", sum(1 for r in run_logs if r.get("status") in ("success", "complete")))
    c4.metric("Failed Runs",    sum(1 for r in run_logs if r.get("status") == "error"))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── clients table ────────────────────────────────────────────────
    st.markdown("### 🗂 clients")
    if clients:
        for c in clients:
            # parse input_data for display
            try:
                inp = json.loads(c.get("input_data") or "{}")
            except Exception:
                inp = {}
            try:
                out = json.loads(c.get("outputs") or "{}")
                out_keys = [k for k in out if out[k]]
            except Exception:
                out_keys = []

            with st.expander(f"ID {c['id']} — {c['business_name']}  ·  {c['created_at'][:16]}"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("**Input Data**")
                    for k, v in inp.items():
                        st.markdown(
                            f'<div style="margin-bottom:4px">'
                            f'<span style="color:#7c3aed;font-size:0.78rem;font-weight:700">{k}</span> '
                            f'<span style="color:#e2e2f0;font-size:0.85rem">{v}</span></div>',
                            unsafe_allow_html=True,
                        )
                with col_b:
                    st.markdown("**Outputs stored**")
                    if out_keys:
                        for k in out_keys:
                            st.markdown(
                                f'<span style="background:#022c22;color:#10b981;border:1px solid #14532d;'
                                f'border-radius:6px;padding:3px 10px;font-size:0.75rem;font-weight:600;'
                                f'margin-right:4px;margin-bottom:4px;display:inline-block">{k}</span>',
                                unsafe_allow_html=True,
                            )
                    else:
                        st.caption("No outputs stored")

                st.markdown("**Raw output JSON (first 500 chars)**")
                raw = c.get("outputs") or ""
                st.code(raw[:500] + ("…" if len(raw) > 500 else ""), language="json")
    else:
        st.info("No clients in database.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── run_logs table ───────────────────────────────────────────────
    st.markdown("### 📋 run_logs")
    if run_logs:
        # build a simple HTML table
        rows_html = ""
        for r in run_logs:
            status = r.get("status", "unknown")
            color  = {"success": "#10b981", "complete": "#10b981", "error": "#ef4444",
                      "running": "#3b82f6"}.get(status, "#f59e0b")
            err    = r.get("error") or "—"
            rows_html += (
                f"<tr>"
                f"<td>{r['id']}</td>"
                f"<td>{r['client_id']}</td>"
                f"<td>{(r.get('started_at') or '')[:16]}</td>"
                f"<td>{(r.get('finished_at') or '')[:16]}</td>"
                f'<td><span style="color:{color};font-weight:700">{status}</span></td>'
                f"<td>{err[:60]}</td>"
                f"</tr>"
            )
        th = "border:1px solid #1e1e3a;padding:8px 12px;font-size:0.8rem;"
        td_style = "border:1px solid #1e1e3a;padding:8px 12px;font-size:0.82rem;color:#e2e2f0;"
        st.markdown(
            '<table style="width:100%;border-collapse:collapse;background:#12122a">'
            f'<thead style="background:#0f0f22"><tr>'
            f'<th style="{th}color:#6b7280">id</th>'
            f'<th style="{th}color:#6b7280">client_id</th>'
            f'<th style="{th}color:#6b7280">started_at</th>'
            f'<th style="{th}color:#6b7280">finished_at</th>'
            f'<th style="{th}color:#6b7280">status</th>'
            f'<th style="{th}color:#6b7280">error</th>'
            f"</tr></thead>"
            f'<tbody style="{td_style}">{rows_html}</tbody>'
            "</table>",
            unsafe_allow_html=True,
        )
    else:
        st.info("No run logs yet.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── raw SQL query box ────────────────────────────────────────────
    st.markdown("### 🔍 Custom SQL Query")
    sql = st.text_area(
        "SQL",
        value="SELECT id, business_name, created_at FROM clients",
        height=80,
        label_visibility="collapsed",
    )
    if st.button("▶ Run Query"):
        try:
            results = _query(sql)
            if results:
                st.dataframe(results, use_container_width=True)
            else:
                st.success("Query returned 0 rows.")
        except Exception as e:
            st.error(f"SQL error: {e}")
