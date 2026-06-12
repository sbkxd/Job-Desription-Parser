"""Pydantic schemas for the Job Intelligence Report presentation layer."""

from typing import List, Optional

from pydantic import BaseModel, Field


class JobInformation(BaseModel):
    """Business-facing metadata about the job description."""

    job_title: str = Field(default="", description="The title of the job.")
    company: str = Field(default="", description="The company name.")
    location: str = Field(default="", description="The job location.")
    source_type: str = Field(default="", description="The source platform type.")
    source_url: str = Field(
        default="", description="The source URL of the job description."
    )


class RoleProfile(BaseModel):
    """Aggregated candidate background details."""

    seniority: str = Field(default="", description="The required seniority level.")
    minimum_experience_years: Optional[float] = Field(
        default=None, description="The minimum required experience in years."
    )
    maximum_experience_years: Optional[float] = Field(
        default=None, description="The maximum required experience in years."
    )


class Skills(BaseModel):
    """Categorized skills associated with the job description."""

    required: List[str] = Field(
        default_factory=list, description="List of required skills."
    )
    preferred: List[str] = Field(
        default_factory=list, description="List of preferred skills."
    )
    normalized: List[str] = Field(
        default_factory=list, description="List of standard/normalized skills."
    )


class ReviewSummary(BaseModel):
    """Flags indicating audit status and low confidence items requiring manual review."""

    review_required: bool = Field(
        default=False, description="Flag indicating if human review is required."
    )
    flagged_skills: List[str] = Field(
        default_factory=list,
        description="Skills flagged for low confidence or out-of-taxonomy.",
    )
    low_confidence_items: List[str] = Field(
        default_factory=list, description="Detailed list of low-confidence items."
    )


class JobIntelligenceReport(BaseModel):
    """The public API response contract for the pipeline."""

    job_information: JobInformation
    role_profile: RoleProfile
    skills: Skills
    education_requirements: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    qualifications: List[str] = Field(default_factory=list)
    technology_stack: List[str] = Field(default_factory=list)
    review_summary: ReviewSummary
