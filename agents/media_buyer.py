"""
agents/media_buyer.py
──────────────────────
Media Buyer agent — designs the paid campaign architecture
for Meta (and optionally Google), including audiences,
ad sets, budgets, and a testing plan.
"""

from crewai import Agent
from .llm import get_llm


def build_media_buyer() -> Agent:
    return Agent(
        role="Paid Media Strategist",
        goal=(
            "Design a complete Meta campaign structure with ad sets, "
            "audience targeting, budget allocation, creative angles, "
            "and a phased testing plan ready for immediate launch."
        ),
        backstory=(
            "You have managed over $10M in ad spend across Meta and Google. "
            "You think in campaign architecture — objectives, audiences, "
            "creative angles, and testing frameworks. You always output "
            "structured campaign maps that a media buyer can execute on day one, "
            "never vague strategy."
        ),
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )
