"""LangGraph node for cleaning and segmenting job description text into sections."""

import time
from typing import Any, Dict

from app.ingestion.schemas import SourceType
from app.orchestration.state.state import PipelineState
from app.preprocessing.schemas.schemas import RawDocument
from app.preprocessing.services.segmentation_service import SegmentationService


async def segment_node(state: PipelineState) -> Dict[str, Any]:
    """Segment raw job description text into structural sections.

    Args:
        state: The current PipelineState.

    Returns:
        State updates containing segmented_document, errors, and execution_metadata.
    """
    start_time = time.perf_counter()
    raw_text = state.get("raw_document") or ""
    source = state.get("job_source") or {}

    errors = []
    segmented_document: dict[str, list[str]] = {
        "responsibilities": [],
        "requirements": [],
        "nice_to_have": [],
        "about_company": [],
        "benefits": [],
        "other": [],
    }

    try:
        raw_doc = RawDocument(
            raw_text=raw_text,
            source_type=SourceType(source.get("source_type", "unknown")),
            source_url=source.get("url"),
        )
        service = SegmentationService()
        res = service.segment(raw_doc)

        if not res.success or not res.document:
            raise RuntimeError(res.error or "Segmentation failed.")

        # Map list of section objects to dict[str, list[str]]
        for sec in res.document.sections:
            sec_type_str = sec.section_type.value
            if sec_type_str in segmented_document:
                segmented_document[sec_type_str].extend(sec.lines)
    except Exception as e:
        errors.append(f"Segmentation failed: {str(e)}")

    duration_ms = (time.perf_counter() - start_time) * 1000.0

    return {
        "segmented_document": segmented_document,
        "errors": errors,
        "execution_metadata": {
            "segmentation_duration_ms": duration_ms,
            "node_segment_success": len(errors) == 0,
        },
    }
