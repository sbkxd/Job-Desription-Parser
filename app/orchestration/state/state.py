"""State definition for the LangGraph-based job description parser pipeline."""

from typing import Annotated, Any, Dict, List, TypedDict


def append_list(left: List[Any], right: List[Any]) -> List[Any]:
    """Reducer to append items to a list in PipelineState."""
    return (left or []) + (right or [])


def update_dict(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    """Reducer to merge dictionary items in PipelineState."""
    new_dict = dict(left or {})
    new_dict.update(right or {})
    return new_dict


class PipelineState(TypedDict):
    """The central state carried through the LangGraph pipeline execution."""

    job_source: Dict[str, Any]
    """Source information (e.g., url, pdf_path, source platform, etc.)."""

    raw_document: str
    """The cleaned raw text content of the job description."""

    segmented_document: Dict[str, List[str]]
    """Text lines grouped by SectionType (responsibilities, requirements, etc.)."""

    extraction_result: Dict[str, Any]
    """Extracted raw attributes: skills, experience range, seniority, requirements."""

    normalization_result: Dict[str, Any]
    """Canonical ESCO normalized mapping and scores."""

    review_result: Dict[str, Any]
    """Flagged validation results: confidence status, review reason, needs_ollama/review flags."""

    mistral_result: Dict[str, Any]
    """Fallback LLM-based disambiguation and resolution suggestions."""

    db: Any
    """Optional database session object (for sharing transactions across nodes)."""

    persistence_result: Dict[str, Any]
    """Output ID coordinates (job_id, skill_ids) from database storage."""

    errors: Annotated[List[str], append_list]
    """Aggregate log of all non-fatal pipeline errors encountered."""

    execution_metadata: Annotated[Dict[str, Any], update_dict]
    """Diagnostic tracking: execution durations per node, router choices, and steps."""
