"""Database engine factory and lifecycle management."""

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.config.settings import Settings
from app.config.settings import settings as _default_settings


def _build_engine(s: Settings) -> AsyncEngine:
    """Build a configured async SQLAlchemy engine."""
    return create_async_engine(
        s.database_url,
        echo=s.DEBUG,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )


# Module-level engine — used by Alembic and session factory
engine: AsyncEngine = _build_engine(_default_settings)


async def create_db_engine(s: Settings) -> AsyncEngine:
    """Create and return a new async engine (for lifespan usage)."""
    return _build_engine(s)


async def dispose_engine(eng: AsyncEngine) -> None:
    """Gracefully dispose of a database engine."""
    await eng.dispose()
