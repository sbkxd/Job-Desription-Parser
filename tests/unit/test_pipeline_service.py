"""Unit tests for PipelineService and LangGraph execution logs (Milestone 7.11, 7.12, 7.18)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.orchestration.services.pipeline_service import PipelineService


@pytest.mark.asyncio
async def test_pipeline_service_run_success() -> None:
    # 1. Mock DB Session
    mock_session = MagicMock(spec=AsyncSession)
    mock_session.add = MagicMock()
    mock_session.flush = AsyncMock()

    service = PipelineService(mock_session)

    # 2. Mock workflow_graph.ainvoke
    mock_final_state = {
        "job_source": {
            "url": "https://example.com/job",
            "job_id": "test-job-uuid",
        },
        "raw_document": "Python Developer job description content.",
        "segmented_document": {"requirements": ["Python Developer"]},
        "extraction_result": {"skills": [{"name": "Python", "confidence": 1.0}]},
        "normalization_result": {
            "skills": [
                {
                    "raw_skill": "Python",
                    "normalized_skill": "Python",
                    "esco_id": "esco_python",
                    "confidence": 1.0,
                    "match_method": "exact",
                }
            ]
        },
        "review_result": {
            "needs_ollama": False,
            "needs_review": False,
            "flagged_skills": [],
        },
        "persistence_result": {
            "job_id": "test-job-uuid",
            "skill_ids": ["test-skill-uuid"],
        },
        "errors": [],
        "execution_metadata": {
            "fetch_duration_ms": 50.0,
            "node_fetch_success": True,
            "segmentation_duration_ms": 40.0,
            "node_segment_success": True,
            "extraction_duration_ms": 60.0,
            "node_extract_success": True,
            "normalization_duration_ms": 80.0,
            "node_normalize_success": True,
            "review_eval_duration_ms": 10.0,
            "persistence_duration_ms": 30.0,
            "node_persist_success": True,
        },
    }

    with patch(
        "app.orchestration.services.pipeline_service.workflow_graph.ainvoke",
        new_callable=AsyncMock,
        return_value=mock_final_state,
    ) as mock_invoke:

        res = await service.run_pipeline(url="https://example.com/job")

        assert res["persistence_result"]["job_id"] == "test-job-uuid"
        assert len(res["errors"]) == 0

        # Check mock calls
        mock_invoke.assert_called_once()
        assert mock_session.add.call_count > 1  # ProcessingRun and PipelineEvents
        assert mock_session.flush.call_count >= 2
