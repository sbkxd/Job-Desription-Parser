# Changelog - JD Skill Extraction Pipeline

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2026-06-10

### Added
- Milestone 3.1: Preprocessing schemas (`app/preprocessing/schemas/schemas.py`) defining `SectionType`, `BoilerplateCategory`, `RawDocument`, `BoilerplateBlock`, `Section`, `SegmentedDocument`, and `SegmentationResult`.
- Milestone 3.2: Text Cleaning Pipeline (`app/preprocessing/cleaners/text_cleaner.py`) with 9 deterministic steps, smart quotes replacement, asterisk/dash bullet unification, and indent preservation.
- Milestone 3.3: Content Normalization alias resolution in `HeadingNormalizer` mapping raw headings to SectionType.
- Milestone 3.4: Boilerplate Detection (`app/preprocessing/classifiers/boilerplate_detector.py`) scanning 50+ patterns across 6 legal/marketing categories and tracking quarantined blocks.
- Milestone 3.5: Heading Detection Engine (`app/preprocessing/segmenters/heading_detector.py`) using exact alias, fuzzy match, and structural heuristics.
- Milestone 3.6: Section Segmenter (`app/preprocessing/segmenters/section_segmenter.py`) splitting lines at heading boundaries.
- Milestone 3.7: Section Classifier (`app/preprocessing/classifiers/section_classifier.py`) scoring content keywords combined with heading confidence.
- Milestone 3.8: Segmentation Service (`app/preprocessing/services/segmentation_service.py`) orchestrating and logging runs.
- Milestone 3.9: segment_jd.md Skill File (`skills/segment_jd.md`) few-shot prompts and rules.
- Milestone 3.10: Preprocessing API Endpoint (`POST /api/v1/preprocess/segment`).
- Milestone 3.11: 6 real-world input/expected fixture pairs and unit test suite achieving 92% overall project coverage.

### Fixed
- Fixed bug in `TextCleaner._collapse_horizontal_whitespace` which collapsed leading indentation spaces.
- Added dynamic suffix/prefix matching in normalizer for headings starting with "About ".
- Added "skills" alone mapping to REQUIREMENTS SectionType.

## [0.3.0] - 2026-06-10

### Added
- Milestone 2.1: Ingestion domain schemas (`app/ingestion/schemas/schemas.py`): `SourceType` (9 values), `FetchStatus` (5 values), `DocumentMetadata`, `FetchedDocument` with `to_output()` contract, `IngestionRequest` (validated URL, timeout bounds), `IngestionResponse`.
- Milestone 2.2: Source Detection Engine (`app/ingestion/detectors/url_detector.py`): `SourceDetector` classifies URLs to `SourceType`; handles Naukri, Foundit, Indeed, Greenhouse, Lever, Workable, Generic ATS (path-based), PDF, Unknown. `requires_javascript()` and `is_supported()` helpers. Module-level `detector` singleton.
- Milestone 2.3: Requests Fetcher (`app/ingestion/fetchers/requests_fetcher.py`): `RequestsFetcher` with 3-UA rotation pool, configurable retry/backoff, extra headers, redirect tracking, `FetchResult` dataclass. Context manager support.
- Milestone 2.4: Trafilatura Content Extractor (`app/ingestion/parsers/trafilatura_parser.py`): `TrafilaturaParser` with 3-tier extraction (primary → broad recall → BS4 fallback). `ParseResult` dataclass with metadata. Config-tuned for sparse JDs.
- Milestone 2.5: Playwright Fetcher (`app/ingestion/fetchers/playwright_fetcher.py`): `PlaywrightFetcher` async headless Chromium. Scroll-to-trigger, console error capture, bot-evasion headers. `PlaywrightResult` dataclass. Graceful degradation when Playwright not installed. Imported `ViewportSize` for type safety.
- 115 new unit tests for Phase 2 ingestion components (156 total, 89% coverage).

### Changed
- `app/logging/logger.py`: `configure_logging()` now accepts `log_level: str | None` and `json_logs: bool | None` keyword arguments so `app/main.py` can pass settings-derived values directly. JSON flag logic changed from `APP_ENV == LOCAL` to `APP_ENV != LOCAL` for clarity.
- `app/repositories/job_repository.py`: Removed three stale `# type: ignore[attr-defined]` comments now that MyPy resolves SQLAlchemy 2.0 `Mapped` column attributes natively.
- `app/repositories/skill_repository.py`: Removed stale `# type: ignore[attr-defined]` from `ilike()` call.
- `app/ingestion/parsers/trafilatura_parser.py`: Removed stale `# type: ignore[import-untyped]` from `bs4` import (stubs now resolvable).
- `app/ingestion/fetchers/playwright_fetcher.py`: Black auto-formatted; added `ViewportSize` import to fix `arg-type` MyPy error.

### Fixed
- MyPy: All 12 errors across 6 files resolved. `mypy app/` now reports `no issues found in 35 source files`.
- Black: All 35 `app/` source files now pass `black --check`.
- Ruff: All `app/` source files pass `ruff check`.

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
