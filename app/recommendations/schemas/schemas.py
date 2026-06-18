"""Pydantic schemas for Mistral Resume Optimization Engine."""

from typing import List

from pydantic import BaseModel, Field


class ImprovementSuggestion(BaseModel):
    """Personalized advisory suggestion to improve a specific section of the resume."""

    type: str = Field(
        ...,
        description="Type of gap (e.g. MISSING_SKILL, KEYWORD, EXPERIENCE, PROJECT, EDUCATION, CERTIFICATION)",
    )
    section: str = Field(
        ...,
        description="Section of the resume (e.g. Skills, Experience, Projects, Education, Certifications)",
    )
    message: str = Field(
        ...,
        description="Advisory feedback. NEVER rewrite facts, invent experience, or fabricate skills.",
    )


class AtsRecommendation(BaseModel):
    """ATS optimization recommendation based on job description keywords."""

    keyword: str = Field(..., description="Job keyword or technology.")
    coverage_status: str = Field(..., description="Status (e.g. MISSING, LOW_COVERAGE)")
    recommendation: str = Field(
        ...,
        description="Specific recommendation on how to naturally incorporate this keyword if applicable.",
    )


class ApplicationReadiness(BaseModel):
    """Aggregated application readiness evaluation."""

    readiness_score: int = Field(
        ..., ge=0, le=100, description="Readiness score from 0-100."
    )
    recommendation: str = Field(..., description="Summary advice regarding readiness.")


class MistralRecommendationsResponse(BaseModel):
    """Structured response schema returned directly from Mistral LLM."""

    resume_improvements: List[ImprovementSuggestion] = Field(
        default_factory=list, description="Advisory suggestions for resume sections."
    )
    ats_recommendations: List[AtsRecommendation] = Field(
        default_factory=list, description="ATS keyword optimizations."
    )
    tailored_summary: str = Field(
        ...,
        description="Tailored professional summary based strictly on actual resume content.",
    )
    application_readiness_score: int = Field(
        ..., ge=0, le=100, description="Readiness score from 0-100."
    )
    application_readiness_recommendation: str = Field(
        ..., description="Overall readiness advice."
    )


class ResumeOptimizationReport(BaseModel):
    """Unified Resume Optimization and Compatibility Report."""

    compatibility_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall compatibility score (0-100) from Phase 9.",
    )
    matched_skills: List[str] = Field(
        default_factory=list, description="Skills matched between resume and JD."
    )
    missing_skills: List[str] = Field(
        default_factory=list,
        description="Required/preferred skills missing from the resume.",
    )
    critical_gaps: List[str] = Field(
        default_factory=list, description="Significant experience or skill gaps."
    )
    strengths: List[str] = Field(
        default_factory=list, description="Highlighted candidate strengths."
    )
    resume_improvements: List[ImprovementSuggestion] = Field(
        default_factory=list, description="Personalized section-by-section suggestions."
    )
    ats_recommendations: List[AtsRecommendation] = Field(
        default_factory=list, description="ATS optimization suggestions."
    )
    application_readiness_score: int = Field(
        ..., ge=0, le=100, description="Readiness score (0-100)."
    )
    application_readiness_recommendation: str = Field(
        ..., description="Summary advice regarding readiness."
    )
    tailored_summary: str = Field(
        ...,
        description="A professional summary tailored for this job, grounded ONLY in actual resume content.",
    )
