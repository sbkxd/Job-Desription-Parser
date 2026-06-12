"""LangGraph router for routing decisions based on skill normalization confidence."""

import logging
from typing import Literal

from app.orchestration.state.state import PipelineState

logger = logging.getLogger(__name__)


def review_router(
    state: PipelineState,
) -> Literal["mistral_resolution", "persistence"]:
    """Conditional router that checks state confidence status.

    Args:
        state: The current PipelineState.

    Returns:
        The string name of the next node to execute.
    """
    review_res = state.get("review_result") or {}
    needs_mistral = review_res.get("needs_mistral", False)

    logger.info("Routing decision: needs_mistral = %s", needs_mistral)

    if needs_mistral:
        return "mistral_resolution"
    return "persistence"
