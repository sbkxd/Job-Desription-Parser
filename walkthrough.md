# Walkthrough - JD Skill Extraction Pipeline

## What Was Built

### Phase 1: Environment Setup & Infrastructure
- Initial repository scaffolding (Phase 0).
- Development tooling configuration (Milestone 1.1) including pre-commit, Black, Ruff, and MyPy.
- Centralized application settings (Milestone 1.2) using Pydantic Settings supporting environment overrides, and automatically calculating PostgreSQL async/sync URLs.
- Structured logging infrastructure (Milestone 1.3) using `structlog` for structured JSON output and request correlation tracking middleware.
- Database foundation layer (Milestone 1.4) configuring asynchronous SQLAlchemy engine and connection pooling.
- Alembic migration environment initialized (Milestone 1.5) — initial revision `3bc883988942` wired to project `Base` metadata.
- Core domain models (Milestone 1.6): `Job`, `Skill`, `JobSkill`, `ReviewQueue`, `ProcessingRun`, `AuditLog` with SQLAlchemy 2.0 `Mapped` annotations and cascade relationships. Alembic migration `a1b2c3d4e5f6` adds full schema.
- Repository pattern (Milestone 1.7): `AbstractRepository`, `SQLAlchemyRepository` base, `JobRepository`, `SkillRepository`.
- FastAPI application factory (Milestone 1.8): async lifespan management, CORS, structured logging middleware, `/api/v1/health/live` + `/api/v1/health/ready` endpoints.
- Testing foundation (Milestone 1.9): 41 unit tests, 94% coverage.
- CI/CD (Milestone 1.10): GitHub Actions workflow — lint, unit test, integration test jobs with PostgreSQL service container.

### Phase 2: Ingestion Framework
- **Ingestion Domain Schemas** (`app/ingestion/schemas/schemas.py`):
  - `SourceType` enum: `naukri`, `foundit`, `indeed`, `greenhouse`, `lever`, `workable`, `generic_ats`, `pdf`, `unknown`.
  - `FetchStatus` enum: `success`, `failed`, `partial`, `timeout`, `blocked`.
  - `DocumentMetadata`: captures OG tags, HTTP status, content type, word count, structured data.
  - `FetchedDocument`: normalized output schema with `to_output()` contract for downstream stages.
  - `IngestionRequest`: validated URL input (http/https only, 5–120s timeout bounds).
  - `IngestionResponse`: wraps success/failure with optional `FetchedDocument` and timing.

- **Source Detection Engine** (`app/ingestion/detectors/url_detector.py`):
  - `SourceDetector.detect(url)` — maps URL → `SourceType` using domain/path rules.
  - `requires_javascript(source_type)` — True for Greenhouse, Lever, Workable.
  - `is_supported(source_type)` — False for `UNKNOWN`.
  - Module-level `detector` singleton for convenience.

- **Requests Fetcher** (`app/ingestion/fetchers/requests_fetcher.py`):
  - `RequestsFetcher` — synchronous fetcher using `requests.Session`.
  - 3-UA rotation pool, configurable retry/backoff, `extra_headers` support.
  - Returns `FetchResult` dataclass: `url`, `html`, `status_code`, `content_type`, `duration_ms`, `final_url`, `success`, `error`, `response_headers`.
  - Context manager support (`with RequestsFetcher() as f:`).

- **Trafilatura Content Extractor** (`app/ingestion/parsers/trafilatura_parser.py`):
  - `TrafilaturaParser` — 3-tier extraction: primary Trafilatura → broad-recall Trafilatura → BS4 plaintext fallback.
  - Config-tuned for short JDs (`MIN_EXTRACTED_SIZE=200`, `MIN_DUPLCHECK_SIZE=100`).
  - Returns `ParseResult`: `raw_text`, `title`, `description`, `author`, `date`, `url`, `language`, `word_count`, `success`, `error`, `metadata`.
  - Never raises — all errors captured in `ParseResult.error`.

- **Playwright Fetcher** (`app/ingestion/fetchers/playwright_fetcher.py`):
  - `PlaywrightFetcher` — async headless Chromium fetcher.
  - Configurable timeout, wait strategy (`networkidle`/`load`/`domcontentloaded`), scroll-to-trigger lazy content.
  - Bot-evasion headers, console error capture.
  - Returns `PlaywrightResult` dataclass.
  - Graceful degradation when Playwright is not installed.
  - Never raises — all errors captured in `PlaywrightResult.error`.

