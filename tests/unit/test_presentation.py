"""Unit tests for presentation layer formatter, schemas, and endpoints."""

import uuid
from typing import Any, Dict
from unittest import mock
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.database.session import get_db_session
from app.main import app
from app.presentation.formatters.job_intelligence_formatter import (
    JobIntelligenceFormatter,
)
from app.presentation.formatters.response_builder import ResponseBuilder
from app.presentation.schemas.job_intelligence import JobIntelligenceReport

client = TestClient(app)


@pytest.fixture
def mock_pipeline_state() -> Dict[str, Any]:
    """Return a mock final PipelineState dictionary."""
    return {
        "job_source": {
            "title": "Senior Python Developer",
            "company": "Tech Corp",
            "location": "Remote",
            "source_type": "greenhouse",
            "url": "https://boards.greenhouse.io/techcorp/jobs/123",
        },
        "raw_document": "Python Developer job description text",
        "segmented_document": {
            "responsibilities": [
                "Build scalable backend services",
                "Equal opportunity employer.",  # Should be filtered out
            ],
            "nice_to_have": [
                "Experience with PyTorch is a plus",
            ],
        },
        "extraction_result": {
            "seniority": "Senior",
            "experience": {"min_years": 5, "max_years": None},
            "requirements": [
                {"text": "Bachelor's degree in CS", "classification": "Required"},
                {"text": "AWS Certification", "classification": "Preferred"},
            ],
        },
        "normalization_result": {
            "skills": [
                {
                    "raw_skill": "Python",
                    "normalized_skill": "Python",
                    "esco_id": "esco_python",
                    "confidence": 1.0,
                    "match_method": "exact",
                },
                {
                    "raw_skill": "PyTorch",
                    "normalized_skill": "PyTorch",
                    "esco_id": "esco_pytorch",
                    "confidence": 0.95,
                    "match_method": "fuzzy",
                },
            ]
        },
        "review_result": {
            "needs_review": True,
            "flagged_skills": [
                {
                    "raw_skill": "PyTorch",
                    "normalized_skill": "PyTorch",
                    "confidence": 0.45,
                    "reason": "Low confidence match",
                }
            ],
        },
    }


def test_job_intelligence_formatter(mock_pipeline_state):
    """Verify that JobIntelligenceFormatter maps pipeline state to report correctly."""
    report = JobIntelligenceFormatter.format(mock_pipeline_state)
    assert isinstance(report, JobIntelligenceReport)

    # Job info
    assert report.job_information.job_title == "Senior Python Developer"
    assert report.job_information.company == "Tech Corp"
    assert report.job_information.location == "Remote"
    assert (
        report.job_information.source_url
        == "https://boards.greenhouse.io/techcorp/jobs/123"
    )

    # Role Profile
    assert report.role_profile.seniority == "Senior"
    assert report.role_profile.minimum_experience_years == 5.0
    assert report.role_profile.maximum_experience_years is None

    # Responsibilities (boilerplate filtered out)
    assert "Build scalable backend services" in report.responsibilities
    assert "Equal opportunity employer." not in report.responsibilities

    # Education & Qualifications
    assert "Bachelor's degree in CS" in report.education_requirements
    assert "AWS Certification" in report.qualifications

    # Skills categorization
    assert "Python" in report.skills.required
    assert "PyTorch" in report.skills.preferred  # Because it matches nice_to_have check
    assert "Python" in report.skills.normalized

    # Technology Stack (alphabetical)
    assert report.technology_stack == ["PyTorch", "Python"]

    # Review Summary
    assert report.review_summary.review_required is True
    assert "PyTorch" in report.review_summary.flagged_skills
    assert (
        "PyTorch (confidence: 0.45, reason: Low confidence match)"
        in report.review_summary.low_confidence_items
    )


def test_response_builder(mock_pipeline_state):
    """Verify ResponseBuilder maps correctly."""
    report = ResponseBuilder.build_report(mock_pipeline_state)
    assert report.job_information.job_title == "Senior Python Developer"


@pytest.mark.asyncio
async def test_pipeline_run_endpoints_return_report(mock_pipeline_state):
    """Verify endpoint /run/url returns JobIntelligenceReport schema."""
    with patch(
        "app.api.v1.endpoints.pipeline.PipelineService.run_pipeline",
        new_callable=AsyncMock,
        return_value=mock_pipeline_state,
    ):
        response = client.post(
            "/api/v1/pipeline/run/url", json={"url": "https://example.com/job"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "job_information" in data
        assert "role_profile" in data
        assert "skills" in data
        assert data["job_information"]["job_title"] == "Senior Python Developer"
        assert "execution_metadata" not in data  # Assert internal metadata is stripped!


@pytest.mark.asyncio
async def test_pipeline_debug_endpoint():
    """Verify pipeline debug endpoint returns full pipeline state."""
    job_id = uuid.uuid4()
    mock_run = mock.MagicMock()
    mock_run.pipeline_state = {
        "raw_document": "Clean raw document",
        "execution_metadata": {"t": 1.0},
    }

    mock_db = mock.AsyncMock()
    mock_result = mock.MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_run
    mock_db.execute.return_value = mock_result

    app.dependency_overrides[get_db_session] = lambda: mock_db
    try:
        response = client.get(f"/api/v1/pipeline/debug/{job_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["raw_document"] == "Clean raw document"
        assert "execution_metadata" in data
    finally:
        app.dependency_overrides.clear()
