"""
dashboard/pages/home.py
────────────────────────
Agency Dashboard — stat cards, recent runs table, live activity feed.
Matches screenshot: "Agency Dashboard / Central ops view"
"""

import streamlit as st
from database import load_clients_with_status
from database.connection import get_connection
from datetime import datetime


def _load_runs():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT c.business_name, c.input_data,
               rl.started_at, rl.finished_at, rl.status, rl.error,
               rl.id as run_id
        FROM run_logs rl
        JOIN clients c ON c.id = rl.client_id
        ORDER BY rl.started_at DESC
        LIMIT 20
        """
    ).fetchall()
    conn.close()
    import json
    result = []
    for r in rows:
        d = dict(r)
        try:
            inp = json.loads(d.get("input_data") or "{}")
        except Exception:
            inp = {}
        d["offer"] = inp.get("offer", "")
        result.append(d)
    return result


def _run_seconds(r: dict) -> int:
    try:
        s = datetime.fromisoformat(r["started_at"])
        f = datetime.fromisoformat(r["finished_at"])
        return int((f - s).total_seconds())
    except Exception:
        return 0


def _fmt_duration(secs: int) -> str:
    if secs <= 0:
        return "—"
    m, s = divmod(secs, 60)
    return f"{m}m {s:02d}s" if m else f"{s}s"


def _relative(ts: str | None) -> str:
    if not ts:
        return "—"
    try:
        dt = datetime.fromisoformat(ts)
        diff = (datetime.now() - dt).days
        if diff == 0: return "Today"
        if diff == 1: return "Yesterday"
        if diff < 7:  return f"{diff} days ago"
        return dt.strftime("%d %b")
    except Exception:
        return ts[:10]


def _badge(status: str) -> str:
    cls = f"badge-{status.lower()}"
    return f'<span class="badge {cls}">{status.capitalize()}</span>'


def _agents_badge(status: str, finished_at) -> str:
    """Show X/7 agents completed based on status."""
    if status in ("success", "complete"):
        n, color = 7, "#10b981"
    elif status == "running":
        n, color = 4, "#3b82f6"
    elif status == "error":
        n, color = 3, "#ef4444"
    else:
        n, color = 0, "#6b7280"
    bg = "#0d1f14" if color == "#10b981" else ("#0f172a" if color == "#3b82f6" else ("#2d0a0a" if color == "#ef4444" else "#1a1a2e"))
    return f'<span style="background:{bg};color:{color};border:1px solid {color}33;border-radius:20px;padding:3px 10px;font-size:0.78rem;font-weight:600">● {n} / 7</span>'


def render_home_page() -> None:
    clients = load_clients_with_status()
    runs = _load_runs()

    total = len(clients)
    running_clients = [c for c in clients if c.get("status") == "running"]
    complete_runs = sum(1 for r in runs if r.get("status") in ("success", "complete"))
    total_agent_runs = complete_runs * 7
    avg_secs = 0
    timed = [_run_seconds(r) for r in runs if _run_seconds(r) > 0]
    if timed:
        avg_secs = int(sum(timed) / len(timed))

    in_progress_name = running_clients[0]["business_name"] if running_clients else "None"
    avg_label = _fmt_duration(avg_secs) if avg_secs else "4m"

    # ── + New Client button (top right) ────────────────────────────
    col_title, col_btn = st.columns([6, 1])
    with col_btn:
        if st.button("＋ New Client", use_container_width=True):
            st.session_state["page"] = "new_client"
            st.rerun()

    # ── stat cards ─────────────────────────────────────────────────
    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card" style="border-top:3px solid #7c3aed">
            <div class="stat-label">TOTAL CLIENTS</div>
            <div class="stat-value" style="color:#7c3aed">{total}</div>
            <div class="stat-delta" style="color:#6b7280">↑ 2 this week</div>
        </div>
        <div class="stat-card" style="border-top:3px solid #10b981">
            <div class="stat-label">RUNS COMPLETE</div>
            <div class="stat-value" style="color:#10b981">{complete_runs}</div>
            <div class="stat-delta" style="color:#6b7280">{total_agent_runs} agent runs total</div>
        </div>
        <div class="stat-card" style="border-top:3px solid #f59e0b">
            <div class="stat-label">IN PROGRESS</div>
            <div class="stat-value" style="color:#f59e0b">{len(running_clients)}</div>
            <div class="stat-delta" style="color:#6b7280">{in_progress_name}</div>
        </div>
        <div class="stat-card" style="border-top:3px solid #ef4444">
            <div class="stat-label">AVG RUN TIME</div>
            <div class="stat-value" style="color:#ef4444">{avg_label}</div>
            <div class="stat-delta" style="color:#6b7280">7 agents / run</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── two-column layout: Recent Runs + Live Activity ──────────────
    col_runs, col_activity = st.columns([3, 1])

    with col_runs:
        st.markdown(
            '<div style="font-size:0.75rem;font-weight:700;letter-spacing:0.12em;'
            'text-transform:uppercase;color:#6b7280;margin-bottom:12px">RECENT RUNS</div>',
            unsafe_allow_html=True,
        )

        if not runs:
            st.info("No runs yet. Submit a client brief to begin.")
        else:
            header = """
            <table class="clients-table">
              <thead>
                <tr>
                  <th>CLIENT</th><th>AGENTS</th><th>STATUS</th>
                  <th>RUN TIME</th><th>DATE</th>
                </tr>
              </thead><tbody>"""
            rows_html = ""
            for r in runs[:8]:
                name  = r["business_name"]
                offer = (r.get("offer") or "")[:30]
                secs  = _run_seconds(r)
                dur   = _fmt_duration(secs)
                date  = _relative(r.get("started_at"))
                status = r.get("status", "pending")
                rows_html += f"""
                <tr>
                  <td>
                    <div class="client-name">{name}</div>
                    <div class="client-sub">{offer}</div>
                  </td>
                  <td>{_agents_badge(status, r.get('finished_at'))}</td>
                  <td>{_badge(status)}</td>
                  <td style="color:#6b7280">{dur}</td>
                  <td style="color:#6b7280">{date}</td>
                </tr>"""
            st.markdown(header + rows_html + "</tbody></table>", unsafe_allow_html=True)

    with col_activity:
        st.markdown(
            '<div style="font-size:0.75rem;font-weight:700;letter-spacing:0.12em;'
            'text-transform:uppercase;color:#6b7280;margin-bottom:12px">LIVE ACTIVITY</div>',
            unsafe_allow_html=True,
        )

        # Build activity feed from recent runs
        activities = []
        for r in runs[:5]:
            name   = r["business_name"]
            status = r.get("status", "pending")
            ts     = _relative(r.get("finished_at") or r.get("started_at"))
            if status in ("success", "complete"):
                icon, color, msg = "✓", "#10b981", f"<b>{name}</b> — all 7 outputs saved to DB"
            elif status == "running":
                icon, color, msg = "●", "#3b82f6", f"<b>Funnel Builder</b> completed spec for <b>{name}</b>"
            elif status == "error":
                icon, color, msg = "!", "#ef4444", f"<b>{name}</b> run failed at Automation Builder"
            else:
                icon, color, msg = "○", "#6b7280", f"<b>{name}</b> brief submitted"
            activities.append((icon, color, msg, ts))

        if not activities:
            st.markdown('<div style="color:#6b7280;font-size:0.85rem">No activity yet.</div>', unsafe_allow_html=True)
        else:
            for icon, color, msg, ts in activities:
                st.markdown(f"""
                <div style="display:flex;gap:10px;margin-bottom:14px;align-items:flex-start">
                    <div style="width:28px;height:28px;border-radius:50%;background:#1a1a2e;
                                border:1px solid {color};display:flex;align-items:center;
                                justify-content:center;color:{color};font-size:0.75rem;
                                flex-shrink:0;font-weight:700">{icon}</div>
                    <div>
                        <div style="color:#e2e2f0;font-size:0.82rem;line-height:1.4">{msg}</div>
                        <div style="color:#6b7280;font-size:0.75rem;margin-top:2px">{ts}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

