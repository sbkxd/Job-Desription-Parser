"""Skill repository with domain-specific queries."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Skill
from app.repositories.base import SQLAlchemyRepository


class SkillRepository(SQLAlchemyRepository[Skill]):
    """Repository for Skill entity."""

    model = Skill

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_name(self, name: str) -> Skill | None:
        """Retrieve a skill by its canonical name (case-insensitive)."""
        stmt = select(Skill).where(Skill.name.ilike(name))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_esco_code(self, esco_code: str) -> Skill | None:
        """Retrieve a skill by ESCO code."""
        stmt = select(Skill).where(Skill.esco_code == esco_code)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def search_by_category(self, category: str) -> list[Skill]:
        """Retrieve skills by category."""
        stmt = select(Skill).where(Skill.category == category).order_by(Skill.name)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_or_create(self, name: str, **kwargs: object) -> tuple[Skill, bool]:
        """Return existing skill or create a new one. Returns (skill, created)."""
        existing = await self.get_by_name(name)
        if existing is not None:
            return existing, False
        skill = Skill(name=name, **kwargs)
        await self.add(skill)
        return skill, True