### Phase 3: Preprocessing & JD Segmentation
- **Preprocessing Schemas** (`app/preprocessing/schemas/schemas.py`):
  - `SectionType` enum: `responsibilities`, `requirements`, `nice_to_have`, `about_company`, `benefits`, `other`.
  - `BoilerplateCategory` enum: `equal_opportunity`, `legal_disclaimer`, `privacy_statement`, `application_instructions`, `recruitment_marketing`, `generic_policy`.
  - `RawDocument`, `BoilerplateBlock`, `Section`, `SegmentedDocument`, `SegmentationResult` schemas.
- **Text Cleaning Pipeline** (`app/preprocessing/cleaners/text_cleaner.py`):
  - 9-step deterministic transformations normalizing whitespace, line-endings, and HTML entities.
  - Standardizes various unicode bullet characters to hyphenated prefix (`- `) while preserving indents.
- **Boilerplate Detection** (`app/preprocessing/classifiers/boilerplate_detector.py`):
  - Scans 50+ patterns across 6 categories. Removes boilerplate lines and preserves them for auditing.
- **Heading Detector & Normalizer** (`app/preprocessing/normalizers/heading_normalizer.py` & `app/preprocessing/segmenters/heading_detector.py`):
  - Classifies headings using an alias dictionary, RapidFuzz fuzzy matches, and structural heuristics.
- **Section Segmenter & Classifier** (`app/preprocessing/classifiers/section_classifier.py` & `app/preprocessing/segmenters/section_segmenter.py`):
  - Segments lines at heading boundaries. Classifies sections based on heading type and bag-of-words keyword rules.
- **Segmentation Service** (`app/preprocessing/services/segmentation_service.py`):
  - Orchestrates cleaning, boilerplate detection, and classification. Logs timing and outputs results.
- **Few-Shot Prompt Skill File** (`skills/segment_jd.md`):
  - Few-shot examples and parsing rules for LLMs.

### Phase 4: Information Extraction Engine
- **Extraction Domain Schemas** (`app/extraction/schemas/schemas.py`):
  - `SkillMention`, `ExperienceRequirement`, `SeniorityLevel`, `RequirementClassification`, and `ExtractionResult` using Pydantic v2.
- **Model Management & DeBERTa Loader** (`app/extraction/models/`):
  - `ModelManager` and `DebertaLoader` providing lazy-loading, singleton instantiation, CPU/GPU detection, caching, and clean lifecycle management.
- **Skills Extraction Engine** (`app/extraction/skills/skills_extractor.py`):
  - Dual-path skill extractor blending a regex Gazetteer (high precision) and DeBERTa-v3 NER model (high recall) for flexible detection. Includes post-processing logic (deduplication, casing resolution, and punctuation cleaning).
- **Experience Extraction Engine** (`app/extraction/experience/experience_extractor.py`):
  - Regular expression parser extracting experience bounds (`min_years` and `max_years`) handling plus notations, exact numbers, and ranges.
- **Seniority Extraction Engine** (`app/extraction/seniority/seniority_extractor.py`):
  - Classifier using title keyword checks, body text matching, and experience years fallback mapping.
- **Requirement Classifier** (`app/extraction/requirements/requirement_classifier.py`):
  - Deterministic rules identifying whether a sentence dictates a `Required`, `Preferred`, or `Optional` qualification.
- **Extraction Orchestrator** (`app/extraction/services/extraction_service.py`):
  - Orchestrator (`ExtractionService`) compiling outputs into a unified `ExtractionResult`.
- **Extraction Endpoint** (`POST /api/v1/extract`):
  - REST endpoint to trigger the information extraction pipeline.
- **Few-Shot Prompt Skill Files** (`skills/extract_skills.md` & `skills/classify_requirement.md`):
  - System prompts and rules for model evaluation.


