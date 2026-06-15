# Implementation Plan - JD Skill Extraction Pipeline

## Current Phase
- **Phase 10**: Deployment Enhancements & Cloud Readiness

## Completed Phases
- **Phase 0**: Repository Initialization
- **Phase 1**: Environment Setup & Infrastructure
- **Phase 2**: CI/CD Foundation & Ingestion Framework
- **Phase 3**: Preprocessing & JD Segmentation
- **Phase 3.5**: JD Noise Filtering, Section Purification & Content Quality Hardening
- **Phase 4**: Information Extraction Engine
- **Phase 5**: ESCO Normalization & Taxonomy Integration
- **Phase 6**: Review System, Taxonomy Gaps & Quality Control
- **Phase 7**: LangGraph Orchestration, MCP Tools & Ollama Integration
- **Phase 8**: Mistral Small Latest Migration
- **Phase 8A**: Complete Frontend Implementation
- **Phase 9**: Final Output Formatter Integration

## Remaining Phases
- **Phase 11**: Observability, Security & Dockerization
- **Phase 12**: Production Hardening & Final Release

## Key Decisions
1. **Ingestion Framework placed in Phase 2**: Source detection, fetchers (Requests + Playwright), content extraction (Trafilatura) and ingestion schemas were implemented alongside CI/CD to validate the full pipeline early.
2. **Playwright fetcher is mocked in tests**: Full browser tests are left for integration testing (Phase 2+ CI job). Unit tests use `_do_fetch` mocking to keep tests fast and dependency-free.
3. **BeautifulSoup as last-resort fallback**: Trafilatura is the primary extractor; BS4 is the final fallback if trafilatura returns nothing.
4. **Cascade normalizer & Quality control engine**: Designed a multi-layered match-and-rank normalization cascade with a quality control review queue to capture, flag, and audit edge cases.
5. **LangGraph Central Execution Engine**: Consolidated previously decoupled NLP processing stages into a single orchestrated graph-based flow.
6. **Ollama Integration as Fallback**: Restated deterministic pipeline components as primary sources of truth, using local LLM (Qwen3:4B) dynamically as fallback only for low-confidence or out-of-taxonomy items.
7. **Production response formatting (Phase 9)**: Created a dedicated presentation layer `app/presentation/` returning `JobIntelligenceReport` as the public API contract, separating internal execution details into debug endpoints.
8. **Persistence of PipelineState**: Added a `pipeline_state` JSON column in the `processing_runs` table to allow robust retrieval of full states via `GET /api/v1/pipeline/debug/{job_id}` without bloating the `jobs` table.

## Risks
1. **Database Schema Changes**: Adding JSON/JSONB column to `processing_runs` requires an Alembic migration. We will generate the migration using Alembic to ensure zero manual alterations.
2. **Performance Constraints**: NLP NER and embedding similarity checks might exceed the 2-second SLA. Mitigation: Caching and batch inference.
3. **Data Quality**: Ambiguous or unstructured JDs from different ATS types.
4. **Playwright in CI**: Chromium browser install adds ~300MB to CI images — considered acceptable.
5. **LLM Inference Latency**: Local Ollama execution adds latency. Mitigation: Conditional execution only on low confidence.

## Assumptions
1. Python 3.11/3.12 is installed and standard tools (venv, pip) are functional.
2. PostgreSQL will be run locally or via Docker during subsequent phases.

## Architecture Decisions
1. **Framework**: FastAPI for API layer.
2. **ORM**: SQLAlchemy 2.0 with async engine configuration.
3. **NLP Engine**: Hugging Face DeBERTa-v3-small for Named Entity Recognition (NER), sentence-transformers for ESCO similarity mapping.
4. **Ingestion**: Requests for static pages, Playwright for JavaScript-heavy ATS pages.
5. **Content Extraction**: Trafilatura (primary) → Trafilatura broad-recall fallback → BeautifulSoup last resort.
6. **Review Queue State Machine**: Tracks pending, in-review, approved, rejected, and corrected states, with persistent DB auditing.
7. **Orchestrator**: LangGraph StateGraph controlling Fetch, Segment, Extract, Normalize, Review Evaluation, Ollama Resolution, Review Queue, and Persistence.
8. **MCP Framework**: Custom MCP Base Tool and Registry classes wrapping fetch, ner, lookup, and save services.
9. **Presentation Layer**: Formatting service (`app/presentation/formatters/job_intelligence_formatter.py`) converting `PipelineState` dicts to `JobIntelligenceReport` Pydantic models.

## Technical Debt
- `app/logging/formatters.py` has 0% coverage (utility module, unused by current tests). To be addressed in Phase 21 (Observability).
- Playwright live browser integration tests deferred to Phase 2+ CI integration test job.

## Next Phase Goals (Phase 9)
1. Design Pydantic models in [job_intelligence.py](file:///d:/Altrosyn%20-%20JD%20Parser/JD%20Parser/app/presentation/schemas/job_intelligence.py) and [api_responses.py](file:///d:/Altrosyn%20-%20JD%20Parser/JD%20Parser/app/presentation/schemas/api_responses.py).
2. Implement [job_intelligence_formatter.py](file:///d:/Altrosyn%20-%20JD%20Parser/JD%20Parser/app/presentation/formatters/job_intelligence_formatter.py) and [response_builder.py](file:///d:/Altrosyn%20-%20JD%20Parser/JD%20Parser/app/presentation/formatters/response_builder.py).
3. Create Alembic migration to add `pipeline_state` JSON column to `processing_runs` table, update [models.py](file:///d:/Altrosyn%20-%20JD%20Parser/JD%20Parser/app/models/models.py).
4. Save the finalized `PipelineState` JSON in `PipelineService` upon successful run.
5. Update pipeline endpoints to return `JobIntelligenceReport`.
6. Add [debug.py](file:///d:/Altrosyn%20-%20JD%20Parser/JD%20Parser/app/api/v1/endpoints/debug.py) endpoint `GET /api/v1/pipeline/debug/{job_id}` returning full state.
7. Update documentation: `architecture.md`, `walkthrough.md`.

## Verification Plan

### Automated Tests
- Run `.venv\Scripts\python -m pytest` verifying all 259 existing tests pass.
- Write new unit tests in `tests/unit/test_presentation.py` covering Pydantic models, formatters, and endpoints.
- Run `ruff check app/` ensuring strict code quality.

### Manual Verification
- Deploy and execute parsing E2E, checking JSON response format against Swagger UI.
- Verify `GET /api/v1/pipeline/debug/{job_id}` retrieves the full internal pipeline state.
