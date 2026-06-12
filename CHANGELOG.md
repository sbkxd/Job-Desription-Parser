# Changelog - JD Skill Extraction Pipeline

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.10.0] - 2026-06-12

### Added
- Created `app/presentation/` directory for public response presentation layer.
- Added `JobIntelligenceReport` Pydantic response models in `app/presentation/schemas/job_intelligence.py` defining clean business-facing contracts.
- Implemented `JobIntelligenceFormatter` under `app/presentation/formatters/job_intelligence_formatter.py` to aggregate, format, and structure raw pipeline states, including required/preferred skill classification and boilerplate text cleanup.
- Added `ResponseBuilder` helper class under `app/presentation/formatters/response_builder.py`.
- Added Alembic migration (`91c8b91e6e90`) adding `pipeline_state` JSON column to `processing_runs` table for persistent debugging.
- Implemented debug endpoint `GET /api/v1/pipeline/debug/{job_id}` to retrieve raw PipelineState.
- Created `tests/unit/test_presentation.py` covering all presentation schemas, formatters, and endpoints.

### Changed
- Updated E2E endpoints `/run/url` and `/run/pdf` to return `JobIntelligenceReport` instead of internal graph state.
- Updated `PipelineService.run_pipeline` to persist final `PipelineState` JSON in `processing_runs` database records.

## [0.9.0] - 2026-06-12

### Added
- Official Mistral Async API Client (`MistralClient`) under `app/orchestration/mistral/` utilizing `mistralai` Speakeasy SDK.
- Dynamic retry handling with exponential backoff, structured JSON response formatting, and configuration timeout limits.
- Automated token consumption, API latency, error metrics logging and secret masking.
- `MistralResolutionNode` replacing the deprecated `OllamaResolutionNode` inside LangGraph.
- Schema validation checking bounds and structure of LLM responses using Pydantic.
- Comprehensive mocked unit tests for the Mistral client, response parser, prompt builder, and E2E pipeline nodes.

### Changed
- Replaced all local Ollama/Qwen3:4B workflow dependencies and references with Mistral Small Latest.
- Updated `PipelineState` to hold `mistral_result` and routing state to use `needs_mistral`.
- Standardized imports and formatting conforming to MyPy, Black, and Ruff styles.

### Removed
- Deleted deprecated `app/orchestration/ollama/` directory and components.
- Deleted `ollama_resolution_node.py` and its corresponding tests.

### Added
- Milestone 7.1: Pipeline State Design (`PipelineState` TypedDict with merge list/dict reducers).
- Milestone 7.2: LangGraph Foundation (StateGraph pipeline workflow setup, node/edge registration, and Edge routing).
- Milestone 7.3: Fetch JD Node executing ingestion fetchers (Requests and Playwright).
- Milestone 7.4: Segment JD Node running preprocessing segmentation logic.
- Milestone 7.5: Extraction Node calling information extraction services.
- Milestone 7.6: Normalization Node matching skills against the ESCO taxonomy.
- Milestone 7.7: Review Evaluation Node checking match confidence to decide conditional routing.
- Milestone 7.8: Conditional Routing edge routing logic utilizing `ReviewRouter`.
- Milestone 7.9: Ollama Client qwen3:4b adapter with retries and structured JSON formatting.
- Milestone 7.10: Ollama Resolution Node fallback resolver for low-confidence or out-of-taxonomy skills.
- Milestone 7.11: Review Queue Node registering items to the review manager database tables.
- Milestone 7.12: Persistence Node saving full parsing runs and entities to Job and Skill databases.
- Milestone 7.13: MCP Tool Framework defining BaseMCPTool interface and tool registration.
- Milestone 7.14: MCP Tool `fetch_jd` wrapper tool.
- Milestone 7.15: MCP Tool `run_ner` extraction wrapper tool.
- Milestone 7.16: MCP Tool `lookup_taxonomy` normalization wrapper tool.
- Milestone 7.17: MCP Tool `save_parsed_jd` persistence wrapper tool.
- Milestone 7.18: Execution Audit System recording events to `pipeline_events` and `processing_runs` DB tables.
- Milestone 7.19: Graph Visualization auto-generating mermaid flow markdown in `docs/graphs/pipeline_flow.md`.
- Milestone 7.20: Pipeline HTTP endpoint API router `/api/v1/pipeline/run`.

### Fixed
- Fixed MCP execute signatures for Liskov substitution correctness under strict MyPy check.
- Fixed mock targets and setup inside `test_mcp_tools.py` and `test_langgraph_e2e.py` to correctly bind mocks before import time graph compiles.

## [0.7.0] - 2026-06-10

