"""
agents/llm.py
─────────────
LLM factory. All agents share this single GPT-4o instance.
Swap model or provider here without touching any agent file.

Supports both old crewai (llm: Any, needs ChatOpenAI) and
new crewai >=1.x (llm: Union[str, BaseLLM], needs crewai.LLM).
"""

import os
from config import settings


def get_llm():
    """Return an LLM instance compatible with whichever crewai version is running."""
    os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)
    try:
        # crewai >= 1.x ships its own LLM wrapper
        from crewai import LLM
        return LLM(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=settings.openai_temperature,
        )
    except ImportError:
        # old crewai (< 1.x) uses LangChain's ChatOpenAI internally
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key,
        )
