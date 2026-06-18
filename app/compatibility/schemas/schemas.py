"""Pydantic schemas for the Job ↔ Resume Compatibility Engine."""

from typing import List, Optional

from pydantic import BaseModel, Field


class SkillMatch(BaseModel):
    """Details about matched, missing, and additional skills."""

    matched: List[str] = Field(
        default_factory=list,
        description="Skills present in both resume and job description.",
    )
    missing: List[str] = Field(
        default_factory=list,
        description="Skills required by the job but missing from the resume.",
    )
    additional: List[str] = Field(
        default_factory=list,
        description="Extra skills present in the resume but not specified in the job description.",
    )


class ExperienceMatch(BaseModel):
    """Details about experience comparison."""

    required: Optional[float] = Field(
        default=None, description="Required experience in years."
    )
    candidate: float = Field(
        default=0.0, description="Candidate's experience in years."
    )
    gap: float = Field(
        default=0.0,
        description="Difference between required and candidate experience (0 if candidate >= required).",
    )


class EducationMatch(BaseModel):
    """Details about education comparison."""

    required_degree: Optional[str] = Field(
        default=None, description="Required education degree level."
    )
    candidate_degrees: List[str] = Field(
        default_factory=list, description="Degrees obtained by the candidate."
    )
    matches: bool = Field(
        default=False,
        description="True if candidate's education matches or exceeds the required level.",
    )


class GapAnalysis(BaseModel):
    """Identified technology, experience, or credential gaps."""

    critical_gaps: List[str] = Field(
        default_factory=list,
        description="Missing required technical skills or significant experience gaps.",
    )
    moderate_gaps: List[str] = Field(
        default_factory=list,
        description="Missing preferred skills or minor experience/education gaps.",
    )
    minor_gaps: List[str] = Field(
        default_factory=list,
        description="Missing optional tools or optional certifications.",
    )


class StrengthAnalysis(BaseModel):
    """Highlights of the candidate's matching attributes."""

    strong_matches: List[str] = Field(
        default_factory=list,
        description="List of candidate's strengths matching the job requirements.",
    )


class CompatibilityReport(BaseModel):
    """Overall Job ↔ Resume Compatibility Report."""

    compatibility_score: int = Field(
        ..., ge=0, le=100, description="Overall compatibility score (0-100)."
    )
    skill_match: SkillMatch = Field(
        ..., description="Details of matched and missing skills."
    )
    experience_match: ExperienceMatch = Field(
        ..., description="Details of experience match."
    )
    education_match: EducationMatch = Field(
        ..., description="Details of education match."
    )
    gap_analysis: GapAnalysis = Field(
        ..., description="Breakdown of critical, moderate, and minor gaps."
    )
    strength_analysis: StrengthAnalysis = Field(
        ..., description="List of candidate strengths."
    )
