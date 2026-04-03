"""
agents/automation_builder.py
─────────────────────────────
Automation Builder agent — maps all GHL workflows, nurture
sequences, pipeline rules, and tag logic with precise
trigger → condition → action → timing detail.
"""

from crewai import Agent
from .llm import get_llm


def build_automation_builder() -> Agent:
    return Agent(
        role="CRM Automation Architect",
        goal=(
            "Design all GHL workflows, nurture sequences, pipeline stage rules, "
            "follow-up sequences, and tag logic with complete trigger, condition, "
            "action, and timing detail for immediate GHL implementation."
        ),
        backstory=(
            "You build the backend logic of marketing systems inside GoHighLevel. "
            "Triggers, conditions, actions, timing — you map these in precise detail. "
            "A GHL technician can open your output and build every workflow exactly "
            "as specified. You never leave decisions to the implementer."
        ),
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )
