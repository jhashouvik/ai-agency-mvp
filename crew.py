"""
crew.py
────────
Orchestration layer — the only module that imports from both
agents/ and tasks/ and wires them into a running Crew.

Usage:
    from crew import run_crew
    from tasks.models import ClientInput

    client = ClientInput(...)
    outputs = run_crew(client)
"""

from crewai import Crew, Process

from agents import (
    build_strategist,
    build_copywriter,
    build_media_buyer,
    build_funnel_builder,
    build_automation_builder,
    build_creative_director,
    build_project_manager,
)
from tasks.builder import build_all_tasks
from tasks.models import ClientInput
from utils import extract_task_outputs
from utils.logger import get_logger

log = get_logger(__name__)


def run_crew(client: ClientInput) -> dict[str, str]:
    """
    Build and run the full 7-agent pipeline for one client brief.

    Steps:
        1. Instantiate all tasks (which internally instantiate agents).
        2. Collect the unique agent instances from those tasks.
        3. Hand everything to CrewAI for sequential execution.
        4. Extract and return a {key: output_text} dict.

    Returns:
        dict with keys: strategy, copy, media_plan, funnel,
                        automations, creatives, project_plan
    """
    tasks = build_all_tasks(client)

    # Derive agent list from tasks — preserves the right instances
    agents = [task.agent for task in tasks]

    log.info(
        "Starting crew run — client=%r  agents=%d  tasks=%d",
        client.business_name,
        len(agents),
        len(tasks),
    )

    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )

    crew.kickoff()
    log.info("Crew kickoff complete — extracting outputs")

    outputs = extract_task_outputs(tasks)
    log.info(
        "Run finished — keys returned: %s",
        list(outputs.keys()),
    )
    return outputs