## Why It Exists
- The settings module ensures the application fails fast if configuration is missing.
- Structured JSON logging provides machine-readable records for cloud environments.
- The dual-fetcher strategy handles both static ATS pages (cheaper) and JS-rendered boards (richer, required for Greenhouse/Lever/Workable).
- Trafilatura's content heuristics strip navigation, ads, and boilerplate — ideal for job descriptions.
- `FetchedDocument.to_output()` provides a stable contract for future NLP pipeline stages.
- Dual-path skills extraction ensures exact-match technical words (e.g. C++) are caught via Gazetteer, while long-tail terms are discovered by the NER classifier.
- Rule-based experience, seniority, and requirement classifiers provide stable baseline logic before LLM integrations.

## How It Works

### Ingestion Pipeline
1. `IngestionRequest` is validated (URL scheme, timeout bounds).
2. `SourceDetector.detect(url)` → `SourceType` determines fetcher choice.
3. If `requires_javascript(source_type)` → `PlaywrightFetcher.fetch(url)` (async).
4. Otherwise → `RequestsFetcher.fetch(url)` (sync).
5. Raw HTML is passed to `TrafilaturaParser.parse(html, url)` → `ParseResult`.
6. `FetchedDocument` is assembled from parse results and metadata.

### Preprocessing & Segmentation Pipeline
1. `RawDocument` text is normalized and cleaned via `TextCleaner`.
2. Cleaned text lines are evaluated for boilerplate via `BoilerplateDetector`. Matches are quarantined.
3. Remaining clean lines are segmented into raw sections on heading boundaries via `SectionSegmenter` using the `HeadingDetector` rules.
4. Each raw section is classified into a canonical `SectionType` and scored with a confidence score in `[0.0, 1.0]` by the `SectionClassifier`.
5. The `SegmentedDocument` is wrapped in a `SegmentationResult` and returned.

### Information Extraction Pipeline
1. `segmented_document` sections are fed into the orchestrator.
2. `SkillsExtractor` identifies raw skill mentions from responsibilities/requirements/nice-to_have sections, merges overlapping spans, resolves casings, and deduplicates them.
3. `ExperienceExtractor` parses years of experience bounds from requirements sections.
4. `SeniorityExtractor` evaluates title patterns and falls back to experience-years mapping.
5. `RequirementClassifier` maps requirement sentences to `Required`/`Preferred`/`Optional`.
6. Output is validated and compiled into an `ExtractionResult` Pydantic payload.


### Configure Logging
- `app/logging/logger.py`: `configure_logging(log_level?, json_logs?)` sets up structlog with environment-aware renderer.
- LOCAL environment → `ConsoleRenderer` (colored). Production → `JSONRenderer`.
- `json_logs` and `log_level` parameters allow `main.py` to override defaults from settings.

### Repository Pattern
- `SQLAlchemyRepository[T]` (generic base): `get`, `add`, `delete`, `list`.
- `JobRepository`: `list_by_status`, `list_pending_review`, `update_status`, `get_with_skills`.
- `SkillRepository`: `get_by_name`, `get_by_esco_code`, `search_by_category`, `get_or_create`.

## How to Run

### Start the Database
```bash
docker compose up db -d
```

### Run Alembic Migrations
```bash
.venv\Scripts\alembic upgrade head
```

### Start the API
```bash
.venv\Scripts\uvicorn app.main:app --reload
```

### API Endpoints Available
- `GET /api/v1/health/live` — Liveness probe
- `GET /api/v1/health/ready` — Readiness probe (checks DB)
- `POST /api/v1/preprocess/segment` — Preprocesses and segments raw JD text
- `POST /api/v1/extract` — Extracts structured skills, experience, seniority, and requirement types
- `GET /docs` — Swagger UI
- `GET /redoc` — ReDoc UI

## How to Test

Run full unit test suite with coverage:
```bash
.venv\Scripts\pytest tests/unit/ -v --cov=app --cov-report=term-missing
```

Run quality checks:
```bash
.venv\Scripts\python -m ruff check app/
.venv\Scripts\python -m black --check app/
.venv\Scripts\python -m mypy app/
```

### Test Coverage Summary (Phase 4 Complete)
| Module | Coverage |
|--------|----------|
| `app/config/` | 100% |
| `app/database/` | 92% |
| `app/logging/` | 95% |
| `app/models/models.py` | 100% |
| `app/repositories/` | 83% |
| `app/ingestion/` | 82% (Playwright live paths mocked) |
| `app/preprocessing/` | 94% |
| `app/extraction/` | 91% |
| **Total** | **92%** |