### Added
- Milestone 6.1: Review Schemas using Pydantic v2.
- Milestone 6.2: Confidence Evaluation Engine mapping match scores to ReviewStatus and reason with configurable thresholds.
- Milestone 6.3: Out-of-Taxonomy Detector classifying skills not in ESCO (e.g. LangChain, CrewAI) and returning review flag.
- Milestone 6.4: Custom Taxonomy Loader and Framework to load user-defined extensions alongside canonical ESCO.
- Milestone 6.5: Review Queue System manager layer with support for PENDING, IN_REVIEW, APPROVED, REJECTED, and CORRECTED states.
- Milestone 6.6: Review Decision Engine processing decisions (approve, reject, correct) and updating JobSkill mapping.
- Milestone 6.7: Audit Trail System tracking review action histories.
- Milestone 6.8: Review Orchestration Service (`ReviewService`) implementing the complete quality control pipeline.
- Milestone 6.9: `skills/review_flag.md` system prompt and guidelines with strict JSON output schema.
- Milestone 6.10: Review APIs (`GET /reviews`, `GET /reviews/{id}`, `POST /reviews/{id}/approve`, `reject`, `correct`).
- Milestone 6.11: Review datasets and fixture configuration (`tests/fixtures/review/review_fixtures.json`).
- Milestone 6.12: Database Alembic migration adding `in_review` and `corrected` to `reviewstatus` enum in PostgreSQL.

### Fixed
- Fixed C901 cognitive complexity in `submit_decision` by refactoring into smaller, structured helper methods.
- Resolved generic `dict` type annotations to `dict[str, Any]` to conform with strict MyPy validation settings.

## [0.6.0] - 2026-06-10

### Added
- Milestone 5.1: Normalization Schemas (Pydantic v2 schemas: `RawSkill`, `EscoSkill`, `SkillCandidate`, `NormalizedSkill`, `MatchResult`, `NormalizationResult`).
- Milestone 5.2 & 5.3: Local ESCO Taxonomy Ingestion Loader and Repository with in-memory indexes and precomputed sentence embeddings.
- Milestone 5.4: Skill Preprocessing engine supporting suffix cleaning, lowercasing, and whitespace normalization.
- Milestone 5.5: Exact Match Engine verifying exact case-insensitive matches against canonical skills with 1.0 confidence.
- Milestone 5.6: Alias Matching engine supporting known variants (e.g. `ReactJS` -> `React`) with 0.95 confidence.
- Milestone 5.7: Fuzzy Match Engine utilizing RapidFuzz for distance similarity matching.
- Milestone 5.8: Embedding Match Engine computing cosine similarity against taxonomy embeddings using sentence-transformers `all-MiniLM-L6-v2`.
- Milestone 5.9 & 5.10: Candidate Ranking and Confidence Engines aggregating scores across matchers.
- Milestone 5.11: `SkillNormalizationService` orchestrating the multi-layered match-and-rank pipeline.
- Milestone 5.12: System prompts and edge-case instructions in `skills/normalize_skill.md`.
- Milestone 5.13: Normalization API endpoint `POST /api/v1/normalize/skills`.
- Milestone 5.14: Ingestion of software, ML, database, and devops skill fixtures in `tests/fixtures/normalization/skills_fixtures.json`.

### Fixed
- Fixed mypy validation issues in `np.linalg.norm` typing and repository `_initialized` class variable checks.
- Formatted normalization module and test files using Black.
- Cleaned and checked code quality using Ruff.

## [0.5.0] - 2026-06-10

### Added
- Milestone 4.1: Extraction Schemas defining Pydantic v2 schemas (`SkillMention`, `ExperienceRequirement`, `SeniorityLevel`, `RequirementClassification`, `ExtractionResult`).
- Milestone 4.2: Model Management Layer (`ModelManager` & `DebertaLoader`) for lazy-loading DeBERTa models.
- Milestone 4.3 & 4.4: Skill Extraction & Post-processing combining Gazetteer and DeBERTa NER, sorting/deduplicating listings.
- Milestone 4.5: Experience Extraction regex rule parsing for numeric minimum/maximum bounds.
- Milestone 4.6: Seniority Extraction scan title keywords and experience fallback rules.
- Milestone 4.7: Requirement Classification deterministic rules for Required, Preferred, Optional.
- Milestone 4.8: Extraction Service coordinating downstream extraction.
- Milestone 4.9: Skill documents (`skills/extract_skills.md`, `skills/classify_requirement.md`).
- Milestone 4.10: Extraction API endpoint (`POST /api/v1/extract`).
- Milestone 4.11: 5 Representative input/expected JSON datasets under `tests/fixtures/extraction/` and unit/integration test suites.

### Fixed
- Fixed seniority experience fallback mapping to classify experience >= 2.0 as "Mid".
- Restructured `SeniorityExtractor.extract` into helper methods to reduce complexity from 21 to 10 (C901).
- Swapped deprecated `example` argument in Pydantic `Field` for `json_schema_extra`.

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
