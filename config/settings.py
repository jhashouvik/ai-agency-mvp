"""
config/settings.py
──────────────────
Single source of truth for all environment variables and app constants.
All other modules import from here — never call os.getenv() directly elsewhere.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    # OpenAI
    openai_api_key: str
    openai_model: str
    openai_temperature: float

    # Database
    db_path: str

    # App
    app_title: str
    debug: bool


def _load_settings() -> Settings:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY is not set. "
            "Copy .env.example to .env and add your key."
        )

    return Settings(
        openai_api_key=api_key,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        openai_temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
        db_path=os.getenv("DB_PATH", "agency.db"),
        app_title=os.getenv("APP_TITLE", "AI Marketing Agency System"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
    )


# Module-level singleton — import this everywhere
settings = _load_settings()
