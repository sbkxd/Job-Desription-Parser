"""Pydantic schemas for Information Extraction Engine."""

from pydantic import BaseModel, Field


class SkillMention(BaseModel):
    """Represents a single extracted skill mention."""

    name: str = Field(..., description="Extract skill name (e.g. Python, SQL)")
    confidence: float = Field(
        ..., description="Confidence score in [0.0, 1.0]", ge=0.0, le=1.0
    )
    section: str = Field(..., description="The source section where mention was found")


class ExperienceRequirement(BaseModel):
    """Represents experience requirements parsed from the job description."""

    min_years: float | None = Field(
        default=None, description="Minimum years of experience required"
    )
    max_years: float | None = Field(
        default=None, description="Maximum years of experience required"
    )


class SeniorityLevel(BaseModel):
    """Represents the resolved seniority level of the position."""

    seniority: str = Field(
        ..., description="Resolved level (e.g. Senior, Mid, Junior, Intern)"
    )
    confidence: float = Field(
        ..., description="Confidence score in [0.0, 1.0]", ge=0.0, le=1.0
    )


class RequirementClassification(BaseModel):
    """Represents a classified requirement line."""

    text: str = Field(..., description="The original line of text")
    classification: str = Field(..., description="Required, Preferred, or Optional")
    confidence: float = Field(
        ..., description="Confidence score in [0.0, 1.0]", ge=0.0, le=1.0
    )


class ExtractionResult(BaseModel):
    """Complete output of the information extraction pipeline."""

    success: bool = Field(..., description="True if extraction succeeded")
    skills: list[SkillMention] = Field(
        default_factory=list, description="List of extracted skills"
    )
    experience: ExperienceRequirement = Field(
        default_factory=ExperienceRequirement,
        description="Resolved experience requirements",
    )
    seniority: SeniorityLevel | None = Field(
        default=None, description="Resolved seniority level"
    )
    requirements_classification: list[RequirementClassification] = Field(
        default_factory=list, description="Classified requirement lines"
    )
    duration_ms: float | None = Field(
        default=None, description="Extraction duration in milliseconds"
    )
    error: str | None = Field(
        default=None, description="Error message if success is False"
    )
