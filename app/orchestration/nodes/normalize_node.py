"""LangGraph node for normalizing extracted skills to standard ESCO concepts."""

import time
from typing import Any, Dict

from app.normalization.services.normalization_service import SkillNormalizationService
from app.orchestration.state.state import PipelineState


async def normalize_node(state: PipelineState) -> Dict[str, Any]:
    """Normalize raw extracted skills to canonical ESCO taxonomy.

    Args:
        state: The current PipelineState.

    Returns:
        State updates containing normalization_result, errors, and execution_metadata.
    """
    start_time = time.perf_counter()
    extracted = state.get("extraction_result") or {}
    skills_data = extracted.get("skills") or []
    raw_skills = [s["name"] for s in skills_data if s.get("name")]

    errors = []
    normalization_result: dict[str, Any] = {"skills": []}

    try:
        if raw_skills:
            service = SkillNormalizationService()
            res = service.normalize(raw_skills)

            # Serialize NormalizationResult
            normalization_result = {
                "skills": [
                    {
                        "raw_skill": ns.raw_skill,
                        "normalized_skill": ns.normalized_skill,
                        "esco_id": ns.esco_id,
                        "confidence": ns.confidence,
                        "match_method": ns.match_method,
                    }
                    for ns in res.normalized_skills
                ]
            }
    except Exception as e:
        errors.append(f"Normalization failed: {str(e)}")

    duration_ms = (time.perf_counter() - start_time) * 1000.0

    return {
        "normalization_result": normalization_result,
        "errors": errors,
        "execution_metadata": {
            "normalization_duration_ms": duration_ms,
            "node_normalize_success": len(errors) == 0,
        },
    }
