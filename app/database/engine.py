from sqlalchemy.ext.asyncio import create_async_engine

from app.config.settings import settings

# Create async engine with pooling parameters suited for production
engine = create_async_engine(
    settings.database_url,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)
