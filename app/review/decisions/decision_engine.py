"""Service for processing human review decisions on normalized skills."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import JobSkill, Skill


class ReviewDecisionService:
    """Processes reviewer decisions (approve, reject, correct) for job skills."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def approve_skill(
        self, job_id: UUID, raw_skill: str, reviewer: str | None = None
    ) -> bool:
        """Approve a skill mapping as-is."""
        # Find the JobSkill link via Raw Skill (or exact name match)
        # Note: We find the skill matching raw_skill or normalized name
        stmt = (
            select(JobSkill)
            .join(Skill)
            .where(
                JobSkill.job_id == job_id,
                (Skill.name.ilike(raw_skill) | Skill.normalized_name.ilike(raw_skill)),
            )
        )
        res = await self.session.execute(stmt)
        job_skill = res.scalars().first()
        if not job_skill:
            return False

        # Auditing and logging is handled by the caller or audit manager.
        return True

    async def reject_skill(
        self, job_id: UUID, raw_skill: str, reviewer: str | None = None
    ) -> bool:
        """Reject and remove a skill mapping from a job."""
        stmt = (
            select(JobSkill)
            .join(Skill)
            .where(
                JobSkill.job_id == job_id,
                (Skill.name.ilike(raw_skill) | Skill.normalized_name.ilike(raw_skill)),
            )
        )
        res = await self.session.execute(stmt)
        job_skill = res.scalars().first()
        if not job_skill:
            return False

        await self.session.delete(job_skill)
        await self.session.flush()
        return True

    async def correct_skill(
        self,
        job_id: UUID,
        raw_skill: str,
        corrected_name: str,
        esco_id: str | None = None,
        reviewer: str | None = None,
    ) -> bool:
        """Correct/replace a skill mapping with a new skill reference."""
        # 1. Find the existing JobSkill record
        stmt = (
            select(JobSkill)
            .join(Skill)
            .where(
                JobSkill.job_id == job_id,
                (Skill.name.ilike(raw_skill) | Skill.normalized_name.ilike(raw_skill)),
            )
        )
        res = await self.session.execute(stmt)
        job_skill = res.scalars().first()
        if not job_skill:
            return False

        # 2. Find or create the corrected Skill in database
        skill_stmt = select(Skill).where(Skill.name.ilike(corrected_name))
        skill_res = await self.session.execute(skill_stmt)
        target_skill = skill_res.scalars().first()

        if not target_skill:
            # Create a custom skill record
            target_skill = Skill(
                name=corrected_name,
                normalized_name=corrected_name.lower().strip(),
                esco_code=esco_id,
                category="Custom / Corrected Skill",
            )
            self.session.add(target_skill)
            await self.session.flush()

        # 3. Re-point the JobSkill record
        job_skill.skill_id = target_skill.id
        await self.session.flush()
        return True
