"""Unit tests for standard MCP Tools (Milestone 7.14 to 7.17)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.normalization.schemas.schemas import NormalizationResult, NormalizedSkill
from app.orchestration.mcp.fetch_jd import FetchJDTool
from app.orchestration.mcp.lookup_taxonomy import LookupTaxonomyTool
from app.orchestration.mcp.run_ner import RunNERTool
from app.orchestration.mcp.save_parsed_jd import SaveParsedJDTool


@pytest.mark.asyncio
async def test_fetch_jd_tool_url() -> None:
    tool = FetchJDTool()
    url = "https://boards.greenhouse.io/test/job"

    # Mock the playwright fetcher
    with (
        patch(
            "app.orchestration.mcp.fetch_jd.PlaywrightFetcher.fetch",
            new_callable=AsyncMock,
        ) as mock_fetch,
        patch("app.orchestration.mcp.fetch_jd.TrafilaturaParser.parse") as mock_parse,
    ):

        mock_fetch.return_value = MagicMock(
            html="<html>test</html>", status_code=200, error=None, duration_ms=10.0
        )
        mock_parse.return_value = MagicMock(
            success=True, title="Test Job", word_count=50, raw_text="Extracted text"
        )

        res = await tool.execute(url=url)
        assert res["raw_text"] == "Extracted text"
        assert res["metadata"]["title"] == "Test Job"


@pytest.mark.asyncio
async def test_run_ner_tool() -> None:
    tool = RunNERTool()
    text = "Must have 3 years Python and Django experience."

    with patch(
        "app.orchestration.mcp.run_ner.ExtractionService.extract"
    ) as mock_extract:
        mock_res = MagicMock()
        mock_res.success = True

        skill_mock = MagicMock()
        skill_mock.name = "Python"
        skill_mock.confidence = 1.0
        mock_res.skills = [skill_mock]

        mock_res.experience = MagicMock(
            min_years=3.0, max_years=None, description="3 years"
        )

        seniority_mock = MagicMock()
        seniority_mock.seniority = "Mid"
        mock_res.seniority = seniority_mock

        mock_res.requirements_classification = []

        mock_extract.return_value = mock_res

        res = await tool.execute(text=text, section="requirements")
        assert len(res["skills"]) == 1
        assert res["skills"][0]["name"] == "Python"
        assert res["experience"]["min_years"] == 3.0
        assert res["seniority"] == "Mid"


@pytest.mark.asyncio
async def test_lookup_taxonomy_tool() -> None:
    tool = LookupTaxonomyTool()

    with patch(
        "app.orchestration.mcp.lookup_taxonomy.SkillNormalizationService.normalize"
    ) as mock_normalize:
        mock_res = NormalizationResult(
            normalized_skills=[
                NormalizedSkill(
                    raw_skill="PySpark",
                    normalized_skill="Apache Spark",
                    esco_id="esco_spark",
                    confidence=0.92,
                    match_method="alias",
                )
            ]
        )
        mock_normalize.return_value = mock_res

        res = await tool.execute(skill="PySpark")
        assert res["normalized_skill"] == "Apache Spark"
        assert res["esco_id"] == "esco_spark"
        assert res["confidence"] == 0.92


@pytest.mark.asyncio
async def test_save_parsed_jd_tool() -> None:
    tool = SaveParsedJDTool()

    # Mock the SQLAlchemy async session execution and transaction commits
    mock_session = MagicMock()
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.flush = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.merge = AsyncMock()

    # Avoid AsyncMock return value issues by explicitly returning a MagicMock result
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute.return_value = mock_result

    with patch(
        "app.orchestration.mcp.save_parsed_jd.async_session_maker"
    ) as mock_maker:
        mock_maker.return_value.__aenter__.return_value = mock_session

        res = await tool.execute(
            title="Software Developer",
            raw_text="Job details...",
            skills=[{"raw_skill": "Python", "normalized_skill": "Python"}],
        )

        assert "job_id" in res
        assert res["skills_persisted"] == 1
        mock_session.commit.assert_called_once()
