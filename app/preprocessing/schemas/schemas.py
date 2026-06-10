"""Preprocessing schemas — data contracts for JD segmentation pipeline."""

import enum
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class SectionType(str, enum.Enum):
    """Canonical section types produced by the segmentation pipeline."""

    RESPONSIBILITIES = "responsibilities"
    REQUIREMENTS = "requirements"
    NICE_TO_HAVE = "nice_to_have"
    ABOUT_COMPANY = "about_company"
    BENEFITS = "benefits"
    OTHER = "other"


class BoilerplateCategory(str, enum.Enum):
    """Categories of detected boilerplate content."""

    EQUAL_OPPORTUNITY = "equal_opportunity"
    LEGAL_DISCLAIMER = "legal_disclaimer"
    PRIVACY_STATEMENT = "privacy_statement"
    APPLICATION_INSTRUCTIONS = "application_instructions"
    RECRUITMENT_MARKETING = "recruitment_marketing"
    GENERIC_POLICY = "generic_policy"


class RawDocument(BaseModel):
    """Input contract for the preprocessing pipeline.

    Accepts the raw text emitted by the ingestion pipeline.
    """

    raw_text: str = Field(..., description="Raw job description text to segment")
    source_type: str | None = Field(
        default=None,
        description="Optional source platform hint (naukri, lever, etc.)",
    )
    source_url: str | None = Field(
        default=None, description="Original URL of the job posting"
    )

    @field_validator("raw_text")
    @classmethod
    def raw_text_must_have_content(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("raw_text must not be empty")
        return v


class BoilerplateBlock(BaseModel):
    """A block of content removed by boilerplate detection.

    Content is never permanently discarded — it is tracked here
    for audit/debugging purposes.
    """

    category: BoilerplateCategory
    lines: list[str] = Field(default_factory=list)
    start_line_idx: int = 0


class Section(BaseModel):
    """A single classified section of a job description.

    Represents one logical block (e.g. Responsibilities, Requirements)
    with its heading, constituent lines, and classification confidence.
    """

    section_type: SectionType
    heading: str | None = Field(
        default=None, description="Detected heading text, None if inferred"
    )
    lines: list[str] = Field(
        default_factory=list, description="Content lines belonging to this section"
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Classification confidence in [0.0, 1.0]",
    )

    @property
    def text(self) -> str:
        """Full section text as a single string."""
        return "\n".join(self.lines)

    @property
    def is_empty(self) -> bool:
        """True when the section contains no meaningful content."""
        return not any(line.strip() for line in self.lines)


class SegmentedDocument(BaseModel):
    """Full output of the preprocessing/segmentation pipeline.

    Contains the classified sections and metadata about the run.
    """

    sections: list[Section] = Field(default_factory=list)
    boilerplate_removed: list[BoilerplateBlock] = Field(default_factory=list)
    segmented_at: datetime = Field(default_factory=datetime.utcnow)
    source_type: str | None = None
    source_url: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    def get_sections(self, section_type: SectionType) -> list[Section]:
        """Return all sections matching the given type."""
        return [s for s in self.sections if s.section_type == section_type]

    def to_output(self) -> dict[str, list[str]]:
        """Return the canonical Phase 3 output structure.

        Aggregates all line content per section type into a flat dict
        matching the required API output shape.
        """
        result: dict[str, list[str]] = {t.value: [] for t in SectionType}
        for section in self.sections:
            result[section.section_type.value].extend(
                line for line in section.lines if line.strip()
            )
        return result


class SegmentationResult(BaseModel):
    """API-level envelope wrapping a segmentation pipeline run."""

    success: bool
    document: SegmentedDocument | None = None
    error: str | None = None
    duration_ms: float | None = None
