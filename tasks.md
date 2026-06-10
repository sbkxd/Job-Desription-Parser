# Tasks - JD Skill Extraction Pipeline

## Pending
- **Phase 4**: Configuration Layer
- **Phase 5**: Database Layer
- **Phase 6**: Domain Models
- **Phase 7**: Ingestion Framework (advanced)
- **Phase 8**: Fetcher Implementations (advanced)
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

## In Progress
*None*

## Blocked
*None*

## Completed
- **Phase 0**: Repository Initialization
- **Phase 1: Environment Setup & Infrastructure**
  - [x] Milestone 1.1: Development Tooling
  - [x] Milestone 1.2: Application Configuration
  - [x] Milestone 1.3: Logging Infrastructure
  - [x] Milestone 1.4: Database Foundation
  - [x] Milestone 1.5: Alembic Setup
  - [x] Milestone 1.6: Core Domain Models
  - [x] Milestone 1.7: Repository Layer
  - [x] Milestone 1.8: FastAPI Application Bootstrap
  - [x] Milestone 1.9: Testing Foundation
  - [x] Milestone 1.10: CI/CD Foundation
- **Phase 2: CI/CD Foundation & Ingestion Framework**
  - [x] Milestone 2.1: Ingestion Domain Schemas (SourceType, FetchStatus, FetchedDocument, IngestionRequest, IngestionResponse)
  - [x] Milestone 2.2: Source Detection Engine (SourceDetector — Naukri, Foundit, Indeed, Greenhouse, Lever, Workable, Generic ATS, PDF, Unknown)
  - [x] Milestone 2.3: Requests Fetcher (RequestsFetcher with retry, UA rotation, FetchResult dataclass)
  - [x] Milestone 2.4: Trafilatura Content Extractor (TrafilaturaParser with 3-tier fallback, ParseResult dataclass)
  - [x] Milestone 2.5: Playwright Fetcher (PlaywrightFetcher async, headless Chromium, scroll-to-trigger, PlaywrightResult)
  - [x] Milestone 2.6: Unit tests for all ingestion components (≥ 80 new tests, 156 total, 89% coverage)
  - [x] Milestone 2.7: MyPy clean, Ruff clean, Black clean across all app/ modules
  - [x] Documentation update (tasks.md, implementation_plan.md, architecture.md, walkthrough.md, intent_matrix_results.md, CHANGELOG.md)
- **Phase 3: Preprocessing & JD Segmentation**
  - [x] Milestone 3.1: Preprocessing Schemas (SectionType, BoilerplateCategory, RawDocument, BoilerplateBlock, Section, SegmentedDocument, SegmentationResult)
  - [x] Milestone 3.2: Text Cleaning Pipeline (TextCleaner with 9 deterministic steps, bullet/number list handling, indentation preservation)
  - [x] Milestone 3.3: Content Normalization (HeadingNormalizer mapping heading surface forms to SectionType)
  - [x] Milestone 3.4: Boilerplate Detection (BoilerplateDetector identifying and quarantining legal/EEO/marketing disclaimers)
  - [x] Milestone 3.5: Heading Detection Engine (HeadingDetector with exact, fuzzy, and structural heuristics)
  - [x] Milestone 3.6: Rule-Based Section Segmenter (SectionSegmenter splitting lines into raw sections on heading boundaries)
  - [x] Milestone 3.7: Section Classification Engine (SectionClassifier scoring sections using heading type and keyword content rules)
  - [x] Milestone 3.8: Segmentation Orchestrator Service (SegmentationService running orchestrations and timing runs)
  - [x] Milestone 3.9: segment_jd.md Skill File (Few-shot samples and rules for AI models under skills/segment_jd.md)
  - [x] Milestone 3.10: Preprocessing API Endpoint (POST /api/v1/preprocess/segment)
  - [x] Milestone 3.11: Segmentation Fixture Dataset & Tests (6 real-world samples under tests/fixtures/segmentation/ and unit tests with 92% coverage)
