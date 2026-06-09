"""Unit tests for Milestone 2.1 — Ingestion Domain Schemas."""

import pytest
from pydantic import ValidationError

from app.ingestion.schemas import (
    DocumentMetadata,
    FetchedDocument,
    FetchStatus,
    IngestionRequest,
    IngestionResponse,
    SourceType,
)

# ---------------------------------------------------------------------------
# SourceType enum
# ---------------------------------------------------------------------------


class TestSourceType:
    def test_all_values(self):
        expected = {
            "naukri",
            "foundit",
            "indeed",
            "greenhouse",
            "lever",
            "workable",
            "generic_ats",
            "pdf",
            "unknown",
        }
        assert {s.value for s in SourceType} == expected

    def test_string_coercion(self):
        assert SourceType("lever") == SourceType.LEVER
        assert SourceType("pdf") == SourceType.PDF

    def test_invalid_source_type(self):
        with pytest.raises(ValueError):
            SourceType("twitter")


# ---------------------------------------------------------------------------
# FetchStatus enum
# ---------------------------------------------------------------------------


class TestFetchStatus:
    def test_all_values(self):
        expected = {"success", "failed", "partial", "timeout", "blocked"}
        assert {s.value for s in FetchStatus} == expected


# ---------------------------------------------------------------------------
# DocumentMetadata
# ---------------------------------------------------------------------------


class TestDocumentMetadata:
    def test_defaults(self):
        meta = DocumentMetadata()
        assert meta.platform == SourceType.UNKNOWN
        assert meta.http_status is None
        assert meta.structured_data == {}
        assert meta.extra == {}

    def test_full_construction(self):
        meta = DocumentMetadata(
            platform=SourceType.LEVER,
            http_status=200,
            content_type="text/html",
            fetch_duration_ms=340.5,
            page_count=None,
            word_count=850,
            language="en",
            og_title="Senior Engineer at Acme",
            og_description="Join our team!",
            og_image="https://example.com/img.png",
            structured_data={"@type": "JobPosting"},
            extra={"canonical_url": "https://jobs.lever.co/acme/123"},
        )
        assert meta.platform == SourceType.LEVER
        assert meta.og_title == "Senior Engineer at Acme"
        assert meta.structured_data["@type"] == "JobPosting"

    def test_serialization(self):
        meta = DocumentMetadata(platform=SourceType.GREENHOUSE, http_status=200)
        dumped = meta.model_dump()
        assert dumped["platform"] == "greenhouse"
        assert dumped["http_status"] == 200


# ---------------------------------------------------------------------------
# FetchedDocument
# ---------------------------------------------------------------------------


class TestFetchedDocument:
    def test_minimal_construction(self):
        doc = FetchedDocument(raw_text="Python developer needed.")
        assert doc.raw_text == "Python developer needed."
        assert doc.source_type == SourceType.UNKNOWN
        assert doc.fetch_status == FetchStatus.SUCCESS
        assert doc.title is None
        assert doc.company is None
        assert doc.location is None

    def test_full_construction(self):
        doc = FetchedDocument(
            source_type=SourceType.LEVER,
            source_url="https://jobs.lever.co/acme/123",
            title="Senior Engineer",
            company="Acme Corp",
            location="Bangalore, IN",
            raw_text="We are hiring a Senior Engineer...",
            fetch_status=FetchStatus.SUCCESS,
        )
        assert doc.source_type == SourceType.LEVER
        assert doc.company == "Acme Corp"
        assert doc.fetch_status == FetchStatus.SUCCESS

    def test_to_output_contract(self):
        """Ensure to_output() matches the exact Phase 2 contract."""
        doc = FetchedDocument(
            source_type=SourceType.NAUKRI,
            source_url="https://naukri.com/job/123",
            title="Data Engineer",
            company="TechCorp",
            location="Mumbai",
            raw_text="Looking for a data engineer...",
        )
        output = doc.to_output()
        required_keys = {
            "source_type",
            "source_url",
            "title",
            "company",
            "location",
            "raw_text",
            "metadata",
        }
        assert required_keys == set(output.keys())
        assert output["source_type"] == "naukri"
        assert output["raw_text"] == "Looking for a data engineer..."

    def test_raw_text_stripped(self):
        doc = FetchedDocument(raw_text="  text with spaces  ")
        assert doc.raw_text == "text with spaces"

    def test_empty_raw_text_allowed(self):
        """Empty raw text is allowed (failed fetch scenario)."""
        doc = FetchedDocument(raw_text="", fetch_status=FetchStatus.FAILED)
        assert doc.raw_text == ""

    def test_serialization_roundtrip(self):
        doc = FetchedDocument(
            source_type=SourceType.INDEED,
            source_url="https://indeed.com/job/456",
            raw_text="Software developer job",
        )
        dumped = doc.model_dump()
        restored = FetchedDocument.model_validate(dumped)
        assert restored.source_type == SourceType.INDEED
        assert restored.raw_text == "Software developer job"

    def test_metadata_nested(self):
        meta = DocumentMetadata(platform=SourceType.GREENHOUSE, http_status=200)
        doc = FetchedDocument(raw_text="test", metadata=meta)
        assert doc.metadata.platform == SourceType.GREENHOUSE
        assert doc.metadata.http_status == 200


# ---------------------------------------------------------------------------
# IngestionRequest
# ---------------------------------------------------------------------------


class TestIngestionRequest:
    def test_valid_https_url(self):
        req = IngestionRequest(url="https://jobs.lever.co/company/abc")
        assert req.url == "https://jobs.lever.co/company/abc"
        assert req.force_playwright is False
        assert req.timeout_seconds == 30

    def test_valid_http_url(self):
        req = IngestionRequest(url="http://example.com/job/1")
        assert req.url == "http://example.com/job/1"

    def test_url_strips_whitespace(self):
        req = IngestionRequest(url="  https://example.com/job  ")
        assert req.url == "https://example.com/job"

    def test_invalid_url_raises(self):
        with pytest.raises(ValidationError):
            IngestionRequest(url="ftp://not-http.com")

    def test_missing_url_raises(self):
        with pytest.raises(ValidationError):
            IngestionRequest()

    def test_timeout_bounds(self):
        with pytest.raises(ValidationError):
            IngestionRequest(url="https://example.com", timeout_seconds=4)
        with pytest.raises(ValidationError):
            IngestionRequest(url="https://example.com", timeout_seconds=121)

    def test_force_playwright_flag(self):
        req = IngestionRequest(url="https://example.com", force_playwright=True)
        assert req.force_playwright is True


# ---------------------------------------------------------------------------
# IngestionResponse
# ---------------------------------------------------------------------------


class TestIngestionResponse:
    def test_success_response(self):
        doc = FetchedDocument(raw_text="Job description text")
        resp = IngestionResponse(success=True, document=doc, duration_ms=145.2)
        assert resp.success is True
        assert resp.document is not None
        assert resp.error is None

    def test_failure_response(self):
        resp = IngestionResponse(
            success=False, error="Connection timeout", duration_ms=30000.0
        )
        assert resp.success is False
        assert resp.document is None
        assert resp.error == "Connection timeout"

    def test_serialization(self):
        resp = IngestionResponse(
            success=True, document=FetchedDocument(raw_text="text")
        )
        dumped = resp.model_dump()
        assert dumped["success"] is True
        assert "document" in dumped
