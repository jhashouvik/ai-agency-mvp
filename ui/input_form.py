"""
ui/input_form.py
─────────────────
Renders the "New Client Brief" tab.
On submit, validates, runs the crew, saves to DB,
and stores results in session state.
"""

import streamlit as st

from tasks.models import ClientInput
from database import save_client, log_completed_run
from utils import Timer
from utils.logger import get_logger

log = get_logger(__name__)


def render_input_form() -> None:
    st.subheader("Enter Client Brief")
    st.info(
        "Fill in all fields and click **Run AI Agency System**. "
        "All 7 agents run sequentially — this takes **3–6 minutes**. "
        "Do not close the tab."
    )

    with st.form("client_form", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            business_name = st.text_input(
                "Business Name *",
                placeholder="FitLife Coaching",
            )
            offer = st.text_area(
                "Offer *",
                placeholder="12-week 1-on-1 coaching programme, £997",
                height=90,
            )
            audience = st.text_area(
                "Target Audience *",
                placeholder="Men aged 35–55 who want to lose weight and get fit",
                height=90,
            )
            goals = st.text_area(
                "Goals *",
                placeholder="30 qualified leads/month, £15k MRR",
                height=90,
            )

        with col2:
            positioning = st.text_area(
                "Positioning / USP *",
                placeholder="Evidence-based, no crash diets, sustainable results",
                height=90,
            )
            budget = st.text_input(
                "Ad Budget *",
                placeholder="£1,500/month",
            )
            current_situation = st.text_area(
                "Current Situation *",
                placeholder=(
                    "No funnel. Running Facebook ads to a basic website. "
                    "Low conversion rate, no follow-up system."
                ),
                height=90,
            )

        submitted = st.form_submit_button(
            "🚀 Run AI Agency System",
            use_container_width=True,
            type="primary",
        )

    if submitted:
        _handle_submission(
            business_name=business_name,
            offer=offer,
            audience=audience,
            positioning=positioning,
            goals=goals,
            budget=budget,
            current_situation=current_situation,
        )


# ── Private helpers ────────────────────────────────────────────────

def _handle_submission(**fields: str) -> None:
    missing = [k for k, v in fields.items() if not v.strip()]
    if missing:
        log.warning("Submission rejected — missing fields: %s", missing)
        st.error(f"Please fill in: {', '.join(missing).replace('_', ' ')}")
        return

    client = ClientInput(**fields)
    log.info("Form submitted — business_name=%r", client.business_name)

    progress = st.progress(0, text="Starting agents…")
    status   = st.empty()

    steps = [
        "Strategist thinking…",
        "Copywriter writing…",
        "Media buyer planning…",
        "Funnel builder designing…",
        "Automation builder mapping…",
        "Creative director briefing…",
        "Project manager planning…",
        "Saving outputs…",
    ]

    try:
        with st.spinner(""):
            with Timer() as t:
                import threading
                import datetime as _dt
                _run_started = _dt.datetime.now().isoformat(timespec="seconds")

                result_holder: dict = {}
                error_holder:  dict = {}

                def _run():
                    try:
                        from crew import run_crew  # lazy import — keeps crewai/embedchain/chromadb out of startup
                        log.info("Crew thread started — client=%r", client.business_name)
                        # Try to capture real token usage via LangChain callback
                        cb_tokens = 0
                        cb_cost   = 0.0
                        try:
                            try:
                                from langchain_community.callbacks import get_openai_callback
                            except ImportError:
                                from langchain.callbacks import get_openai_callback
                            with get_openai_callback() as cb:
                                result_holder["outputs"] = run_crew(client)
                            cb_tokens = cb.total_tokens
                            cb_cost   = cb.total_cost
                            log.info("Callback token usage — total=%d  cost=$%.4f", cb_tokens, cb_cost)
                        except Exception:
                            result_holder["outputs"] = run_crew(client)

                        outputs = result_holder.get("outputs", {})

                        # If callback didn't capture tokens (returns 0), estimate from output text.
                        # CrewAI makes multiple iterative LLM calls per agent (think/act/observe).
                        # Calibrated against real OpenAI dashboard: $2.20 total across 4 runs.
                        # Real ratio: $2.20 actual vs $0.3441 raw char estimate = 6.39x multiplier.
                        # GPT-4o pricing: $2.50/1M input + $10.00/1M output, 70/30 split.
                        if cb_tokens == 0 and outputs:
                            total_output_chars = sum(len(str(v)) for v in outputs.values() if v)
                            input_chars        = len(str(client.to_dict()))
                            visible_tokens = int((total_output_chars + input_chars) / 4)
                            # scale by calibration factor (accounts for intermediate reasoning steps)
                            total_tokens   = int(visible_tokens * 6.39)
                            est_in_tokens  = int(total_tokens * 0.70)
                            est_out_tokens = int(total_tokens * 0.30)
                            cb_tokens      = total_tokens
                            cb_cost        = (est_in_tokens / 1_000_000 * 2.50) + (est_out_tokens / 1_000_000 * 10.00)
                            log.info("Estimated tokens (calibrated 6.39x) — total=%d  cost=$%.4f", cb_tokens, cb_cost)

                        result_holder["tokens_input"]  = int(cb_tokens * 0.70)
                        result_holder["tokens_output"] = int(cb_tokens * 0.30)
                        result_holder["tokens_total"]  = cb_tokens
                        result_holder["cost_usd"]      = cb_cost
                        log.info("Crew thread finished successfully")
                    except Exception as exc:          # noqa: BLE001
                        log.exception("Crew thread raised an exception: %s", exc)
                        error_holder["error"] = exc

                thread = threading.Thread(target=_run, daemon=True)
                thread.start()

                step_idx = 0
                import time
                while thread.is_alive():
                    pct = min(int((step_idx / len(steps)) * 90), 90)
                    progress.progress(pct, text=steps[min(step_idx, len(steps) - 2)])
                    time.sleep(6)
                    step_idx += 1

                thread.join()

            if "error" in error_holder:
                raise error_holder["error"]

            outputs = result_holder["outputs"]

        import datetime as _dt
        _run_finished = _dt.datetime.now().isoformat(timespec="seconds")
        _duration_secs = int(
            (_dt.datetime.fromisoformat(_run_finished) -
             _dt.datetime.fromisoformat(_run_started)).total_seconds()
        )
        log.info("Run complete in %s — saving to DB", t.pretty)
        progress.progress(95, text="Saving to database…")
        client_id = save_client(client.to_dict(), outputs)
        log_completed_run(
            client_id, _run_started, _run_finished, "success",
            tokens_input=result_holder.get("tokens_input", 0),
            tokens_output=result_holder.get("tokens_output", 0),
            tokens_total=result_holder.get("tokens_total", 0),
            cost_usd=result_holder.get("cost_usd", 0.0),
            duration_secs=_duration_secs,
        )
        progress.progress(100, text="Done!")

        st.success(
            f"✅ Complete in {t.pretty}! "
            f"Client saved (ID #{client_id}). "
            f"Switch to the **View Output** tab."
        )

        st.session_state["current_outputs"] = outputs
        st.session_state["current_client"]  = client.to_dict()
        st.session_state["view_client"]     = client_id

    except Exception as exc:  # noqa: BLE001
        log.exception("Unhandled error during submission: %s", exc)
        progress.empty()
        st.error(f"Something went wrong: {exc}")
        if st.session_state.get("DEBUG"):
            st.exception(exc)
