# Changelog - JD Skill Extraction Pipeline

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-06-09
### Added
- Milestone 1.5: Alembic initialized; initial revision `3bc883988942`; `env.py` wired to project `Base` metadata.
- Milestone 1.6: Core domain models (`Job`, `Skill`, `JobSkill`, `ReviewQueue`, `ProcessingRun`, `AuditLog`) with SQLAlchemy 2.0 `Mapped` annotations, cascade relationships, and DB indexes.
- Milestone 1.6: Alembic migration `a1b2c3d4e5f6_add_core_domain_models.py` — full handcrafted schema for all 6 tables with PostgreSQL enums and FK constraints.
- Milestone 1.7: Repository pattern — `AbstractRepository`, `SQLAlchemyRepository` base, `JobRepository` (with `list_by_status`, `update_status`, `get_with_skills`), `SkillRepository` (with `get_or_create`, `get_by_esco_code`).
- Milestone 1.8: FastAPI application factory (`app/main.py`) with async lifespan management, CORS middleware, structured logging middleware.
- Milestone 1.8: Health API endpoints (`GET /api/v1/health/live`, `GET /api/v1/health/ready`) with Kubernetes probe semantics.
- Milestone 1.9: 41 unit tests passing; 94% overall coverage.
- Milestone 1.10: GitHub Actions CI workflow (`.github/workflows/ci.yml`) — lint, unit test, and integration test jobs with PostgreSQL service container.

## [0.1.0] - 2026-06-09
### Added
- Milestone 1.1: Development tooling configuration (Black, Ruff, MyPy, pre-commit, pytest).
- Milestone 1.2: Centralized application configuration using Pydantic Settings (`app/config/settings.py`, `constants.py`, `environment.py`) with environment-based overrides and computed properties.
- Milestone 1.3: Structured JSON logging framework using `structlog` and custom correlation ID tracking middleware (`app/logging/logger.py`, `middleware.py`, `formatters.py`).
- Milestone 1.4: Database foundation layer setup with async SQLAlchemy 2.0 engine, pool configuration, declarative Base and async session management (`app/database/base.py`, `engine.py`, `session.py`).
- Unit tests for configuration, logging, and database layers (`tests/unit/test_config.py`, `tests/unit/test_logging.py`, `tests/unit/test_database.py`).

## [0.0.0] - 2026-06-09
### Added
- Phase 0: Initialized directory scaffolding (`app/`, `docs/`, `skills/`, `mcp/`, `tests/`, `infra/`, `scripts/`, `.github/`).
- Repository-level README.md, LICENSE, .gitignore, mkdocs.yml, pyproject.toml, Dockerfile, and docker-compose.yml.
- Core management artifacts: implementation_plan.md, tasks.md, architecture.md, walkthrough.md, intent_matrix_results.md.
