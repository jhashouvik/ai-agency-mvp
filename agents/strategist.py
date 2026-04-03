"""
agents/strategist.py
─────────────────────
Strategist agent — runs first, produces the master strategy
that every downstream agent reads as context.
"""

from crewai import Agent
from .llm import get_llm


def build_strategist() -> Agent:
    return Agent(
        role="Senior Marketing Strategist",
        goal=(
            "Analyse the client brief and produce a complete, structured "
            "go-to-market strategy covering funnel recommendation, audience "
            "breakdown, offer positioning, campaign approach, and KPIs."
        ),
        backstory=(
            "You are a senior marketing strategist with 15 years of digital "
            "agency experience. You think in funnels, audiences, and offers. "
            "You produce numbered, structured strategy documents that other "
            "specialists can execute against immediately — no vague advice, "
            "no fluff, only actionable direction."
        ),
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )
