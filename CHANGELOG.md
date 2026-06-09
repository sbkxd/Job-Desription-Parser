# Changelog - JD Skill Extraction Pipeline

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
