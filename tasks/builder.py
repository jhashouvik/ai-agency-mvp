"""
tasks/builder.py
─────────────────
Builds all 7 CrewAI Task objects in the correct execution order.
Each task carries an explicit expected_output so the LLM knows
exactly what format to produce.

Context chaining: later tasks receive prior task objects via
the `context` parameter — CrewAI injects their outputs automatically.
"""

from crewai import Task
from agents import (
    build_strategist,
    build_copywriter,
    build_media_buyer,
    build_funnel_builder,
    build_automation_builder,
    build_creative_director,
    build_project_manager,
)
from .models import ClientInput
from utils.logger import get_logger

log = get_logger(__name__)


def build_all_tasks(client: ClientInput) -> list[Task]:
    """
    Instantiate agents and wire up the full 7-task pipeline.

    Returns a list of Task objects in execution order.
    The crew.py module passes this list to the Crew constructor.
    """
    ctx = client.as_context_block()
    log.info("Building 7-task pipeline for client=%r", client.business_name)

    # ── Instantiate agents ──────────────────────────────────────────
    strategist          = build_strategist()
    copywriter          = build_copywriter()
    media_buyer         = build_media_buyer()
    funnel_builder      = build_funnel_builder()
    automation_builder  = build_automation_builder()
    creative_director   = build_creative_director()
    project_manager     = build_project_manager()

    # ── Task 1: Strategy (runs first, feeds everyone) ───────────────
    t_strategy = Task(
        description=(
            f"Analyse the following client brief and produce a complete "
            f"marketing strategy document.\n\n{ctx}"
        ),
        expected_output=(
            "A structured strategy document with clearly numbered sections:\n"
            "1. Offer analysis and positioning angle\n"
            "2. Target audience breakdown (demographics, psychographics, "
            "   pain points, objections)\n"
            "3. Funnel recommendation (type, stages, rationale)\n"
            "4. Campaign approach (primary channel, messaging hierarchy)\n"
            "5. KPIs and success metrics with target numbers"
        ),
        agent=strategist,
    )

    # ── Task 2: Copy assets ─────────────────────────────────────────
    t_copy = Task(
        description=(
            "Using the strategy above, write all copy assets required "
            "for launch. Structure each section with a clear heading."
        ),
        expected_output=(
            "A labelled copy document containing:\n"
            "1. THREE ad hooks (opening lines for Meta ads)\n"
            "2. Primary Meta ad — full copy (hook, body, CTA)\n"
            "3. Landing page — headline, subheadline, 5 bullet benefits, CTA text\n"
            "4. Sales page — headline + opening lead paragraph\n"
            "5. Email nurture sequence — 5 emails each with subject line and full body"
        ),
        agent=copywriter,
        context=[t_strategy],
    )

    # ── Task 3: Media plan ──────────────────────────────────────────
    t_media = Task(
        description=(
            "Using the strategy above, design the complete Meta paid "
            "campaign structure ready for a media buyer to implement."
        ),
        expected_output=(
            "A structured campaign map containing:\n"
            "1. Campaign objective and rationale\n"
            "2. Three ad sets — audience definition, interest/behaviour "
            "   targeting, and budget split for each\n"
            "3. Creative angle per ad set (messaging angle + reason)\n"
            "4. Testing plan — what to test first and how to read results\n"
            "5. Recommended bidding strategy and daily budget breakdown"
        ),
        agent=media_buyer,
        context=[t_strategy],
    )

    # ── Task 4: Funnel spec ─────────────────────────────────────────
    t_funnel = Task(
        description=(
            "Using the strategy and copy above, design the complete "
            "GHL funnel specification page by page."
        ),
        expected_output=(
            "A GHL funnel spec document. For EACH page include:\n"
            "- Page name and goal\n"
            "- Sections in order (section name + element list)\n"
            "- Copy placeholders (where the copy from Task 2 slots in)\n"
            "- Form fields required\n"
            "- Next step / redirect logic\n\n"
            "Pages to cover: Opt-in page, Thank-you page, "
            "Sales/VSL page, Application/Booking page"
        ),
        agent=funnel_builder,
        context=[t_strategy, t_copy],
    )

    # ── Task 5: Automation map ──────────────────────────────────────
    t_automations = Task(
        description=(
            "Using the funnel spec and copy assets above, design all "
            "GHL workflows and CRM automations."
        ),
        expected_output=(
            "An automation map with trigger → condition → action → timing "
            "detail for each workflow:\n"
            "1. Lead intake workflow\n"
            "2. Nurture sequence workflow (tied to email copy from Task 2)\n"
            "3. Pipeline stage movement rules\n"
            "4. Follow-up sequences (SMS + email, timing, conditions)\n"
            "5. Tag logic (what tags are applied and when)"
        ),
        agent=automation_builder,
        context=[t_funnel, t_copy],
    )

    # ── Task 6: Creative briefs ─────────────────────────────────────
    t_creatives = Task(
        description=(
            "Using the campaign structure and copy above, produce "
            "3 ad creative briefs for the media launch."
        ),
        expected_output=(
            "Three creative briefs. Each brief must contain:\n"
            "- Concept name\n"
            "- Format and dimensions (e.g. 1080×1080, 9:16 Story)\n"
            "- Headline overlay text\n"
            "- Visual description (what's in the image or video)\n"
            "- Emotional hook (feeling the ad triggers)\n"
            "- Colour palette and style direction\n"
            "- Midjourney prompt (for image-based ads)"
        ),
        agent=creative_director,
        context=[t_copy, t_media],
    )

    # ── Task 7: Project plan ────────────────────────────────────────
    t_project = Task(
        description=(
            "Using all deliverables above, produce a phased project "
            "plan that a delivery team can action from Day 1."
        ),
        expected_output=(
            "A project plan organised into 4 phases:\n"
            "Phase 1 — Strategy & Copy (Days 1–3)\n"
            "Phase 2 — Funnel Build (Days 4–7)\n"
            "Phase 3 — Automation Setup (Days 6–8)\n"
            "Phase 4 — Campaign Launch (Days 8–10)\n\n"
            "For each task: task name, description, assigned role, "
            "due day number, and dependencies."
        ),
        agent=project_manager,
        context=[t_strategy, t_copy, t_media, t_funnel, t_automations, t_creatives],
    )

    task_list = [
        t_strategy,
        t_copy,
        t_media,
        t_funnel,
        t_automations,
        t_creatives,
        t_project,
    ]
    log.debug("All %d tasks built successfully", len(task_list))
    return task_list
