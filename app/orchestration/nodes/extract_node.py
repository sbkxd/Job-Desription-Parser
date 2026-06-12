"""LangGraph node for running information extraction (NER and attribute parsing)."""

import time
from typing import Any, Dict

from app.extraction.services.extraction_service import ExtractionService
from app.orchestration.state.state import PipelineState


async def extract_node(state: PipelineState) -> Dict[str, Any]:
    """Extract skills, experience, seniority, and requirements from sections.

    Args:
        state: The current PipelineState.

    Returns:
        State updates containing extraction_result, errors, and execution_metadata.
    """
    start_time = time.perf_counter()
    segmented_document = state.get("segmented_document") or {}

    errors = []
    extraction_result = {}

    try:
        service = ExtractionService()
        res = service.extract(segmented_document)

        if not res.success:
            raise RuntimeError(res.error or "Extraction failed.")

        # Serialize ExtractionResult to standard dictionary
        extraction_result = {
            "skills": [
                {"name": s.name, "confidence": s.confidence} for s in res.skills
            ],
            "experience": {
                "min_years": res.experience.min_years,
                "max_years": res.experience.max_years,
            },
            "seniority": res.seniority.seniority if res.seniority else "",
            "requirements": [
                {
                    "text": r.text,
                    "classification": r.classification,
                    "confidence": r.confidence,
                }
                for r in res.requirements_classification
            ],
        }
    except Exception as e:
        errors.append(f"Extraction failed: {str(e)}")

    duration_ms = (time.perf_counter() - start_time) * 1000.0

    return {
        "extraction_result": extraction_result,
        "errors": errors,
        "execution_metadata": {
            "extraction_duration_ms": duration_ms,
            "node_extract_success": len(errors) == 0,
        },
    }
