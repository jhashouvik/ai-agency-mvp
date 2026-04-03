"""
tasks/models.py
────────────────
Data model for a client brief.
Validate and pass this object through the entire pipeline.
"""

from dataclasses import dataclass


@dataclass
class ClientInput:
    business_name: str
    offer: str
    audience: str
    positioning: str
    goals: str
    budget: str
    current_situation: str

    def to_dict(self) -> dict:
        return {
            "business_name": self.business_name,
            "offer": self.offer,
            "audience": self.audience,
            "positioning": self.positioning,
            "goals": self.goals,
            "budget": self.budget,
            "current_situation": self.current_situation,
        }

    def as_context_block(self) -> str:
        """Formatted string injected into every task description."""
        return (
            f"CLIENT BRIEF\n"
            f"{'─' * 40}\n"
            f"Business      : {self.business_name}\n"
            f"Offer         : {self.offer}\n"
            f"Audience      : {self.audience}\n"
            f"Positioning   : {self.positioning}\n"
            f"Goals         : {self.goals}\n"
            f"Budget        : {self.budget}\n"
            f"Current State : {self.current_situation}\n"
            f"{'─' * 40}"
        )
