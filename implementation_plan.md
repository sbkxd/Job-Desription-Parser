# Implementation Plan - JD Skill Extraction Pipeline

## Current Phase
- **Phase 8**: Wait for Phase 8 instructions (pending)

## Completed Phases
- **Phase 0**: Repository Initialization
- **Phase 1**: Environment Setup & Infrastructure
- **Phase 2**: CI/CD Foundation & Ingestion Framework
- **Phase 3**: Preprocessing & JD Segmentation
- **Phase 4**: Information Extraction Engine
- **Phase 5**: ESCO Normalization & Taxonomy Integration
- **Phase 6**: Review System, Taxonomy Gaps & Quality Control
- **Phase 7**: LangGraph Orchestration, MCP Tools & Ollama Integration

## Remaining Phases
- **Phase 8**: Production Hardening & Benchmarking (or as requested)
- **Phase 9**: Deployment Enhancements & Cloud Readiness
- **Phase 10**: Observability, Security & Dockerization
- **Phase 11**: Production Hardening & Final Release

## Key Decisions
1. **Ingestion Framework placed in Phase 2**: Source detection, fetchers (Requests + Playwright), content extraction (Trafilatura) and ingestion schemas were implemented alongside CI/CD to validate the full pipeline early.
2. **Playwright fetcher is mocked in tests**: Full browser tests are left for integration testing (Phase 2+ CI job). Unit tests use `_do_fetch` mocking to keep tests fast and dependency-free.
3. **BeautifulSoup as last-resort fallback**: Trafilatura is the primary extractor; BS4 is the final fallback if trafilatura returns nothing.
4. **Cascade normalizer & Quality control engine**: Designed a multi-layered match-and-rank normalization cascade with a quality control review queue to capture, flag, and audit edge cases.
5. **LangGraph Central Execution Engine**: Consolidated previously decoupled NLP processing stages into a single orchestrated graph-based flow.
6. **Ollama Integration as Fallback**: Restated deterministic pipeline components as primary sources of truth, using local LLM (Qwen3:4B) dynamically as fallback only for low-confidence or out-of-taxonomy items.

## Risks
1. **Dependency Versions**: Integrating DeBERTa-v3, FastAPI, and SQLAlchemy 2.0 requires careful dependency alignment.
2. **Performance Constraints**: NLP NER and embedding similarity checks might exceed the 2-second SLA. Mitigation: Caching and batch inference.
3. **Data Quality**: Ambiguous or unstructured JDs from different ATS types.
4. **Playwright in CI**: Chromium browser install adds ~300MB to CI images — considered acceptable.
5. **LLM Inference Latency**: Local Ollama execution adds latency. Mitigation: Conditional execution only on low confidence.

## Assumptions
1. Python 3.11/3.12 is installed and standard tools (venv, pip) are functional.
2. PostgreSQL will be run locally or via Docker during subsequent phases.
3. Ollama server is running locally on port 11434 with `qwen3:4b` available.

## Architecture Decisions
1. **Framework**: FastAPI for API layer.
2. **ORM**: SQLAlchemy 2.0 with async engine configuration.
3. **NLP Engine**: Hugging Face DeBERTa-v3-small for Named Entity Recognition (NER), sentence-transformers for ESCO similarity mapping.
4. **Ingestion**: Requests for static pages, Playwright for JavaScript-heavy ATS pages.
5. **Content Extraction**: Trafilatura (primary) → Trafilatura broad-recall fallback → BeautifulSoup last resort.
6. **Review Queue State Machine**: Tracks pending, in-review, approved, rejected, and corrected states, with persistent DB auditing.
7. **Orchestrator**: LangGraph StateGraph controlling Fetch, Segment, Extract, Normalize, Review Evaluation, Ollama Resolution, Review Queue, and Persistence.
8. **MCP Framework**: Custom MCP Base Tool and Registry classes wrapping fetch, ner, lookup, and save services.

## Technical Debt
- `app/logging/formatters.py` has 0% coverage (utility module, unused by current tests). To be addressed in Phase 21 (Observability).
- Playwright live browser integration tests deferred to Phase 2+ CI integration test job.

## Next Phase Goals (Phase 8)
- As directed by user instructions for Phase 8.
