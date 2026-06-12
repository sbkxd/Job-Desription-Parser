"""LangGraph router for routing decisions based on skill normalization confidence."""

import logging
from typing import Literal

from app.orchestration.state.state import PipelineState

logger = logging.getLogger(__name__)


def review_router(
    state: PipelineState,
) -> Literal["ollama_resolution", "persistence"]:
    """Conditional router that checks state confidence status.

    Args:
        state: The current PipelineState.

    Returns:
        The string name of the next node to execute.
    """
    review_res = state.get("review_result") or {}
    needs_ollama = review_res.get("needs_ollama", False)

    logger.info("Routing decision: needs_ollama = %s", needs_ollama)

    if needs_ollama:
        return "ollama_resolution"
    return "persistence"
