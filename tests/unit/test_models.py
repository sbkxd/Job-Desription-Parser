"""Unit tests for core domain models."""

import uuid

from app.models.models import (
    AuditLog,
    Job,
    JobSkill,
    JobStatus,
    ProcessingRun,
    RequirementType,
    ReviewQueue,
    ReviewStatus,
    Skill,
)


def test_job_model_instantiation():
    """Test Job model can be instantiated with required fields."""
    job = Job(title="Software Engineer", company="Acme Corp")
    assert job.title == "Software Engineer"
    assert job.company == "Acme Corp"


def test_job_model_with_status():
    """Test Job model can be instantiated with explicit status."""
    job = Job(title="Data Scientist", status=JobStatus.PROCESSING)
    assert job.title == "Data Scientist"
    assert job.status == JobStatus.PROCESSING


def test_job_status_enum():
    assert JobStatus.PENDING == "pending"
    assert JobStatus.PROCESSING == "processing"
    assert JobStatus.COMPLETED == "completed"
    assert JobStatus.FAILED == "failed"
    assert JobStatus.REVIEW_REQUIRED == "review_required"


def test_skill_model_instantiation():
    skill = Skill(name="Python")
    assert skill.name == "Python"
    assert skill.esco_code is None
    assert skill.esco_uri is None


def test_skill_model_with_esco():
    skill = Skill(name="Python", esco_code="S1.2.3", category="Programming")
    assert skill.esco_code == "S1.2.3"
    assert skill.category == "Programming"


def test_job_skill_model_instantiation():
    job_id = uuid.uuid4()
    skill_id = uuid.uuid4()
    job_skill = JobSkill(
        job_id=job_id,
        skill_id=skill_id,
        requirement_type=RequirementType.MUST_HAVE,
    )
    assert job_skill.job_id == job_id
    assert job_skill.skill_id == skill_id
    assert job_skill.requirement_type == RequirementType.MUST_HAVE


def test_requirement_type_enum():
    assert RequirementType.MUST_HAVE == "must_have"
    assert RequirementType.PREFERRED == "preferred"
    assert RequirementType.OPTIONAL == "optional"


def test_review_queue_instantiation():
    job_id = uuid.uuid4()
    review = ReviewQueue(job_id=job_id, status=ReviewStatus.PENDING)
    assert review.job_id == job_id
    assert review.status == ReviewStatus.PENDING
    assert review.reviewed_by is None


def test_review_status_enum():
    assert ReviewStatus.PENDING == "pending"
    assert ReviewStatus.APPROVED == "approved"
    assert ReviewStatus.REJECTED == "rejected"


def test_processing_run_instantiation():
    job_id = uuid.uuid4()
    run = ProcessingRun(job_id=job_id, status="started")
    assert run.job_id == job_id
    assert run.status == "started"
    assert run.error_message is None


def test_processing_run_with_error():
    job_id = uuid.uuid4()
    run = ProcessingRun(
        job_id=job_id, status="failed", error_message="Timeout exceeded"
    )
    assert run.status == "failed"
    assert run.error_message == "Timeout exceeded"


def test_audit_log_model():
    job_id = uuid.uuid4()
    log = AuditLog(job_id=job_id, action="job_created", actor="system")
    assert log.job_id == job_id
    assert log.action == "job_created"
    assert log.actor == "system"


def test_audit_log_no_actor():
    job_id = uuid.uuid4()
    log = AuditLog(job_id=job_id, action="automated_parse")
    assert log.actor is None


def test_model_table_names():
    assert Job.__tablename__ == "jobs"
    assert Skill.__tablename__ == "skills"
    assert JobSkill.__tablename__ == "job_skills"
    assert ReviewQueue.__tablename__ == "review_queue"
    assert ProcessingRun.__tablename__ == "processing_runs"
    assert AuditLog.__tablename__ == "audit_logs"


def test_model_primary_key_columns():
    """Test all models have id as primary key column."""
    for model in [Job, Skill, JobSkill, ReviewQueue, ProcessingRun, AuditLog]:
        pk_cols = [
            c.name for c in model.__table__.primary_key.columns  # type: ignore[attr-defined]
        ]
        assert "id" in pk_cols, f"{model.__name__} missing 'id' PK"
