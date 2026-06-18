"""Unit tests for Resume Ingestion, Extraction, Normalization, and API endpoints."""

import json
import os
from unittest import mock
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.resume.extraction.extractor import ResumeExtractor
from app.resume.ingestion.parser import ResumeParser
from app.resume.schemas.schemas import ResumeIntelligenceReport
from app.resume.services.service import ResumeService

client = TestClient(app)


@pytest.fixture
def student_resume_data():
    """Load mock student resume JSON fixture data."""
    fixture_path = os.path.join(
        os.path.dirname(__file__), "..", "fixtures", "resume", "student_resume.json"
    )
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_resume_parser(tmp_path):
    """Verify that ResumeParser correctly extracts text from PDF by mocking pdfminer."""
    temp_pdf = tmp_path / "resume.pdf"
    temp_pdf.write_bytes(b"%PDF-1.4 mock content")

    with patch("pdfminer.high_level.extract_text", return_value="Mocked Resume Text"):
        parser = ResumeParser()
        text = parser.parse(str(temp_pdf))
        assert text == "Mocked Resume Text"


@pytest.mark.asyncio
async def test_resume_extractor(student_resume_data):
    """Verify that ResumeExtractor calls MistralClient and parses to schema."""
    mock_report = ResumeIntelligenceReport(**student_resume_data)

    mock_client = mock.MagicMock()
    mock_client.generate_structured = AsyncMock(return_value=mock_report)

    extractor = ResumeExtractor(client=mock_client)
    report = await extractor.extract("Mock Resume Text")

    assert report.candidate_profile.candidate_name == "Jane Student"
    assert len(report.skills) == 2
    assert report.skills[0].raw_skill == "Python"
    mock_client.generate_structured.assert_called_once()


@pytest.mark.asyncio
async def test_resume_service(student_resume_data):
    """Verify the coordinated ResumeService ingestion, extraction, and normalization flow."""
    mock_report = ResumeIntelligenceReport(**student_resume_data)

    mock_parser = mock.MagicMock()
    mock_parser.parse.return_value = "Jane Student Resume Text"

    mock_extractor = mock.MagicMock()
    mock_extractor.extract = AsyncMock(return_value=mock_report)

    # Mock SkillNormalizationService
    mock_normalized_skills = [
        mock.MagicMock(
            raw_skill="Python",
            normalized_skill="Python",
            esco_id="esco_python",
            confidence=1.0,
        ),
        mock.MagicMock(
            raw_skill="Java",
            normalized_skill="Java",
            esco_id="esco_java",
            confidence=1.0,
        ),
    ]
    mock_norm_result = mock.MagicMock()
    mock_norm_result.normalized_skills = mock_normalized_skills

    mock_normalizer = mock.MagicMock()
    mock_normalizer.normalize.return_value = mock_norm_result

    service = ResumeService(
        parser=mock_parser, extractor=mock_extractor, normalizer=mock_normalizer
    )

    report = await service.analyze_resume("dummy_path.pdf")

    assert report.candidate_profile.candidate_name == "Jane Student"
    assert report.skills[0].normalized_skill == "Python"
    assert report.skills[0].confidence == 1.0
    mock_parser.parse.assert_called_once_with("dummy_path.pdf")
    mock_extractor.extract.assert_called_once_with("Jane Student Resume Text")
    mock_normalizer.normalize.assert_called_once_with(["Python", "Java"])


@pytest.mark.asyncio
async def test_resume_analyze_endpoint(student_resume_data):
    """Verify that POST /resume/analyze uploads file and returns Report."""
    mock_report = ResumeIntelligenceReport(**student_resume_data)

    with patch(
        "app.api.v1.endpoints.resume_api.ResumeService.analyze_resume",
        new_callable=AsyncMock,
        return_value=mock_report,
    ):
        # Create a mock file payload
        file_payload = {
            "file": ("resume.pdf", b"%PDF-1.4 mock content", "application/pdf")
        }

        # Test endpoint /resume/analyze
        response = client.post("/resume/analyze", files=file_payload)
        assert response.status_code == 200

        data = response.json()
        assert "candidate_profile" in data
        assert data["candidate_profile"]["candidate_name"] == "Jane Student"
        assert len(data["skills"]) == 2

        # Test endpoint /api/v1/resume/analyze
        # Reset file seek for second post
        file_payload = {
            "file": ("resume.pdf", b"%PDF-1.4 mock content", "application/pdf")
        }
        response_v1 = client.post("/api/v1/resume/analyze", files=file_payload)
        assert response_v1.status_code == 200
        assert (
            response_v1.json()["candidate_profile"]["candidate_name"] == "Jane Student"
        )
