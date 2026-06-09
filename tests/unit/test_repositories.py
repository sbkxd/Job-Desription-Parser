"""Unit tests for repository pattern (mocked async session)."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.models import Job, JobStatus, Skill
from app.repositories.job_repository import JobRepository
from app.repositories.skill_repository import SkillRepository


def make_session() -> AsyncMock:
    """Create a mock async SQLAlchemy session."""
    session = AsyncMock()
    session.get = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.delete = AsyncMock()
    session.flush = AsyncMock()
    return session


# ---------------------------------------------------------------------------
# JobRepository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_job_repo_get_returns_job():
    session = make_session()
    job = Job(id=uuid.uuid4(), title="Engineer")
    session.get.return_value = job

    repo = JobRepository(session)
    result = await repo.get(job.id)

    assert result is job
    session.get.assert_called_once_with(Job, job.id)


@pytest.mark.asyncio
async def test_job_repo_get_returns_none():
    session = make_session()
    session.get.return_value = None

    repo = JobRepository(session)
    result = await repo.get(uuid.uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_job_repo_add_flushes():
    session = make_session()
    job = Job(title="ML Engineer", status=JobStatus.PENDING)

    repo = JobRepository(session)
    result = await repo.add(job)

    session.add.assert_called_once_with(job)
    session.flush.assert_called_once()
    assert result is job


@pytest.mark.asyncio
async def test_job_repo_delete_existing():
    session = make_session()
    job_id = uuid.uuid4()
    job = Job(id=job_id, title="Analyst")
    session.get.return_value = job

    repo = JobRepository(session)
    deleted = await repo.delete(job_id)

    assert deleted is True
    session.delete.assert_called_once_with(job)
    session.flush.assert_called_once()


@pytest.mark.asyncio
async def test_job_repo_delete_not_found():
    session = make_session()
    session.get.return_value = None

    repo = JobRepository(session)
    deleted = await repo.delete(uuid.uuid4())

    assert deleted is False
    session.delete.assert_not_called()


@pytest.mark.asyncio
async def test_job_repo_list():
    session = make_session()
    jobs = [Job(title=f"Job {i}") for i in range(3)]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = jobs
    session.execute.return_value = mock_result

    repo = JobRepository(session)
    result = await repo.list(limit=10, offset=0)

    assert result == jobs
    session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_job_repo_list_by_status():
    session = make_session()
    jobs = [Job(title="Job A", status=JobStatus.COMPLETED)]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = jobs
    session.execute.return_value = mock_result

    repo = JobRepository(session)
    result = await repo.list_by_status(JobStatus.COMPLETED)

    assert len(result) == 1
    session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_job_repo_update_status():
    session = make_session()
    job_id = uuid.uuid4()
    job = Job(id=job_id, title="Dev", status=JobStatus.PENDING)
    session.get.return_value = job

    repo = JobRepository(session)
    result = await repo.update_status(job_id, JobStatus.COMPLETED)

    assert result is not None
    assert result.status == JobStatus.COMPLETED
    session.flush.assert_called_once()


@pytest.mark.asyncio
async def test_job_repo_update_status_not_found():
    session = make_session()
    session.get.return_value = None

    repo = JobRepository(session)
    result = await repo.update_status(uuid.uuid4(), JobStatus.COMPLETED)

    assert result is None


# ---------------------------------------------------------------------------
# SkillRepository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_skill_repo_get_by_name():
    session = make_session()
    skill = Skill(name="Python")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = skill
    session.execute.return_value = mock_result

    repo = SkillRepository(session)
    result = await repo.get_by_name("Python")

    assert result is skill


@pytest.mark.asyncio
async def test_skill_repo_get_by_name_not_found():
    session = make_session()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    session.execute.return_value = mock_result

    repo = SkillRepository(session)
    result = await repo.get_by_name("NonExistentSkill")

    assert result is None


@pytest.mark.asyncio
async def test_skill_repo_get_or_create_existing():
    session = make_session()
    skill = Skill(name="Python")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = skill
    session.execute.return_value = mock_result

    repo = SkillRepository(session)
    result, created = await repo.get_or_create("Python")

    assert result is skill
    assert created is False
    session.add.assert_not_called()


@pytest.mark.asyncio
async def test_skill_repo_get_or_create_new():
    session = make_session()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    session.execute.return_value = mock_result

    repo = SkillRepository(session)
    result, created = await repo.get_or_create("Rust")

    assert created is True
    assert result.name == "Rust"
    session.add.assert_called_once()
    session.flush.assert_called_once()
