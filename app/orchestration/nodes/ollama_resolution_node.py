"""LangGraph node for running Ollama-based fallback resolution on flagged skills."""

import re
import time
from typing import Any, Dict, List

from app.orchestration.ollama.qwen_adapter import QwenAdapter
from app.orchestration.state.state import PipelineState


def _get_skill_context(raw_doc: str, skill: str) -> str:
    """Helper to extract a sentence or context snippet containing the skill name."""
    if not raw_doc or not skill:
        return ""

    # Search case-insensitively with word boundaries
    pattern = re.compile(rf"([^.?!]*\b{re.escape(skill)}\b[^.?!]*)", re.IGNORECASE)
    match = pattern.search(raw_doc)
    if match:
        return match.group(1).strip()

    # Fallback: slice a window
    idx = raw_doc.lower().find(skill.lower())
    if idx != -1:
        start = max(0, idx - 100)
        end = min(len(raw_doc), idx + 100 + len(skill))
        return raw_doc[start:end].strip()

    return ""


async def ollama_resolution_node(state: PipelineState) -> Dict[str, Any]:
    """Resolve low-confidence and out-of-taxonomy skills using the local Ollama LLM.

    Args:
        state: The current PipelineState.

    Returns:
        State updates containing ollama_result and execution_metadata.
    """
    start_time = time.perf_counter()
    raw_doc = state.get("raw_document") or ""
    review_res = state.get("review_result") or {}
    flagged_skills = review_res.get("flagged_skills") or []

    adapter = QwenAdapter()
    resolutions: List[Dict[str, Any]] = []

    for fs in flagged_skills:
        skill_name = fs.get("raw_skill", "")
        reason = fs.get("reason", "")
        context = _get_skill_context(raw_doc, skill_name)

        resolution_item = {
            "raw_skill": skill_name,
            "reason": reason,
            "context": context,
        }

        try:
            if reason == "OUT_OF_TAXONOMY":
                # Out of taxonomy fallback classification
                res = await adapter.assist_review(
                    skill=skill_name, context=context, review_reason=reason
                )
                resolution_item["category"] = res.get("category", "Custom Skill")
                resolution_item["suggested_confidence"] = res.get("confidence", 0.5)
            else:
                # Ambiguous taxonomy candidate resolution
                # Pass raw skill name as fallback candidate
                candidates = [fs.get("normalized_skill") or skill_name]
                res = await adapter.resolve_ambiguous_skill(
                    skill=skill_name, context=context, candidates=candidates
                )
                resolution_item["recommended_match"] = res.get(
                    "selected_skill"
                ) or fs.get("normalized_skill")
                resolution_item["resolution_reason"] = res.get(
                    "reason", "LLM fallback matching"
                )
        except Exception as e:
            # Non-blocking: record error inside resolution item and proceed
            resolution_item["error"] = str(e)

        resolutions.append(resolution_item)

    duration_ms = (time.perf_counter() - start_time) * 1000.0

    return {
        "ollama_result": {
            "resolutions": resolutions,
        },
        "execution_metadata": {
            "ollama_resolution_duration_ms": duration_ms,
        },
    }
