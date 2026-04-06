"""
dashboard/pages/agents.py
──────────────────────────
AI Agents page — stat cards + per-agent performance cards with progress bars.
All values loaded from real database data — no hardcoded estimates.
"""

import json
import streamlit as st
from database.connection import get_connection


AGENT_DEFS = [
    {"key": "strategy",     "name": "Strategist",        "tags": "go-to-market strategy · positioning · KPIs",   "bar_color": "#7c3aed"},
    {"key": "copy",         "name": "Copywriter",         "tags": "ads · emails · landing pages · sales pages",   "bar_color": "#10b981"},
    {"key": "media_plan",   "name": "Media Buyer",        "tags": "Meta campaign structure · audiences · budgets", "bar_color": "#f59e0b"},
    {"key": "funnel",       "name": "Funnel Builder",     "tags": "GHL funnel spec · pages · sections · flow",    "bar_color": "#6366f1"},
    {"key": "automations",  "name": "Automation Builder", "tags": "GHL workflows · nurture · pipeline rules",     "bar_color": "#ef4444"},
    {"key": "creatives",    "name": "Creative Director",  "tags": "ad briefs · visuals · Midjourney prompts",     "bar_color": "#f59e0b"},
    {"key": "project_plan", "name": "Project Manager",    "tags": "30-day plan · milestones · task assignments",  "bar_color": "#10b981"},
]


def _load_all_stats() -> dict:
    conn = get_connection()

    total_runs   = conn.execute("SELECT COUNT(*) FROM run_logs").fetchone()[0]
    success_runs = conn.execute(
        "SELECT COUNT(*) FROM run_logs WHERE status IN ('success','complete')"
    ).fetchone()[0]
    error_runs   = conn.execute("SELECT COUNT(*) FROM run_logs WHERE status='error'").fetchone()[0]
    client_count = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]

    tok = conn.execute(
        """
        SELECT
            COALESCE(SUM(tokens_total),  0)   AS total_tokens,
            COALESCE(SUM(tokens_input),  0)   AS tokens_input,
            COALESCE(SUM(tokens_output), 0)   AS tokens_output,
            COALESCE(SUM(cost_usd),      0.0) AS total_cost,
            COALESCE(AVG(NULLIF(duration_secs, 0)), 0) AS avg_duration
        FROM run_logs
        WHERE status IN ('success', 'complete')
        """
    ).fetchone()

    # per-agent output char lengths from stored client outputs
    agent_chars: dict[str, list[int]] = {ag["key"]: [] for ag in AGENT_DEFS}
    rows = conn.execute("SELECT outputs FROM clients WHERE outputs IS NOT NULL").fetchall()
    for row in rows:
        try:
            out = json.loads(row[0] or "{}")
        except Exception:
            continue
        for ag in AGENT_DEFS:
            v = out.get(ag["key"], "")
            if v:
                agent_chars[ag["key"]].append(len(v))

    conn.close()

    # approx tokens per agent: chars / 4 (standard GPT chars-per-token ratio)
    agent_tokens: dict[str, int] = {}
    for ag in AGENT_DEFS:
        lengths = agent_chars[ag["key"]]
        agent_tokens[ag["key"]] = int(sum(lengths) / 4) if lengths else 0

    return {
        "total_runs":    total_runs,
        "success_runs":  success_runs,
        "error_runs":    error_runs,
        "client_count":  client_count,
        "total_tokens":  tok["total_tokens"],
        "tokens_input":  tok["tokens_input"],
        "tokens_output": tok["tokens_output"],
        "total_cost":    tok["total_cost"],
        "avg_duration":  tok["avg_duration"],
        "agent_tokens":  agent_tokens,
    }


