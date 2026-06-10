import logging
import sys
from typing import Any, cast

import structlog

from app.config.environment import AppEnv
from app.config.settings import settings


def configure_logging(
    log_level: str | None = None,
    json_logs: bool | None = None,
) -> None:
    """Configure structlog and standard logging.

    Args:
        log_level: Override the log level from settings (e.g. 'INFO', 'DEBUG').
        json_logs: Override whether to emit JSON logs (True) or console logs (False).
                   Defaults to False for LOCAL environment, True otherwise.
    """
    # Resolve level
    level_name: str = log_level or settings.LOG_LEVEL
    level: int = getattr(logging, level_name.upper(), logging.INFO)

    # Resolve JSON flag
    use_json: bool
    if json_logs is not None:
        use_json = json_logs
    else:
        use_json = settings.APP_ENV != AppEnv.LOCAL

    # Define structlog processors
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Select formatter/renderer based on environment
    renderer: Any
    if not use_json:
        # Development environment: clean colored logs
        renderer = structlog.dev.ConsoleRenderer(colors=True)
    else:
        # Production/Docker environment: structured JSON logs
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging to use structlog formatting
    handler = logging.StreamHandler(sys.stdout)
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(level)

    # Prevent logs from standard libraries from drowning out app logs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)


configure_logging()


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger(name))
