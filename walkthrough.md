# Walkthrough - JD Skill Extraction Pipeline

## What Was Built
- Initial repository scaffolding (Phase 0).
- Development tooling configuration (Milestone 1.1) including pre-commit, Black, Ruff, and MyPy.
- Centralized application settings (Milestone 1.2) using Pydantic Settings supporting environment overrides, and automatically calculating PostgreSQL async/sync URLs.
- Structured logging infrastructure (Milestone 1.3) using `structlog` for structured JSON output and request correlation tracking middleware.
- Database foundation layer (Milestone 1.4) configuring asynchronous SQLAlchemy engine and connection pooling.

## Why It Exists
- The settings module (`app/config/settings.py`) provides validation for all system-level configuration parameters, ensuring the application fails fast if configuration is missing or invalid.
- Structured JSON logging provides machine-readable log records for cloud environments, and request ID correlation ensures all log messages for a given API request can be grouped together.
- Database foundation layer provides async support for PostgreSQL interaction, enabling high performance under concurrent API load.

## How It Works
1. `app/config/settings.py`: Declares `Settings` model sub-classing `BaseSettings` which reads variables from environment or a `.env` file.
2. `app/config/environment.py`: Contains `AppEnv` Enum (local, dev, staging, prod).
3. `app/config/constants.py`: Stores default configuration values.
4. Computed properties `database_url` and `sync_database_url` build valid PostgreSQL connection URIs dynamically.
5. `app/logging/logger.py`: Configures `structlog` with JSON/Console renderers and stdlib integration.
6. `app/logging/middleware.py`: FastAPI middleware generating/propagating `X-Request-ID` header and context variables.
7. `app/database/base.py`: Declares the SQLAlchemy declarative `Base` model.
8. `app/database/engine.py`: Builds async SQLAlchemy engine utilizing `asyncpg` with a connection pool size of 10 and max overflow of 20.
9. `app/database/session.py`: Exposes `async_session_maker` and `get_db_session()` dependency generator.

## How to Run
- Run PostgreSQL via Docker Compose:
  ```bash
  docker compose up db -d
  ```

## How to Test
Run pytest inside the virtual environment:
```bash
.\.venv\Scripts\pytest
```
This runs the configuration tests in `tests/unit/test_config.py`, logging tests in `tests/unit/test_logging.py`, and database tests in `tests/unit/test_database.py`.
