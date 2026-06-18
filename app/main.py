"""FastAPI application factory and lifespan management."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.database.engine import create_db_engine, dispose_engine
from app.logging.logger import configure_logging
from app.logging.middleware import LoggingMiddleware

logger = structlog.get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown lifecycle."""
    configure_logging(log_level=settings.log_level, json_logs=settings.json_logs)
    log = structlog.get_logger(__name__)

    log.info(
        "application_starting",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )

    # Initialize database engine
    engine = await create_db_engine(settings)
    app.state.db_engine = engine

    log.info("database_engine_initialized")
    yield

    # Teardown
    await dispose_engine(engine)
    log.info("application_shutdown")


def create_app() -> FastAPI:
    """Application factory — creates and configures the FastAPI app."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Enterprise-grade Job Description Skill Extraction Pipeline API",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Middleware
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    from app.api.v1.endpoints.compatibility_api import (
        router as compatibility_router,  # noqa: PLC0415
    )
    from app.api.v1.endpoints.recommendations_api import (
        router as recommendations_router,  # noqa: PLC0415
    )
    from app.api.v1.endpoints.resume_api import router as resume_router  # noqa: PLC0415
    from app.api.v1.router import api_router  # noqa: PLC0415

    app.include_router(api_router, prefix="/api/v1")
    app.include_router(resume_router, prefix="/resume", tags=["Resume"])
    app.include_router(
        compatibility_router, prefix="/compatibility", tags=["Compatibility"]
    )
    app.include_router(
        recommendations_router, prefix="/resume", tags=["Recommendations"]
    )

    return app


app = create_app()
