"""
agents/copywriter.py
─────────────────────
Copywriter agent — reads the strategy and produces all copy assets:
ads, landing page, sales page, and email nurture sequence.
"""

from crewai import Agent
from .llm import get_llm


def build_copywriter() -> Agent:
    return Agent(
        role="Direct Response Copywriter",
        goal=(
            "Write production-ready copy for Meta ads, landing pages, "
            "sales pages, and a 5-email nurture sequence based on the "
            "strategy provided. Every word must earn its place."
        ),
        backstory=(
            "You are a world-class direct response copywriter trained in "
            "AIDA, PAS, and hook frameworks. No fluff, no filler. Your output "
            "is always clearly labelled and structured so it can be pasted "
            "directly into a funnel builder or email platform without editing."
        ),
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )
