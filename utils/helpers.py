"""
utils/helpers.py
─────────────────
Utility functions shared across the application.
No business logic here — pure helpers.
"""

import time


# Keys in the same order as tasks/builder.py task list
TASK_KEYS = [
    "strategy",
    "copy",
    "media_plan",
    "funnel",
    "automations",
    "creatives",
    "project_plan",
]


def extract_task_outputs(tasks: list) -> dict[str, str]:
    """
    Map each completed CrewAI Task to a human-readable key.
    Returns a dict ready for database storage and UI display.
    """
    outputs: dict[str, str] = {}
    for key, task in zip(TASK_KEYS, tasks):
        raw = task.output
        outputs[key] = str(raw) if raw is not None else ""
    return outputs


def format_duration(seconds: float) -> str:
    """Convert elapsed seconds to a human-readable string."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}m {secs}s"


class Timer:
    """Simple context-manager timer."""

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, *_):
        self.elapsed = time.perf_counter() - self._start

    @property
    def pretty(self) -> str:
        return format_duration(self.elapsed)
