"""LangGraph node for evaluating skill confidence thresholds and routing decisions."""

import time
from typing import Any, Dict

from app.orchestration.state.state import PipelineState
from app.review.evaluators.confidence_evaluator import ConfidenceEvaluator
from app.review.schemas.schemas import ReviewStatusSchema


async def review_eval_node(state: PipelineState) -> Dict[str, Any]:
    """Evaluate skill confidences and determine routing paths.

    Args:
        state: The current PipelineState.

    Returns:
        State updates containing review_result and execution_metadata.
    """
    start_time = time.perf_counter()
    normalization_result = state.get("normalization_result") or {}
    skills = normalization_result.get("skills") or []

    evaluator = ConfidenceEvaluator()
    needs_ollama = False
    needs_review = False
    flagged_skills = []

    for s in skills:
        status, reason = evaluator.evaluate(
            confidence=s.get("confidence", 0.0),
            match_method=s.get("match_method", "none"),
        )
        if status == ReviewStatusSchema.PENDING:
            needs_review = True
            # Routing rule: any PENDING/low-confidence/out-of-taxonomy skill needs LLM assistance
            needs_ollama = True
            flagged_skills.append(
                {
                    "raw_skill": s.get("raw_skill"),
                    "normalized_skill": s.get("normalized_skill"),
                    "esco_id": s.get("esco_id"),
                    "confidence": s.get("confidence"),
                    "reason": reason,
                    "status": "pending",
                }
            )

    duration_ms = (time.perf_counter() - start_time) * 1000.0

    return {
        "review_result": {
            "needs_ollama": needs_ollama,
            "needs_review": needs_review,
            "flagged_skills": flagged_skills,
        },
        "execution_metadata": {
            "review_eval_duration_ms": duration_ms,
            "needs_ollama": needs_ollama,
            "needs_review": needs_review,
        },
    }
