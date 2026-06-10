"""Manager for the persistent review queue database layer."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import ReviewQueue, ReviewStatus
from app.repositories.base import SQLAlchemyRepository


class ReviewQueueManager(SQLAlchemyRepository[ReviewQueue]):
    """Queue manager for handling human review lifecycle transitions."""

    model = ReviewQueue

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_job_id(self, job_id: UUID) -> ReviewQueue | None:
        """Retrieve the review queue entry for a specific job."""
        stmt = select(self.model).where(self.model.job_id == job_id)
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def update_status(
        self,
        review_id: UUID,
        status: ReviewStatus,
        reviewer: str | None = None,
        flagged_reasons: str | None = None,
    ) -> ReviewQueue | None:
        """Update the review status and review timestamps."""
        review_item = await self.get(review_id)
        if not review_item:
            return None

        review_item.status = status
        if status in [
            ReviewStatus.APPROVED,
            ReviewStatus.REJECTED,
            ReviewStatus.CORRECTED,
        ]:
            review_item.reviewed_at = datetime.utcnow()
            review_item.reviewed_by = reviewer

        if flagged_reasons is not None:
            review_item.flagged_reasons = flagged_reasons

        await self._session.flush()
        return review_item
