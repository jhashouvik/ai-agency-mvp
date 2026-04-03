"""
dashboard/pages/agents.py
──────────────────────────
AI Agents page — stat cards + per-agent performance cards with progress bars.
Matches screenshot: "AI Agents / Performance and run stats per agent role"
"""

import streamlit as st
from database import load_clients_with_status
from database.connection import get_connection


AGENT_DEFS = [
    {
        "key": "strategy",
        "name": "Strategist",
        "tags": "go-to-market strategy · positioning · KPIs",
        "bar_color": "#7c3aed",
        "avg_time": "42s",
        "tokens": "~210k",
    },
    {
        "key": "copy",
        "name": "Copywriter",
        "tags": "ads · emails · landing pages · sales pages",
        "bar_color": "#10b981",
        "avg_time": "51s",
        "tokens": "~280k",
    },
    {
        "key": "media_plan",
        "name": "Media Buyer",
        "tags": "Meta campaign structure · audiences · budgets",
        "bar_color": "#f59e0b",
        "avg_time": "34s",
        "tokens": "~175k",
    },
    {
        "key": "funnel",
        "name": "Funnel Builder",
        "tags": "GHL funnel spec · pages · sections · flow",
        "bar_color": "#6366f1",
        "avg_time": "45s",
        "tokens": "~195k",
    },
    {
        "key": "automations",
        "name": "Automation Builder",
        "tags": "GHL workflows · nurture · pipeline rules",
        "bar_color": "#ef4444",
        "avg_time": "38s",
        "tokens": "~160k",
    },
    {
        "key": "creatives",
        "name": "Creative Director",
        "tags": "ad briefs · visuals · Midjourney prompts",
        "bar_color": "#f59e0b",
        "avg_time": "29s",
        "tokens": "~120k",
    },
    {
        "key": "project_plan",
        "name": "Project Manager",
        "tags": "30-day plan · milestones · task assignments",
        "bar_color": "#10b981",
        "avg_time": "22s",
        "tokens": "~90k",
    },
]


def _load_stats():
    conn = get_connection()
    total_runs = conn.execute("SELECT COUNT(*) FROM run_logs").fetchone()[0]
    success_runs = conn.execute(
        "SELECT COUNT(*) FROM run_logs WHERE status IN ('success','complete')"
    ).fetchone()[0]
    error_runs = conn.execute(
        "SELECT COUNT(*) FROM run_logs WHERE status='error'"
    ).fetchone()[0]
    client_count = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    conn.close()
    return total_runs, success_runs, error_runs, client_count


def render_agents_page() -> None:
    total_runs, success_runs, error_runs, client_count = _load_stats()

    total_agent_runs = total_runs * 7
    success_rate = int((success_runs / total_runs) * 100) if total_runs else 0
    failures = error_runs
    # estimated token spend: ~210k avg per agent run * total_agent_runs
    total_tokens = total_agent_runs * 210000
    token_label = f"{total_tokens / 1_000_000:.1f}M" if total_tokens >= 1_000_000 else f"{total_tokens // 1000}k"
    est_spend = f"${total_agent_runs * 0.44:.2f}"  # rough gpt-4o estimate

    # ── stat cards ─────────────────────────────────────────────────
    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card" style="border-top:3px solid #7c3aed">
            <div class="stat-label">TOTAL AGENT RUNS</div>
            <div class="stat-value" style="color:#7c3aed">{total_agent_runs}</div>
            <div class="stat-delta" style="color:#6b7280">Across {client_count} clients</div>
        </div>
        <div class="stat-card" style="border-top:3px solid #10b981">
            <div class="stat-label">SUCCESS RATE</div>
            <div class="stat-value" style="color:#10b981">{success_rate}%</div>
            <div class="stat-delta" style="color:#6b7280">{failures} failures total</div>
        </div>
        <div class="stat-card" style="border-top:3px solid #f59e0b">
            <div class="stat-label">AVG PER AGENT</div>
            <div class="stat-value" style="color:#f59e0b">38s</div>
            <div class="stat-delta" style="color:#6b7280">GPT-4o response time</div>
        </div>
        <div class="stat-card" style="border-top:3px solid #ef4444">
            <div class="stat-label">TOKENS USED</div>
            <div class="stat-value" style="color:#ef4444">{token_label if total_tokens else "—"}</div>
            <div class="stat-delta" style="color:#6b7280">Est. {est_spend} spend</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── section label ───────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:0.75rem;font-weight:700;letter-spacing:0.12em;'
        'text-transform:uppercase;color:#6b7280;margin:8px 0 16px 0">AGENT PERFORMANCE</div>',
        unsafe_allow_html=True,
    )

    # ── 2-column grid of agent cards ───────────────────────────────
    pairs = [AGENT_DEFS[i:i+2] for i in range(0, len(AGENT_DEFS), 2)]
    for pair in pairs:
        cols = st.columns(2)
        for col, ag in zip(cols, pair):
            runs_for_agent = success_runs  # each client run = 1 per agent
            success_count  = success_runs
            fail_count     = error_runs
            with col:
                st.markdown(f"""
                <div style="background:#12122a;border:1px solid #1e1e3a;border-radius:12px;
                            padding:18px 20px;margin-bottom:12px;">
                    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px">
                        <span style="font-weight:700;font-size:0.95rem;color:#fff">{ag['name']}</span>
                        <span style="color:#6b7280;font-size:0.8rem">{runs_for_agent} runs</span>
                    </div>
                    <div style="color:#6b7280;font-size:0.78rem;margin-bottom:12px">{ag['tags']}</div>
                    <div style="height:4px;background:#1e1e3a;border-radius:2px;margin-bottom:10px">
                        <div style="height:4px;background:{ag['bar_color']};border-radius:2px;
                                    width:{success_rate}%"></div>
                    </div>
                    <div style="display:flex;gap:16px;font-size:0.78rem;color:#6b7280">
                        <span>Success <b style="color:#e2e2f0">{success_count}/{runs_for_agent}</b></span>
                        <span>Avg time <b style="color:#e2e2f0">{ag['avg_time']}</b></span>
                        <span>Tokens <b style="color:#e2e2f0">{ag['tokens']}</b></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

