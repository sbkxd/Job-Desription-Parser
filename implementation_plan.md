# Implementation Plan - JD Skill Extraction Pipeline

## Current Phase
- **Phase 0: Repository Initialization**

## Completed Phases
*None*

## Remaining Phases
- **Phase 1**: Environment Setup
- **Phase 2**: CI/CD Foundation
- **Phase 3**: Configuration Layer
- **Phase 4**: Database Layer
- **Phase 5**: Domain Models
- **Phase 6**: Ingestion Framework
- **Phase 7**: Fetcher Implementations
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

## Risks
1. **Dependency Versions**: Integrating DeBERTa-v3, FastAPI, and SQLAlchemy 2.0 requires careful dependency alignment.
2. **Performance Constraints**: NLP NER and embedding similarity checks might exceed the 2-second SLA. Mitigation: Caching and batch inference.
3. **Data Quality**: Ambiguous or unstructured JDs from different ATS types.

## Assumptions
1. Python 3.11/3.12 is installed and standard tools (venv, pip) are functional.
2. PostgreSQL will be run locally or via Docker during subsequent phases.

## Architecture Decisions
1. **Framework**: FastAPI for API layer.
2. **ORM**: SQLAlchemy 2.0 with async engine configuration.
3. **NLP Engine**: Hugging Face DeBERTa-v3-small for Named Entity Recognition (NER), sentence-transformers for ESCO similarity mapping.

## Technical Debt
*None (Greenfield project)*

## Next Actions
1. Complete Phase 0 by verifying scaffolding and committing.
2. Initiate Phase 1 (Environment Setup with pyproject.toml, dependency managers, formatters/linters).
