# Tasks - JD Skill Extraction Pipeline

## Pending
- **Phase 7**: MCP Tools
- **Phase 8**: Ollama Integration
- **Phase 9**: Deployment Enhancements & Cloud Readiness
- **Phase 10**: Observability, Security & Dockerization
- **Phase 11**: Production Hardening & Final Release

## In Progress
*None*

## Blocked
*None*

## Completed
- **Phase 6: Review System, Taxonomy Gaps & Quality Control**
  - [x] Milestone 6.1: Review Schemas (`app/review/schemas/schemas.py`)
  - [x] Milestone 6.2: Confidence Evaluation Engine (`app/review/evaluators/confidence_evaluator.py`)
  - [x] Milestone 6.3: Out-of-Taxonomy Detector (`app/review/evaluators/out_of_taxonomy.py`)
  - [x] Milestone 6.4: Custom Taxonomy Extension Framework (`app/normalization/loaders/custom_taxonomy_loader.py`)
  - [x] Milestone 6.5: Review Queue System (`app/review/queues/queue_manager.py`)
  - [x] Milestone 6.6: Review Decision Engine (`app/review/decisions/decision_engine.py`)
  - [x] Milestone 6.7: Audit Trail System (`app/review/audit/audit_trail.py`)
  - [x] Milestone 6.8: Review Orchestration Service (`app/review/services/review_service.py`)
  - [x] Milestone 6.9: review_flag.md Skill File (`skills/review_flag.md`)
  - [x] Milestone 6.10: Review APIs (`app/api/v1/endpoints/review.py`)
  - [x] Milestone 6.11: Review Dataset & Fixtures (`tests/fixtures/review/`)
  - [x] Milestone 6.12: Database Alembic Migration for ReviewStatus Enum
- **Phase 5: ESCO Normalization & Taxonomy Integration**
  - [x] Milestone 5.1: Normalization Schemas (Pydantic v2 domain schemas)
  - [x] Milestone 5.2: ESCO Dataset Ingestion (local loaders + cache on startup)
  - [x] Milestone 5.3: Taxonomy Indexing (exact, alias, normalized text indexes)
  - [x] Milestone 5.4: Skill Preprocessing (lowercasing, punctuation, versioning)
  - [x] Milestone 5.5: Exact Match Engine (1.0 confidence exact matching)
  - [x] Milestone 5.6: Alias Matching (alias dict and configuration matching)
  - [x] Milestone 5.7: RapidFuzz Matching (top-k fuzzy matches and thresholds)
  - [x] Milestone 5.8: Embedding Matching (sentence-transformers semantic matches)
  - [x] Milestone 5.9: Candidate Ranking Engine (combining multiple match strategies)
  - [x] Milestone 5.10: Confidence Engine (explainable deterministic scoring)
  - [x] Milestone 5.11: Normalization Service (SkillNormalizationService orchestration)
  - [x] Milestone 5.12: normalize_skill.md Skill File (system prompts + examples)
  - [x] Milestone 5.13: Normalization API (POST /normalize/skills HTTP endpoint)
  - [x] Milestone 5.14: Normalization Dataset & Unit/Integration Tests (Representative fixtures + test suite)
- **Phase 4: Information Extraction Engine**
  - [x] Milestone 4.1: Extraction Schemas (Pydantic v2 domain schemas)
  - [x] Milestone 4.2: Model Management Layer (lazy-loading DeBERTa-v3-small infrastructure)
  - [x] Milestone 4.3: Skill Extraction Engine (NER inference pipeline + gazetteer mapping)
  - [x] Milestone 4.4: Skill Post-Processing (deduplication, span merging, casing)
  - [x] Milestone 4.5: Experience Extraction (min/max years parser rules)
  - [x] Milestone 4.6: Seniority Extraction (title matching + experience mapping fallback)
  - [x] Milestone 4.7: Requirement Classification (Required, Preferred, Optional rules)
  - [x] Milestone 4.8: Extraction Orchestrator (Orchestrated ExtractionService pipeline)
  - [x] Milestone 4.9: Skill Files (skills/extract_skills.md and skills/classify_requirement.md)
  - [x] Milestone 4.10: Extraction API (POST /api/v1/extract HTTP endpoint)
  - [x] Milestone 4.11: Extraction Dataset & Unit/Integration Tests (Fixtures and test suites passing)
- **Phase 3: Preprocessing & JD Segmentation**
- **Phase 0**: Repository Initialization
- **Phase 1: Environment Setup & Infrastructure**
- **Phase 2: CI/CD Foundation & Ingestion Framework**
