"""Health and readiness endpoints."""

import time
from typing import Any

import structlog
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from app.config.settings import get_settings

router = APIRouter()
logger = structlog.get_logger(__name__)
settings = get_settings()

_START_TIME = time.time()


@router.get(
    "/live",
    summary="Liveness probe",
    response_description="Returns 200 when the service is alive",
    status_code=status.HTTP_200_OK,
)
async def liveness() -> dict[str, Any]:
    """Kubernetes liveness probe — confirms the process is running."""
    return {
        "status": "alive",
        "app": settings.app_name,
        "version": settings.app_version,
        "uptime_seconds": round(time.time() - _START_TIME, 2),
    }


@router.get(
    "/ready",
    summary="Readiness probe",
    response_description="Returns 200 when the service is ready to handle traffic",
)
async def readiness(request: Request) -> JSONResponse:
    """Kubernetes readiness probe — confirms DB connectivity."""
    checks: dict[str, str] = {}

    # Database check
    db_ok = False
    engine = getattr(request.app.state, "db_engine", None)
    if engine is not None:
        try:
            async with engine.connect() as conn:
                await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
            checks["database"] = "ok"
            db_ok = True
        except Exception as exc:
            logger.warning("readiness_db_check_failed", error=str(exc))
            checks["database"] = f"error: {exc}"
    else:
        checks["database"] = "engine_not_initialized"

    all_ok = db_ok
    http_status = status.HTTP_200_OK if all_ok else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=http_status,
        content={
            "status": "ready" if all_ok else "not_ready",
            "checks": checks,
        },
    )
