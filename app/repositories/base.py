"""Abstract base repository defining the generic CRUD contract."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class AbstractRepository(ABC, Generic[ModelT]):
    """Abstract base class for all repositories."""

    @abstractmethod
    async def get(self, entity_id: UUID) -> ModelT | None:
        """Retrieve a single entity by primary key."""
        ...

    @abstractmethod
    async def list(self, limit: int = 100, offset: int = 0) -> list[ModelT]:
        """Retrieve a paginated list of entities."""
        ...

    @abstractmethod
    async def add(self, entity: ModelT) -> ModelT:
        """Persist a new entity."""
        ...

    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """Remove an entity by primary key. Returns True if deleted."""
        ...


class SQLAlchemyRepository(AbstractRepository[ModelT], Generic[ModelT]):
    """Generic SQLAlchemy 2.0 async repository implementation."""

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, entity_id: UUID) -> ModelT | None:
        """Retrieve entity by primary key."""
        result = await self._session.get(self.model, entity_id)
        return result

    async def list(self, limit: int = 100, offset: int = 0) -> list[ModelT]:
        """Retrieve paginated list."""
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, entity: ModelT) -> ModelT:
        """Add entity to session and flush."""
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        """Delete entity by primary key."""
        entity = await self.get(entity_id)
        if entity is None:
            return False
        await self._session.delete(entity)
        await self._session.flush()
        return True
