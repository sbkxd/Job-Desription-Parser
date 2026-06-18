"""Pydantic schemas for Resume Intelligence & Extraction."""

from typing import List, Optional

from pydantic import BaseModel, Field


class EducationEntry(BaseModel):
    """Represents an education history entry."""

    degree: Optional[str] = Field(
        default=None, description="Degree name (e.g. Bachelor of Science)"
    )
    field_of_study: Optional[str] = Field(
        default=None, description="Field of study (e.g. Computer Science)"
    )
    school: Optional[str] = Field(default=None, description="Name of the institution")
    graduation_year: Optional[int] = Field(default=None, description="Graduation year")


class ExperienceEntry(BaseModel):
    """Represents a professional experience entry."""

    job_title: Optional[str] = Field(default=None, description="Job title or role")
    company: Optional[str] = Field(default=None, description="Company name")
    start_date: Optional[str] = Field(
        default=None, description="Start date (e.g. June 2021)"
    )
    end_date: Optional[str] = Field(default=None, description="End date or 'Present'")
    description: Optional[str] = Field(
        default=None, description="Description of duties/responsibilities"
    )
    years: Optional[float] = Field(
        default=None, description="Calculated years of experience in this role"
    )


class ProjectEntry(BaseModel):
    """Represents a project entry."""

    project_title: Optional[str] = Field(default=None, description="Project title")
    description: Optional[str] = Field(
        default=None, description="Description of project scope and details"
    )
    technologies: List[str] = Field(
        default_factory=list, description="Technologies or skills used in the project"
    )


class CandidateProfile(BaseModel):
    """Represents candidate metadata and highlights."""

    candidate_name: Optional[str] = Field(
        default=None, description="Full name of the candidate"
    )
    education: List[EducationEntry] = Field(
        default_factory=list, description="Education history"
    )
    years_experience: float = Field(
        default=0.0, description="Total years of professional experience"
    )
    certifications: List[str] = Field(
        default_factory=list, description="List of certifications"
    )
    summary: Optional[str] = Field(
        default=None, description="Professional summary or bio"
    )
    achievements: List[str] = Field(
        default_factory=list, description="List of notable achievements"
    )
    publications: List[str] = Field(
        default_factory=list, description="List of publications"
    )


class ResumeSkill(BaseModel):
    """Represents a skill extracted from the resume and optionally normalized."""

    raw_skill: str = Field(..., description="The skill as mentioned in the resume")
    normalized_skill: Optional[str] = Field(
        default=None, description="Normalized skill name from taxonomy"
    )
    confidence: float = Field(
        default=0.0, description="Extraction or normalization confidence score"
    )
    esco_id: Optional[str] = Field(
        default=None, description="ESCO ID code if normalized"
    )


class ResumeIntelligenceReport(BaseModel):
    """Canonical Resume Intelligence Report."""

    candidate_profile: CandidateProfile = Field(
        ..., description="Candidate's basic details and education"
    )
    skills: List[ResumeSkill] = Field(
        default_factory=list, description="Extracted and normalized skills"
    )
    experience: List[ExperienceEntry] = Field(
        default_factory=list, description="Work history details"
    )
    projects: List[ProjectEntry] = Field(
        default_factory=list, description="Projects list"
    )
