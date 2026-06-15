# Tasks - JD Skill Extraction Pipeline

## Pending
- **Phase 10**: Deployment Enhancements & Cloud Readiness
- **Phase 11**: Observability, Security & Dockerization
- **Phase 12**: Production Hardening & Final Release

## In Progress
*None*

## Blocked
*None*

## Completed
- **Phase 8A: Complete Frontend Implementation**
  - [x] Milestone 8A.1: Add PDF upload endpoint to FastAPI backend
  - [x] Milestone 8A.2: Initialize Next.js 15 Tailwind application in `frontend/`
  - [x] Milestone 8A.3: Configure global design system (`globals.css`)
  - [x] Milestone 8A.4: Create core UI components (Header, Footer, Hero)
  - [x] Milestone 8A.5: Implement InputSection (URL form + Drag & Drop PDF with progress bar)
  - [x] Milestone 8A.6: Implement PipelineVisualizer node animations
  - [x] Milestone 8A.7: Implement ResultsDashboard (cards, tag cloud, timeline, checklist, Recharts visualizations, exports)
  - [x] Milestone 8A.8: Write frontend documentation
- **Phase 9: Final Output Formatter Integration**
  - [x] Milestone 9.1: Presentation Schemas (`app/presentation/schemas/job_intelligence.py`)
  - [x] Milestone 9.2: Job Intelligence Formatter (`app/presentation/formatters/job_intelligence_formatter.py`)
  - [x] Milestone 9.3: Alembic migration for `pipeline_state` JSON column in `processing_runs`
  - [x] Milestone 9.4: Update pipeline endpoints to return formatted `JobIntelligenceReport`
  - [x] Milestone 9.5: Add debug endpoint `GET /pipeline/debug/{job_id}`
  - [x] Milestone 9.6: Update `architecture.md` and `walkthrough.md`
  - [x] Milestone 9.7: Add presentation unit tests and verify code quality
- **Phase 8: Mistral Small Latest Migration**
  - [x] Milestone 8.1: Mistral Client (`app/orchestration/mistral/mistral_client.py` with retries, timeouts, and structured JSON)
  - [x] Milestone 8.2: Mistral Resolution Node (`app/orchestration/nodes/mistral_resolution_node.py` replacing Ollama)
  - [x] Milestone 8.3: Verification and Quality Gate (ruff, black, mypy, and 259 unit/E2E tests passing)
- **Phase 7: LangGraph Orchestration, MCP Tools & Ollama Integration**
  - [x] Milestone 7.1: Pipeline State Design (`PipelineState` model and merge reducers)
  - [x] Milestone 7.2: LangGraph Foundation (StateGraph setup & compilation)
  - [x] Milestone 7.3: Fetch JD Node (Retrieval via Playwright/Requests)
  - [x] Milestone 7.4: Segment JD Node (Section segmentation node)
  - [x] Milestone 7.5: Extraction Node (NER extraction attributes node)
  - [x] Milestone 7.6: Normalization Node (ESCO matching normalization node)
  - [x] Milestone 7.7: Review Evaluation Node (Confidence & routing evaluation node)
  - [x] Milestone 7.8: Conditional Routing (ReviewRouter conditional edges)
  - [x] Milestone 7.9: Ollama Client (qwen3:4b Client & qwen_adapter)
  - [x] Milestone 7.10: Ollama Resolution Node (Fallback skill resolution node)
  - [x] Milestone 7.11: Review Queue Node (Queue item generation node)
  - [x] Milestone 7.12: Persistence Node (Job and skill database saving node)
  - [x] Milestone 7.13: MCP Tool Framework (BaseMCPTool and registry)
  - [x] Milestone 7.14: MCP Tool: `fetch_jd()` (Fetching wrapper)
  - [x] Milestone 7.15: MCP Tool: `run_ner()` (Extraction wrapper)
  - [x] Milestone 7.16: MCP Tool: `lookup_taxonomy()` (Normalization wrapper)
  - [x] Milestone 7.17: MCP Tool: `save_parsed_jd()` (Persistence wrapper)
  - [x] Milestone 7.18: Execution Audit System (ProcessingRuns & PipelineEvents logging)
  - [x] Milestone 7.19: Graph Visualization (Mermaid documentation rendering in `docs/graphs/`)
  - [x] Milestone 7.20: Full Pipeline API (POST `/api/v1/pipeline/run` endpoint)
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
