"""Unit tests for the Mistral Resume Recommendations & Optimization Engine."""

import json
import os
from unittest import mock
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.presentation.schemas.job_intelligence import JobIntelligenceReport
from app.recommendations.schemas.schemas import (
    MistralRecommendationsResponse,
    ResumeOptimizationReport,
)
from app.recommendations.services.service import RecommendationService
from app.resume.schemas.schemas import ResumeIntelligenceReport

client = TestClient(app)


@pytest.fixture
def student_resume():
    """Load mock student resume JSON fixture."""
    fixture_path = os.path.join(
        os.path.dirname(__file__), "..", "fixtures", "resume", "student_resume.json"
    )
    with open(fixture_path, "r", encoding="utf-8") as f:
        return ResumeIntelligenceReport(**json.load(f))


@pytest.fixture
def mock_job_report():
    """Return a mock JobIntelligenceReport."""
    return JobIntelligenceReport(
        job_information={
            "job_title": "Junior Python Developer",
            "company": "Tech Innovators",
            "location": "Remote",
            "source_type": "generic",
            "source_url": "https://example.com/job",
        },
        role_profile={
            "seniority": "Junior",
            "minimum_experience_years": 1.0,
            "maximum_experience_years": None,
        },
        skills={
            "required": ["Python", "Flask"],
            "preferred": ["SQL", "Docker"],
            "normalized": ["Python", "Flask", "SQL", "Docker"],
        },
        education_requirements=[
            "Bachelor's degree in Computer Science or related fields."
        ],
        responsibilities=[
            "Write scalable Python services",
            "Maintain API integrations",
        ],
        qualifications=["Bachelor's Degree", "AWS Cloud Practitioner"],
        technology_stack=["Python", "Flask", "Docker"],
        review_summary={
            "review_required": False,
            "flagged_skills": [],
            "low_confidence_items": [],
        },
    )


@pytest.mark.asyncio
async def test_recommendation_service(student_resume, mock_job_report):
    """Verify that RecommendationService calls Mistral and returns a structured report."""
    mock_mistral = mock.MagicMock()
    mock_mistral_response = MistralRecommendationsResponse(
        resume_improvements=[
            {
                "type": "MISSING_SKILL",
                "section": "Skills",
                "message": "Add Flask if you have it.",
            }
        ],
        ats_recommendations=[
            {
                "keyword": "Flask",
                "coverage_status": "MISSING",
                "recommendation": "Mention Flask.",
            }
        ],
        tailored_summary="Jane is an eager student TA with Python skills.",
        application_readiness_score=80,
        application_readiness_recommendation="Ready to apply.",
    )
    mock_mistral.generate_structured = AsyncMock(return_value=mock_mistral_response)

    service = RecommendationService(mistral_client=mock_mistral)
    report = await service.generate_recommendations(student_resume, mock_job_report)

    assert isinstance(report, ResumeOptimizationReport)
    assert report.compatibility_score > 0
    assert report.application_readiness_score == 80
    assert report.tailored_summary == "Jane is an eager student TA with Python skills."
    assert len(report.resume_improvements) == 1
    assert report.resume_improvements[0].type == "MISSING_SKILL"
    mock_mistral.generate_structured.assert_called_once()


@pytest.mark.asyncio
async def test_generate_recommendations_endpoint(student_resume, mock_job_report):
    """Verify that POST /resume/recommendations endpoint returns ResumeOptimizationReport."""
    mock_report = ResumeOptimizationReport(
        compatibility_score=82,
        matched_skills=["Python"],
        missing_skills=["Flask"],
        critical_gaps=[],
        strengths=["Strong education"],
        resume_improvements=[
            {
                "type": "MISSING_SKILL",
                "section": "Skills",
                "message": "Add Flask if you have it.",
            }
        ],
        ats_recommendations=[
            {
                "keyword": "Flask",
                "coverage_status": "MISSING",
                "recommendation": "Mention Flask.",
            }
        ],
        application_readiness_score=78,
        application_readiness_recommendation="Solid profile.",
        tailored_summary="Grounded summary here.",
    )

    with patch(
        "app.api.v1.endpoints.recommendations_api.RecommendationService.generate_recommendations",
        new_callable=AsyncMock,
        return_value=mock_report,
    ):
        payload = {
            "resume": student_resume.model_dump(),
            "job": mock_job_report.model_dump(),
        }

        # Test root endpoint
        response = client.post("/resume/recommendations", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["compatibility_score"] == 82
        assert data["application_readiness_score"] == 78
        assert data["tailored_summary"] == "Grounded summary here."

        # Test api/v1 endpoint
        response_v1 = client.post("/api/v1/resume/recommendations", json=payload)
        assert response_v1.status_code == 200
        assert response_v1.json()["compatibility_score"] == 82
