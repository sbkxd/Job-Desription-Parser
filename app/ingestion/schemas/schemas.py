"""Ingestion domain schemas — data contracts for the entire pipeline."""

import enum
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class SourceType(str, enum.Enum):
    """Enumeration of supported ingestion source types."""

    NAUKRI = "naukri"
    FOUNDIT = "foundit"
    INDEED = "indeed"
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    WORKABLE = "workable"
    GENERIC_ATS = "generic_ats"
    PDF = "pdf"
    UNKNOWN = "unknown"


class FetchStatus(str, enum.Enum):
    """Terminal status of a fetch operation."""

    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
    BLOCKED = "blocked"


class DocumentMetadata(BaseModel):
    """Structured metadata attached to every fetched document."""

    platform: SourceType = SourceType.UNKNOWN
    http_status: int | None = None
    content_type: str | None = None
    fetch_duration_ms: float | None = None
    page_count: int | None = None  # PDF only
    word_count: int | None = None
    language: str | None = None
    og_title: str | None = None
    og_description: str | None = None
    og_image: str | None = None
    structured_data: dict[str, Any] = Field(default_factory=dict)
    extra: dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}


class FetchedDocument(BaseModel):
    """
    The canonical output object of the ingestion pipeline.

    Matches the required Phase 2 output contract:
        source_type, source_url, title, company, location, raw_text, metadata
    """

    source_type: SourceType = SourceType.UNKNOWN
    source_url: str | None = None
    title: str | None = None
    company: str | None = None
    location: str | None = None
    raw_text: str
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    fetch_status: FetchStatus = FetchStatus.SUCCESS
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    error_message: str | None = None

    @field_validator("raw_text")
    @classmethod
    def raw_text_not_empty_on_success(cls, v: str) -> str:
        return v.strip()

    def to_output(self) -> dict[str, Any]:
        """Return the canonical Phase 2 output dict."""
        return {
            "source_type": self.source_type.value,
            "source_url": self.source_url,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "raw_text": self.raw_text,
            "metadata": self.metadata.model_dump(),
        }


class IngestionRequest(BaseModel):
    """API request schema for URL-based ingestion."""

    url: str = Field(..., description="The job posting URL to ingest")
    force_playwright: bool = Field(
        default=False,
        description="Force Playwright-based rendering even for static pages",
    )
    timeout_seconds: int = Field(
        default=30, ge=5, le=120, description="Fetch timeout in seconds"
    )

    @field_validator("url")
    @classmethod
    def url_must_be_valid(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class IngestionResponse(BaseModel):
    """API response schema wrapping a FetchedDocument."""

    success: bool
    document: FetchedDocument | None = None
    error: str | None = None
    duration_ms: float | None = None
