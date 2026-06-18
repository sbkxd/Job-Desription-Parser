"""Unit tests for the Job ↔ Resume Compatibility Engine."""

import json
import os
import uuid
from unittest import mock
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.compatibility.schemas.schemas import CompatibilityReport
from app.compatibility.scoring.scoring import CompatibilityEngine
from app.compatibility.services.service import CompatibilityService
from app.main import app
from app.presentation.schemas.job_intelligence import JobIntelligenceReport
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


def test_compatibility_engine(student_resume, mock_job_report):
    """Verify that CompatibilityEngine matches and scores accurately."""
    engine = CompatibilityEngine()
    report = engine.analyze(student_resume, mock_job_report)

    assert isinstance(report, CompatibilityReport)
    assert report.compatibility_score > 0
    # Jane Student has Python, TA TA experience 0.5 yrs, degree BS CS
    assert "Python" in report.skill_match.matched
    assert "Flask" in report.skill_match.missing
    assert report.experience_match.required == 1.0
    assert report.experience_match.candidate == 0.5
    assert report.experience_match.gap == 0.5
    assert report.education_match.matches is True  # BS CS meets BS CS requirement
    assert len(report.gap_analysis.moderate_gaps) > 0  # Missing Flask
    assert (
        len(report.strength_analysis.strong_matches) > 0
    )  # Meets education, has Python


@pytest.mark.asyncio
async def test_compatibility_service(student_resume, mock_job_report):
    """Verify CompatibilityService orchestrates the direct comparison successfully."""
    mock_engine = mock.MagicMock()
    mock_report = CompatibilityReport(
        compatibility_score=85,
        skill_match={"matched": ["Python"], "missing": [], "additional": []},
        experience_match={"required": 1.0, "candidate": 2.0, "gap": 0.0},
        education_match={
            "required_degree": "Bachelor",
            "candidate_degrees": ["Bachelor"],
            "matches": True,
        },
        gap_analysis={"critical_gaps": [], "moderate_gaps": [], "minor_gaps": []},
        strength_analysis={"strong_matches": ["Strong match"]},
    )
    mock_engine.analyze.return_value = mock_report

    service = CompatibilityService(engine=mock_engine)
    report = await service.analyze_compatibility(student_resume, mock_job_report)

    assert report.compatibility_score == 85
    mock_engine.analyze.assert_called_once_with(student_resume, mock_job_report)


@pytest.mark.asyncio
async def test_analyze_compatibility_endpoint(student_resume, mock_job_report):
    """Verify that POST /compatibility/analyze endpoint returns CompatibilityReport."""
    mock_report = CompatibilityReport(
        compatibility_score=80,
        skill_match={"matched": ["Python"], "missing": ["Flask"], "additional": []},
        experience_match={"required": 1.0, "candidate": 0.5, "gap": 0.5},
        education_match={
            "required_degree": "Bachelor's Degree",
            "candidate_degrees": ["Bachelor of Science"],
            "matches": True,
        },
        gap_analysis={"critical_gaps": [], "moderate_gaps": [], "minor_gaps": []},
        strength_analysis={"strong_matches": ["Strong education match"]},
    )

    with patch(
        "app.api.v1.endpoints.compatibility_api.CompatibilityService.analyze_compatibility",
        new_callable=AsyncMock,
        return_value=mock_report,
    ):
        payload = {
            "resume": student_resume.model_dump(),
            "job": mock_job_report.model_dump(),
        }
        response = client.post("/compatibility/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["compatibility_score"] == 80
        assert "skill_match" in data
        assert "gap_analysis" in data


@pytest.mark.asyncio
async def test_analyze_compatibility_pdf_endpoint(student_resume):
    """Verify that POST /compatibility/analyze-pdf works with resume PDF upload."""
    mock_report = CompatibilityReport(
        compatibility_score=75,
        skill_match={"matched": ["Python"], "missing": ["Flask"], "additional": []},
        experience_match={"required": 1.0, "candidate": 0.5, "gap": 0.5},
        education_match={
            "required_degree": "Bachelor's Degree",
            "candidate_degrees": ["Bachelor of Science"],
            "matches": True,
        },
        gap_analysis={"critical_gaps": [], "moderate_gaps": [], "minor_gaps": []},
        strength_analysis={"strong_matches": ["Strong education match"]},
    )

    with (
        patch(
            "app.api.v1.endpoints.compatibility_api.CompatibilityService.analyze_compatibility_by_job_id",
            new_callable=AsyncMock,
            return_value=mock_report,
        ),
        patch("builtins.open", mock.mock_open()),
        patch("os.makedirs"),
        patch("shutil.copyfileobj"),
    ):
        file_payload = {
            "resume_file": ("resume.pdf", b"%PDF-1.4 mock resume", "application/pdf")
        }
        data_payload = {"job_id": str(uuid.uuid4())}

        response = client.post(
            "/compatibility/analyze-pdf", files=file_payload, data=data_payload
        )
        assert response.status_code == 200
        assert response.json()["compatibility_score"] == 75
