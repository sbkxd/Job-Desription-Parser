"""Unit tests for Pipeline Schemas (Milestone 7.1)."""

from app.orchestration.schemas.schemas import (
    MCPResponse,
    MistralResolution,
    PipelinePdfRequest,
    PipelineResult,
    PipelineStageResult,
    PipelineUrlRequest,
)


def test_pipeline_request_validation() -> None:
    # 1. Valid URL
    req = PipelineUrlRequest(url="https://example.com/job")
    assert req.url == "https://example.com/job"

    # 2. Valid PDF
    req2 = PipelinePdfRequest(pdf_path="/path/to/jd.pdf")
    assert req2.pdf_path == "/path/to/jd.pdf"


def test_pipeline_stage_result() -> None:
    res = PipelineStageResult(
        stage="fetch",
        status="success",
        duration_ms=120.5,
        data={"some": "metadata"},
    )
    assert res.stage == "fetch"
    assert res.status == "success"
    assert res.duration_ms == 120.5
    assert res.data == {"some": "metadata"}


def test_pipeline_result_serialization() -> None:
    res = PipelineResult(
        success=True,
        job_id="test-job-uuid",
        ingestion={"status": "success"},
        segmentation={"status": "success"},
    )
    assert res.success is True
    assert res.job_id == "test-job-uuid"
    assert res.ingestion == {"status": "success"}
    assert res.segmentation == {"status": "success"}
    assert res.extraction == {}


def test_mistral_resolution() -> None:
    res = MistralResolution(
        selected_skill="Apache Spark",
        reason="Matches context",
        confidence=0.95,
    )
    assert res.selected_skill == "Apache Spark"
    assert res.confidence == 0.95


def test_mcp_response() -> None:
    res = MCPResponse(tool="fetch_jd", success=True, output={"foo": "bar"})
    assert res.tool == "fetch_jd"
    assert res.success is True
    assert res.output == {"foo": "bar"}