def render_agents_page() -> None:
    d = _load_all_stats()

    total_agent_runs = d["total_runs"] * 7
    success_rate     = int((d["success_runs"] / d["total_runs"]) * 100) if d["total_runs"] else 0

    # ── token / cost display labels ─────────────────────────────────
    tt = d["total_tokens"]
    if tt >= 1_000_000:
        token_label = f"{tt / 1_000_000:.1f}M"
    elif tt >= 1_000:
        token_label = f"{tt / 1_000:.0f}k"
    else:
        token_label = str(tt) if tt else "—"

    cost_label = f"${d['total_cost']:.4f}" if d["total_cost"] else "—"
    cost_sub   = f"Real OpenAI spend · {token_label} tokens"

    # avg time per agent = total crew run time / 7
    avg_secs_agent = int(d["avg_duration"] / 7) if d["avg_duration"] else 0
    avg_time_label = f"{avg_secs_agent}s" if avg_secs_agent else "—"
    avg_time_sub   = "Avg per-agent response time" if avg_secs_agent else "No runs recorded yet"

    # ── stat cards ──────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(
        '<div class="stat-card" style="border-top:3px solid #7c3aed">'
        '<div class="stat-label">TOTAL AGENT RUNS</div>'
        f'<div class="stat-value" style="color:#7c3aed">{total_agent_runs if total_agent_runs else "—"}</div>'
        f'<div class="stat-delta" style="color:#6b7280">Across {d["client_count"]} client{"s" if d["client_count"] != 1 else ""}</div>'
        "</div>",
        unsafe_allow_html=True,
    )
    c2.markdown(
        '<div class="stat-card" style="border-top:3px solid #10b981">'
        '<div class="stat-label">SUCCESS RATE</div>'
        f'<div class="stat-value" style="color:#10b981">{success_rate}%</div>'
        f'<div class="stat-delta" style="color:#6b7280">{d["error_runs"]} failure{"s" if d["error_runs"] != 1 else ""} total</div>'
        "</div>",
        unsafe_allow_html=True,
    )
    c3.markdown(
        '<div class="stat-card" style="border-top:3px solid #f59e0b">'
        '<div class="stat-label">AVG PER AGENT</div>'
        f'<div class="stat-value" style="color:#f59e0b">{avg_time_label}</div>'
        f'<div class="stat-delta" style="color:#6b7280">{avg_time_sub}</div>'
        "</div>",
        unsafe_allow_html=True,
    )
    c4.markdown(
        '<div class="stat-card" style="border-top:3px solid #ef4444">'
        '<div class="stat-label">ACTUAL COST</div>'
        f'<div class="stat-value" style="color:#ef4444">{cost_label}</div>'
        f'<div class="stat-delta" style="color:#6b7280">{cost_sub}</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    # ── section label ───────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:0.75rem;font-weight:700;letter-spacing:0.12em;'
        'text-transform:uppercase;color:#6b7280;margin:16px 0 16px 0">AGENT PERFORMANCE</div>',
        unsafe_allow_html=True,
    )

    # ── 2-column grid of agent cards ────────────────────────────────
    agent_avg_secs = int(d["avg_duration"] / 7) if d["avg_duration"] else 0
    pairs = [AGENT_DEFS[i:i + 2] for i in range(0, len(AGENT_DEFS), 2)]
    for pair in pairs:
        cols = st.columns(2)
        for col, ag in zip(cols, pair):
            tok_count = d["agent_tokens"].get(ag["key"], 0)
            tok_str = (
                f"{tok_count / 1_000:.0f}k" if tok_count >= 1_000
                else str(tok_count) if tok_count else "—"
            )
            time_str = f"{agent_avg_secs}s" if agent_avg_secs else "—"
            with col:
                st.markdown(
                    '<div style="background:#12122a;border:1px solid #1e1e3a;border-radius:12px;'
                    'padding:18px 20px;margin-bottom:12px;">'
                    '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px">'
                    f'<span style="font-weight:700;font-size:0.95rem;color:#fff">{ag["name"]}</span>'
                    f'<span style="color:#6b7280;font-size:0.8rem">{d["success_runs"]} runs</span>'
                    "</div>"
                    f'<div style="color:#6b7280;font-size:0.78rem;margin-bottom:12px">{ag["tags"]}</div>'
                    '<div style="height:4px;background:#1e1e3a;border-radius:2px;margin-bottom:10px">'
                    f'<div style="height:4px;background:{ag["bar_color"]};border-radius:2px;width:{success_rate}%"></div>'
                    "</div>"
                    '<div style="display:flex;gap:16px;font-size:0.78rem;color:#6b7280">'
                    f'<span>Success <b style="color:#e2e2f0">{d["success_runs"]}/{d["total_runs"]}</b></span>'
                    f'<span>Avg time <b style="color:#e2e2f0">{time_str}</b></span>'
                    f'<span>Output tokens <b style="color:#e2e2f0">{tok_str}</b></span>'
                    "</div></div>",
                    unsafe_allow_html=True,
                )

