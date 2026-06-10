"""Core domain models for JD Skill Extraction Pipeline."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    UUID,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REVIEW_REQUIRED = "review_required"


class RequirementType(str, enum.Enum):
    MUST_HAVE = "must_have"
    PREFERRED = "preferred"
    OPTIONAL = "optional"


class ReviewStatus(str, enum.Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CORRECTED = "corrected"


class Job(Base):
    """Represents a parsed job description."""

    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    company: Mapped[str | None] = mapped_column(String(256), nullable=True)
    location: Mapped[str | None] = mapped_column(String(256), nullable=True)
    seniority: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus), default=JobStatus.PENDING, nullable=False
    )
    review_required: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    experience_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    experience_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    job_skills: Mapped[list["JobSkill"]] = relationship(
        "JobSkill", back_populates="job", cascade="all, delete-orphan"
    )
    review: Mapped["ReviewQueue | None"] = relationship(
        "ReviewQueue", back_populates="job", uselist=False, cascade="all, delete-orphan"
    )
    processing_runs: Mapped[list["ProcessingRun"]] = relationship(
        "ProcessingRun", back_populates="job", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog", back_populates="job", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_jobs_status", "status"),)


class Skill(Base):
    """Represents a normalized skill entity."""

    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)
    normalized_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    esco_code: Mapped[str | None] = mapped_column(String(128), nullable=True)
    esco_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    job_skills: Mapped[list["JobSkill"]] = relationship(
        "JobSkill", back_populates="skill"
    )

    __table_args__ = (Index("ix_skills_name", "name"),)


class JobSkill(Base):
    """Associates jobs with skills and classification metadata."""

    __tablename__ = "job_skills"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
    )
    requirement_type: Mapped[RequirementType] = mapped_column(
        Enum(RequirementType), default=RequirementType.MUST_HAVE, nullable=False
    )
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="job_skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="job_skills")

    __table_args__ = (
        Index("ix_job_skills_job_id", "job_id"),
        Index("ix_job_skills_skill_id", "skill_id"),
    )


class ReviewQueue(Base):
    """Tracks jobs requiring human review."""

    __tablename__ = "review_queue"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus), default=ReviewStatus.PENDING, nullable=False
    )
    flagged_reasons: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(256), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="review")

    __table_args__ = (Index("ix_review_queue_status", "status"),)


class ProcessingRun(Base):
    """Tracks individual pipeline processing runs."""

    __tablename__ = "processing_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="started")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="processing_runs")

    __table_args__ = (Index("ix_processing_runs_job_id", "job_id"),)


class AuditLog(Base):
    """Immutable audit trail of all actions on jobs."""

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    actor: Mapped[str | None] = mapped_column(String(256), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="audit_logs")

    __table_args__ = (Index("ix_audit_logs_job_id", "job_id"),)
