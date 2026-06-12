"""E2E Integration tests for the LangGraph-based parsing pipeline."""

import uuid
from unittest import mock
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.database.session import get_db_session
from app.main import app
from app.orchestration.graph.pipeline_graph import build_pipeline_graph
from app.orchestration.routing.router import review_router

client = TestClient(app)


@pytest.fixture
def mock_db_session():
    mock_session = mock.AsyncMock()
    mock_session.add = mock.MagicMock()
    mock_session.flush = mock.AsyncMock()
    mock_session.execute = mock.AsyncMock()
    mock_session.commit = mock.AsyncMock()
    app.dependency_overrides[get_db_session] = lambda: mock_session
    yield mock_session
    app.dependency_overrides.clear()


def test_review_router_conditions() -> None:
    # 1. High confidence path -> persistence
    state_high = {
        "review_result": {
            "needs_mistral": False,
            "needs_review": False,
        }
    }
    assert review_router(state_high) == "persistence"

    # 2. Low confidence path -> mistral
    state_low = {
        "review_result": {
            "needs_mistral": True,
            "needs_review": True,
        }
    }
    assert review_router(state_low) == "mistral_resolution"


@pytest.mark.asyncio
async def test_full_graph_execution_success(mock_db_session) -> None:
    job_id = uuid.uuid4()
    initial_state = {
        "job_source": {
            "url": "https://example.com/job/software-dev",
            "job_id": str(job_id),
        },
        "raw_document": "",
        "segmented_document": {},
        "extraction_result": {},
        "normalization_result": {},
        "review_result": {},
        "mistral_result": {},
        "persistence_result": {},
        "errors": [],
        "execution_metadata": {},
        "db": mock_db_session,
    }

    # Mock all internal nodes inside the graph module where they are referenced during build
    with (
        patch(
            "app.orchestration.graph.pipeline_graph.fetch_jd_node",
            new_callable=mock.AsyncMock,
        ) as mock_fetch,
        patch(
            "app.orchestration.graph.pipeline_graph.segment_node",
            new_callable=mock.AsyncMock,
        ) as mock_segment,
        patch(
            "app.orchestration.graph.pipeline_graph.extract_node",
            new_callable=mock.AsyncMock,
        ) as mock_extract,
        patch(
            "app.orchestration.graph.pipeline_graph.normalize_node",
            new_callable=mock.AsyncMock,
        ) as mock_normalize,
        patch(
            "app.orchestration.graph.pipeline_graph.review_eval_node",
            new_callable=mock.AsyncMock,
        ) as mock_review_eval,
        patch(
            "app.orchestration.graph.pipeline_graph.persistence_node",
            new_callable=mock.AsyncMock,
        ) as mock_persistence,
    ):

        mock_fetch.return_value = {
            "raw_document": "Python Developer job text",
            "execution_metadata": {
                "fetch_duration_ms": 10.0,
                "node_fetch_success": True,
            },
        }
        mock_segment.return_value = {
            "segmented_document": {"requirements": ["Python Developer"]},
            "execution_metadata": {
                "segmentation_duration_ms": 10.0,
                "node_segment_success": True,
            },
        }
        mock_extract.return_value = {
            "extraction_result": {"skills": [{"name": "Python", "confidence": 1.0}]},
            "execution_metadata": {
                "extraction_duration_ms": 10.0,
                "node_extract_success": True,
            },
        }
        mock_normalize.return_value = {
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
            "execution_metadata": {
                "normalization_duration_ms": 10.0,
                "node_normalize_success": True,
            },
        }
        mock_review_eval.return_value = {
            "review_result": {"needs_mistral": False, "needs_review": False},
            "execution_metadata": {
                "review_eval_duration_ms": 5.0,
                "needs_mistral": False,
                "needs_review": False,
            },
        }
        mock_persistence.return_value = {
            "persistence_result": {"job_id": str(job_id), "skill_ids": ["skill-uuid"]},
            "execution_metadata": {
                "persistence_duration_ms": 10.0,
                "node_persist_success": True,
            },
        }

        # Build graph dynamically within mock context to use mock functions
        graph = build_pipeline_graph().compile()
        result = await graph.ainvoke(initial_state)

        assert result["persistence_result"]["job_id"] == str(job_id)
        assert len(result["errors"]) == 0
        mock_fetch.assert_called_once()
        mock_persistence.assert_called_once()


def test_api_pipeline_endpoints(mock_db_session) -> None:
    job_id = uuid.uuid4()
    mock_final_state = {
        "job_source": {
            "url": "https://example.com/job/software-dev",
            "job_id": str(job_id),
        },
        "raw_document": "Python Developer job text",
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
        "review_result": {"needs_mistral": False, "needs_review": False},
        "persistence_result": {"job_id": str(job_id), "skill_ids": ["skill-uuid"]},
        "errors": [],
        "execution_metadata": {
            "fetch_duration_ms": 10.0,
            "node_fetch_success": True,
            "segmentation_duration_ms": 10.0,
            "node_segment_success": True,
            "extraction_duration_ms": 10.0,
            "node_extract_success": True,
            "normalization_duration_ms": 10.0,
            "node_normalize_success": True,
            "review_eval_duration_ms": 5.0,
            "persistence_duration_ms": 10.0,
            "node_persist_success": True,
        },
    }

    with patch(
        "app.api.v1.endpoints.pipeline.PipelineService.run_pipeline",
        new_callable=mock.AsyncMock,
        return_value=mock_final_state,
    ):
        # 1. Test /run/url
        response = client.post(
            "/api/v1/pipeline/run/url",
            json={"url": "https://example.com/job/software-dev"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "job_information" in data
        assert "skills" in data
        assert (
            data["job_information"]["source_url"]
            == "https://example.com/job/software-dev"
        )
        assert "success" not in data

        # 2. Test /run/pdf
        response_pdf = client.post(
            "/api/v1/pipeline/run/pdf",
            json={"pdf_path": "C:/Users/USER/Downloads/sample-job-description.pdf"},
        )
        assert response_pdf.status_code == 200
        data_pdf = response_pdf.json()
        assert "job_information" in data_pdf
        assert "skills" in data_pdf
        assert "success" not in data_pdf
