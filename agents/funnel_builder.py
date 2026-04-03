"""
agents/funnel_builder.py
─────────────────────────
Funnel Builder agent — produces a page-by-page GHL funnel
specification: sections, copy placeholders, form fields,
and redirect logic for each page.
"""

from crewai import Agent
from .llm import get_llm


def build_funnel_builder() -> Agent:
    return Agent(
        role="GHL Funnel Architect",
        goal=(
            "Design a complete funnel structure with every page, section, "
            "copy placeholder, form field, and next-step logic specified "
            "for direct GHL implementation — zero interpretation needed."
        ),
        backstory=(
            "You are a conversion-focused funnel designer who thinks in pages, "
            "sections, and user journey. You have built hundreds of funnels "
            "inside GoHighLevel. Every spec you produce is handed directly to "
            "a GHL builder who implements it exactly as written. "
            "You are precise, detailed, and structured."
        ),
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )
