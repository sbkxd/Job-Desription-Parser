"""Pydantic schemas for Pipeline Orchestration (Milestone 7.1)."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PipelineRequest(BaseModel):
    """Payload for triggering the job description parser pipeline."""

    url: Optional[str] = Field(
        default=None, description="The URL of the job description to fetch."
    )
    pdf_path: Optional[str] = Field(
        default=None, description="The local path to a PDF job description."
    )


class PipelineStageResult(BaseModel):
    """Result of an individual execution stage of the pipeline."""

    stage: str
    status: str
    duration_ms: float
    data: Dict[str, Any] = Field(default_factory=dict)


class PipelineResult(BaseModel):
    """E2E result from a complete parser pipeline execution."""

    success: bool
    job_id: Optional[str] = None
    ingestion: Dict[str, Any] = Field(default_factory=dict)
    segmentation: Dict[str, Any] = Field(default_factory=dict)
    extraction: Dict[str, Any] = Field(default_factory=dict)
    normalization: Dict[str, Any] = Field(default_factory=dict)
    review: Dict[str, Any] = Field(default_factory=dict)
    ollama: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    execution_metadata: Dict[str, Any] = Field(default_factory=dict)


class OllamaResolution(BaseModel):
    """Structuring the schema of local LLM resolution outputs."""

    selected_skill: str
    reason: str
    confidence: float


class MCPResponse(BaseModel):
    """Response returned by Model Context Protocol tools execution."""

    tool: str
    success: bool
    output: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
