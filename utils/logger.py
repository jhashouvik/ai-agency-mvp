"""
utils/logger.py
────────────────
Centralised logging configuration for the AI Agency MVP.

• One log file per calendar date:  logs/YYYY-MM-DD.log
• Every run APPENDS to the existing daily file (never overwrites).
• Root logger + 'agency' named logger both write to the same handlers.
• Console handler mirrors the file so developers see output in the terminal.

Usage anywhere in the project:
    from utils.logger import get_logger
    log = get_logger(__name__)
    log.info("Something happened")
"""

import logging
import os
from datetime import date
from pathlib import Path


# ── Paths ──────────────────────────────────────────────────────────
_LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
_LOGS_DIR.mkdir(exist_ok=True)

# ── Format ─────────────────────────────────────────────────────────
_FMT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FMT = "%Y-%m-%d %H:%M:%S"

# ── Singleton guard ─────────────────────────────────────────────────
_configured: bool = False


def _configure() -> None:
    """Set up file + console handlers once per process."""
    global _configured
    if _configured:
        return

    log_file = _LOGS_DIR / f"{date.today().isoformat()}.log"

    formatter = logging.Formatter(_FMT, datefmt=_DATE_FMT)

    # File handler — append mode so reruns accumulate in the same daily file
    file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Console handler — useful during development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # Avoid duplicate handlers if Streamlit re-imports on hot-reload
    if not root.handlers:
        root.addHandler(file_handler)
        root.addHandler(console_handler)
    else:
        # Replace handlers to ensure our file handler is always present
        # (Streamlit may add its own StreamHandler on startup)
        has_file = any(isinstance(h, logging.FileHandler) for h in root.handlers)
        if not has_file:
            root.addHandler(file_handler)

    # Quiet noisy third-party loggers
    for noisy in ("httpx", "httpcore", "openai", "urllib3", "crewai"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger, ensuring handlers are configured first.

    Args:
        name: Typically ``__name__`` of the calling module.

    Returns:
        A configured :class:`logging.Logger` instance.
    """
    _configure()
    return logging.getLogger(name)
