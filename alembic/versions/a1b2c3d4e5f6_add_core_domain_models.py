"""add_core_domain_models

Revision ID: a1b2c3d4e5f6
Revises: 3bc883988942
Create Date: 2026-06-09

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "3bc883988942"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Enums
job_status = sa.Enum(
    "pending",
    "processing",
    "completed",
    "failed",
    "review_required",
    name="jobstatus",
)
requirement_type = sa.Enum(
    "must_have",
    "preferred",
    "optional",
    name="requirementtype",
)
review_status = sa.Enum(
    "pending",
    "approved",
    "rejected",
    name="reviewstatus",
)


def upgrade() -> None:
    """Create all core domain tables."""

    # --- jobs ---
    op.create_table(
        "jobs",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(512), nullable=True),
        sa.Column("company", sa.String(256), nullable=True),
        sa.Column("location", sa.String(256), nullable=True),
        sa.Column("seniority", sa.String(64), nullable=True),
        sa.Column("source_url", sa.Text, nullable=True),
        sa.Column("raw_text", sa.Text, nullable=True),
        sa.Column(
            "status",
            job_status,
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "review_required", sa.Boolean, nullable=False, server_default="false"
        ),
        sa.Column("experience_min", sa.Float, nullable=True),
        sa.Column("experience_max", sa.Float, nullable=True),
        sa.Column("confidence_score", sa.Float, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_jobs_status", "jobs", ["status"])

    # --- skills ---
    op.create_table(
        "skills",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(256), nullable=False, unique=True),
        sa.Column("normalized_name", sa.String(256), nullable=True),
        sa.Column("esco_code", sa.String(128), nullable=True),
        sa.Column("esco_uri", sa.Text, nullable=True),
        sa.Column("category", sa.String(128), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_skills_name", "skills", ["name"])

    # --- job_skills ---
    op.create_table(
        "job_skills",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "job_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("jobs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "skill_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("skills.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "requirement_type",
            requirement_type,
            nullable=False,
            server_default="must_have",
        ),
        sa.Column("confidence_score", sa.Float, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_job_skills_job_id", "job_skills", ["job_id"])
    op.create_index("ix_job_skills_skill_id", "job_skills", ["skill_id"])

    # --- review_queue ---
    op.create_table(
        "review_queue",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "job_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("jobs.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "status",
            review_status,
            nullable=False,
            server_default="pending",
        ),
        sa.Column("flagged_reasons", sa.Text, nullable=True),
        sa.Column("reviewed_by", sa.String(256), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_review_queue_status", "review_queue", ["status"])

    # --- processing_runs ---
    op.create_table(
        "processing_runs",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "job_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("jobs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(64), nullable=False, server_default="started"),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("duration_ms", sa.Float, nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_processing_runs_job_id", "processing_runs", ["job_id"])

    # --- audit_logs ---
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "job_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("jobs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("action", sa.String(128), nullable=False),
        sa.Column("actor", sa.String(256), nullable=True),
        sa.Column("details", sa.Text, nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_audit_logs_job_id", "audit_logs", ["job_id"])


def downgrade() -> None:
    """Drop all core domain tables."""
    op.drop_index("ix_audit_logs_job_id", "audit_logs")
    op.drop_table("audit_logs")
    op.drop_index("ix_processing_runs_job_id", "processing_runs")
    op.drop_table("processing_runs")
    op.drop_index("ix_review_queue_status", "review_queue")
    op.drop_table("review_queue")
    op.drop_index("ix_job_skills_skill_id", "job_skills")
    op.drop_index("ix_job_skills_job_id", "job_skills")
    op.drop_table("job_skills")
    op.drop_index("ix_skills_name", "skills")
    op.drop_table("skills")
    op.drop_index("ix_jobs_status", "jobs")
    op.drop_table("jobs")
    job_status.drop(op.get_bind(), checkfirst=True)
    requirement_type.drop(op.get_bind(), checkfirst=True)
    review_status.drop(op.get_bind(), checkfirst=True)
