"""LangGraph node for preparing and creating review queue records."""

import json
import time
from typing import Any, Dict

from app.models.models import ReviewStatus
from app.orchestration.state.state import PipelineState


async def review_queue_node(state: PipelineState) -> Dict[str, Any]:
    """Prepare and record the review queue details, merging Ollama suggestions.

    Args:
        state: The current PipelineState.

    Returns:
        State updates containing review_result and execution_metadata.
    """
    start_time = time.perf_counter()
    review_res = state.get("review_result") or {}
    flagged_skills = list(review_res.get("flagged_skills") or [])
    mistral_res = state.get("mistral_result") or {}
    resolutions = mistral_res.get("resolutions") or []

    # Map resolutions by raw skill name for fast matching
    resolutions_map = {r["raw_skill"].lower(): r for r in resolutions}

    # Merge Ollama suggestions into the flagged reasons list
    merged_skills = []
    for fs in flagged_skills:
        raw_name = fs.get("raw_skill", "")
        item = dict(fs)
        res_info = resolutions_map.get(raw_name.lower())
        if res_info:
            if "recommended_match" in res_info:
                item["suggested_match"] = res_info["recommended_match"]
                item["resolution_reason"] = res_info.get("resolution_reason")
            if "category" in res_info:
                item["suggested_category"] = res_info["category"]
                item["suggested_confidence"] = res_info.get("suggested_confidence")
        merged_skills.append(item)

    # Prepare serialized review queue metadata
    flagged_reasons_str = json.dumps({"skills": merged_skills})

    duration_ms = (time.perf_counter() - start_time) * 1000.0

    return {
        "review_result": {
            **review_res,
            "flagged_skills": merged_skills,
            "flagged_reasons": flagged_reasons_str,
            "status": ReviewStatus.PENDING.value,
        },
        "execution_metadata": {
            "review_queue_duration_ms": duration_ms,
        },
    }
