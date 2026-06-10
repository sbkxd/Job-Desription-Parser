# Implementation Plan - JD Skill Extraction Pipeline

## Current Phase
- **Phase 3**: Configuration Layer

## Completed Phases
- **Phase 0**: Repository Initialization
- **Phase 1**: Environment Setup & Infrastructure
- **Phase 2**: CI/CD Foundation & Ingestion Framework

## Remaining Phases
- **Phase 3**: Configuration Layer (next)
- **Phase 4**: Database Layer
- **Phase 5**: Domain Models
- **Phase 6**: Ingestion Framework (advanced)
- **Phase 7**: Fetcher Implementations (advanced)
- **Phase 8**: Preprocessing Pipeline
- **Phase 9**: Skill Framework
- **Phase 10**: NER Infrastructure
- **Phase 11**: Skill Extraction
- **Phase 12**: Experience Extraction
- **Phase 13**: Seniority Extraction
- **Phase 14**: Requirement Classification
- **Phase 15**: ESCO Taxonomy Integration
- **Phase 16**: Normalization Engine
- **Phase 17**: Review Queue
- **Phase 18**: MCP Server
- **Phase 19**: Orchestration Layer
- **Phase 20**: REST APIs
- **Phase 21**: Observability
- **Phase 22**: Security
- **Phase 23**: Dockerization
- **Phase 24**: Documentation
- **Phase 25**: Cloud Readiness
- **Phase 26**: Performance Testing
- **Phase 27**: Production Hardening
- **Phase 28**: Final Release

## Key Decisions
1. **Ingestion Framework placed in Phase 2**: Source detection, fetchers (Requests + Playwright), content extraction (Trafilatura) and ingestion schemas were implemented alongside CI/CD to validate the full pipeline early.
2. **Playwright fetcher is mocked in tests**: Full browser tests are left for integration testing (Phase 2+ CI job). Unit tests use `_do_fetch` mocking to keep tests fast and dependency-free.
3. **BeautifulSoup as last-resort fallback**: Trafilatura is the primary extractor; BS4 is the final fallback if trafilatura returns nothing.

## Risks
1. **Dependency Versions**: Integrating DeBERTa-v3, FastAPI, and SQLAlchemy 2.0 requires careful dependency alignment.
2. **Performance Constraints**: NLP NER and embedding similarity checks might exceed the 2-second SLA. Mitigation: Caching and batch inference.
3. **Data Quality**: Ambiguous or unstructured JDs from different ATS types.
4. **Playwright in CI**: Chromium browser install adds ~300MB to CI images — considered acceptable.

## Assumptions
1. Python 3.11/3.12 is installed and standard tools (venv, pip) are functional.
2. PostgreSQL will be run locally or via Docker during subsequent phases.

## Architecture Decisions
1. **Framework**: FastAPI for API layer.
2. **ORM**: SQLAlchemy 2.0 with async engine configuration.
3. **NLP Engine**: Hugging Face DeBERTa-v3-small for Named Entity Recognition (NER), sentence-transformers for ESCO similarity mapping.
4. **Ingestion**: Requests for static pages, Playwright for JavaScript-heavy ATS pages.
5. **Content Extraction**: Trafilatura (primary) → Trafilatura broad-recall fallback → BeautifulSoup last resort.

## Technical Debt
- `app/logging/formatters.py` has 0% coverage (utility module, unused by current tests). To be addressed in Phase 21 (Observability).
- Playwright live browser integration tests deferred to Phase 2+ CI integration test job.

## Next Phase Goals (Phase 3: Configuration Layer)
1. Implement advanced configuration management for NLP model paths, ESCO taxonomy file paths, and pipeline tuning parameters.
2. Add environment-based feature flags (enable/disable playwright, ESCO matching, etc.).
3. Write corresponding unit tests for all new configuration surface area.
