import time
import uuid

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Generate or extract request correlation ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Bind request_id to structlog context vars (thread/async safe context)
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_time = time.perf_counter()

        logger.info(
            "Incoming request",
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params),
        )

        try:
            response = await call_next(request)

            # Attach X-Request-ID to response headers
            response.headers["X-Request-ID"] = request_id

            duration = time.perf_counter() - start_time
            logger.info(
                "Request processed successfully",
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
            )
            return response

        except Exception as exc:
            duration = time.perf_counter() - start_time
            logger.error(
                "Request failed",
                error=str(exc),
                duration_ms=round(duration * 1000, 2),
                exc_info=True,
            )
            raise exc
