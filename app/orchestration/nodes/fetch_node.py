"""LangGraph node for fetching job description content from URLs or PDF files."""

import time
from typing import Any, Dict

from app.orchestration.mcp.fetch_jd import FetchJDTool
from app.orchestration.state.state import PipelineState


async def fetch_jd_node(state: PipelineState) -> Dict[str, Any]:
    """Ingest raw job description content and populate state.

    Args:
        state: The current PipelineState.

    Returns:
        State updates containing raw_document, errors, and execution_metadata.
    """
    start_time = time.perf_counter()
    source = state.get("job_source") or {}
    url = source.get("url")
    pdf_path = source.get("pdf_path")

    errors = []
    raw_document = ""
    metadata = {}

    try:
        tool = FetchJDTool()
        result = await tool.execute(url=url, pdf_path=pdf_path)
        raw_document = result.get("raw_text", "")
        metadata = result.get("metadata", {})
    except Exception as e:
        errors.append(f"Ingestion failed: {str(e)}")

    duration_ms = (time.perf_counter() - start_time) * 1000.0

    return {
        "raw_document": raw_document,
        "job_source": {**source, **metadata},
        "errors": errors,
        "execution_metadata": {
            "fetch_duration_ms": duration_ms,
            "node_fetch_success": len(errors) == 0,
        },
    }
