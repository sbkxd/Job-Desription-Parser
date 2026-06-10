# Implementation Plan - JD Skill Extraction Pipeline

## Current Phase
- **Phase 5**: ESCO Normalization & Taxonomy Integration (next)

## Completed Phases
- **Phase 0**: Repository Initialization
- **Phase 1**: Environment Setup & Infrastructure
- **Phase 2**: CI/CD Foundation & Ingestion Framework
- **Phase 3**: Preprocessing & JD Segmentation
- **Phase 4**: Information Extraction Engine

## Remaining Phases
- **Phase 5**: ESCO Normalization & Taxonomy Integration
- **Phase 6**: Review Workflows & Review Queue
- **Phase 7**: MCP Tools
- **Phase 8**: Ollama Integration
- **Phase 9**: Deployment Enhancements & Cloud Readiness
- **Phase 10**: Observability, Security & Dockerization
- **Phase 11**: Production Hardening & Final Release

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

## Next Phase Goals (Phase 5: ESCO Normalization & Taxonomy Integration)
1. Set up ESCO Taxonomy dataset files and model loader.
2. Implement semantic search & mapping using sentence-transformers to map extracted skills to canonical ESCO terms.
3. Wire normalizer service to map skills, seniority levels, and requirements classifications.
4. Update API contracts and run validation checks.
