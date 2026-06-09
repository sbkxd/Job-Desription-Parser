"""Job repository with domain-specific queries."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.models import Job, JobStatus
from app.repositories.base import SQLAlchemyRepository


class JobRepository(SQLAlchemyRepository[Job]):
    """Repository for Job entity with domain-specific operations."""

    model = Job

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_with_skills(self, job_id: UUID) -> Job | None:
        """Retrieve a Job eagerly loading its skills."""
        stmt = select(Job).where(Job.id == job_id).options(selectinload(Job.job_skills))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_status(
        self, status: JobStatus, limit: int = 100, offset: int = 0
    ) -> list[Job]:
        """Retrieve jobs filtered by processing status."""
        stmt = (
            select(Job)
            .where(Job.status == status)
            .limit(limit)
            .offset(offset)
            .order_by(Job.created_at.desc())  # type: ignore[attr-defined]
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_pending_review(self, limit: int = 50) -> list[Job]:
        """Retrieve jobs flagged for human review."""
        stmt = (
            select(Job)
            .where(Job.review_required.is_(True))  # type: ignore[attr-defined]
            .limit(limit)
            .order_by(Job.created_at.asc())  # type: ignore[attr-defined]
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(self, job_id: UUID, status: JobStatus) -> Job | None:
        """Update the status of a job by ID."""
        job = await self.get(job_id)
        if job is None:
            return None
        job.status = status
        await self._session.flush()
        return job
