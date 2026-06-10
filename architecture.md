# Architecture - JD Skill Extraction Pipeline

## System Diagram
```mermaid
graph TD
    User([User / API Client]) --> APILayer[API Layer (FastAPI)]
    MCP[MCP Client] --> MCPLayer[MCP Server Layer]
    APILayer --> Orchestrator[Orchestration Layer]
    MCPLayer --> Orchestrator

    Orchestrator --> Ingestion[Ingestion & Fetchers]
    Orchestrator --> Preprocessing[Preprocessing Pipeline]
    Orchestrator --> NLPEngine[NLP Layer: DeBERTa NER]
    Orchestrator --> Normalizer[Skill Normalization & ESCO Mapping]
    Orchestrator --> ReviewQueue[Review Queue / State Machine]

    Orchestrator --> DbLayer[Persistence Layer (SQLAlchemy 2.0 / PostgreSQL)]

    subgraph Ingestion [Ingestion Framework]
        SourceDetector[Source Detector] --> FetcherRouter{Fetcher Router}
        FetcherRouter -- static page --> RequestsFetcher[Requests Fetcher]
        FetcherRouter -- JS-rendered page --> PlaywrightFetcher[Playwright Fetcher]
        RequestsFetcher --> ContentExtractor[Trafilatura Content Extractor]
        PlaywrightFetcher --> ContentExtractor
        ContentExtractor --> FetchedDocument[FetchedDocument]
    end
```

## Component Overview

### Ingestion Framework (Phase 2)
| Component | Module | Responsibility |
|-----------|--------|----------------|
| `SourceDetector` | `app.ingestion.detectors.url_detector` | Classifies JD URL → `SourceType` enum. Handles Naukri, Foundit, Indeed, Greenhouse, Lever, Workable, Generic ATS, PDF, Unknown. |
| `RequestsFetcher` | `app.ingestion.fetchers.requests_fetcher` | Static HTTP fetch with retry, UA rotation, redirect tracking, response header capture. |
| `PlaywrightFetcher` | `app.ingestion.fetchers.playwright_fetcher` | Async headless Chromium fetch for JS-rendered pages. Scroll-to-trigger, console error capture. |
| `TrafilaturaParser` | `app.ingestion.parsers.trafilatura_parser` | 3-tier HTML→text extraction: Trafilatura primary → Trafilatura broad recall → BeautifulSoup fallback. |
| Ingestion Schemas | `app.ingestion.schemas.schemas` | `SourceType`, `FetchStatus`, `DocumentMetadata`, `FetchedDocument`, `IngestionRequest`, `IngestionResponse`. |

### Preprocessing & Segmentation (Phase 3)
| Component | Module | Responsibility |
|-----------|--------|----------------|
| `TextCleaner` | `app.preprocessing.cleaners.text_cleaner` | Normalizes whitespace, unicode, collapses blank lines, unifies smart quotes, and standardizes bullets/lists while preserving indentation. |
| `HeadingNormalizer` | `app.preprocessing.normalizers.heading_normalizer` | Strips decorative punctuation and maps raw heading variants to canonical SectionTypes. |
| `BoilerplateDetector` | `app.preprocessing.classifiers.boilerplate_detector` | Scans 50+ patterns to quarantine disclaimers/marketing/EEO copy without permanent data loss. |
| `HeadingDetector` | `app.preprocessing.segmenters.heading_detector` | Detects headings using exact matches, fuzzy scoring, and structural heuristics. |
| `SectionSegmenter` | `app.preprocessing.segmenters.section_segmenter` | Splits cleaned text into raw sections at heading boundaries. |
| `SectionClassifier` | `app.preprocessing.classifiers.section_classifier` | Classifies sections using heading categories and bag-of-words keyword scoring. |
| `SegmentationService` | `app.preprocessing.services.segmentation_service` | Orchestrates the entire pipeline, records execution metadata/timing, and emits `SegmentationResult`. |

## Data Flow
```mermaid
sequenceDiagram
    participant Client
    participant API as API / MCP Layer
    participant Orc as Orchestrator
    participant Det as Source Detector
    participant Fetch as Fetcher (Requests / Playwright)
    participant Parse as Trafilatura Parser
    participant NLP as NLP NER Engine
    participant Norm as Normalization Engine (ESCO)
    participant DB as PostgreSQL Database

    Client->>API: POST /pipeline/run (URL/PDF)
    API->>Orc: Trigger Pipeline Run
    Orc->>Det: detect(url) → SourceType
    Det-->>Orc: SourceType
    Orc->>Fetch: fetch(url) → FetchResult / PlaywrightResult
    Fetch-->>Orc: Raw HTML + metadata
    Orc->>Parse: parse(html, url) → ParseResult
    Parse-->>Orc: Clean Text + word_count + metadata
    Orc->>NLP: Extract Entities (Skills, Exp, Seniority)
    NLP-->>Orc: Spans & Confidence Scores
    Orc->>Norm: Map to ESCO Taxonomy
    Norm-->>Orc: Standardized Skills (IDs/Titles)
    Orc->>DB: Persist Job, Skills & Run Logs
    Orc->>Client: Return Structured Output
```

## Entity Relationship (ER) Diagram
```mermaid
erDiagram
    JOBS {
        UUID id PK
        string title
        string company
        string location
        string seniority
        string source_url
        string raw_text
        string status
        bool review_required
        float experience_min
        float experience_max
        float confidence_score
        timestamp created_at
        timestamp updated_at
    }
    SKILLS {
        UUID id PK
        string name
        string normalized_name
        string esco_code
        string esco_uri
        string category
        timestamp created_at
    }
    JOB_SKILLS {
        UUID id PK
        UUID job_id FK
        UUID skill_id FK
        string requirement_type
        float confidence_score
        timestamp created_at
    }
    REVIEW_QUEUE {
        UUID id PK
        UUID job_id FK
        string status
        string flagged_reasons
        string reviewed_by
        timestamp reviewed_at
        timestamp created_at
    }
    PROCESSING_RUNS {
        UUID id PK
        UUID job_id FK
        string status
        string error_message
        float duration_ms
        timestamp started_at
        timestamp completed_at
    }
    AUDIT_LOGS {
        UUID id PK
        UUID job_id FK
        string action
        string actor
        string details
        timestamp timestamp
    }

    JOBS ||--o{ JOB_SKILLS : "has"
    SKILLS ||--o{ JOB_SKILLS : "referenced in"
    JOBS ||--o| REVIEW_QUEUE : "requires"
    JOBS ||--o{ PROCESSING_RUNS : "tracked by"
    JOBS ||--o{ AUDIT_LOGS : "tracks"
```

## Fetcher Selection Logic

```mermaid
flowchart TD
    A[URL Input] --> B{SourceDetector.detect}
    B -->|GREENHOUSE, LEVER, WORKABLE| C[PlaywrightFetcher]
    B -->|NAUKRI, FOUNDIT, INDEED, GENERIC_ATS| D[RequestsFetcher]
    B -->|PDF| E[PDF Fetcher - future phase]
    B -->|UNKNOWN| F[RequestsFetcher with fallback]
    C --> G[TrafilaturaParser]
    D --> G
    G -->|success| H[FetchedDocument]
    G -->|fail| I[IngestionResponse: failed]
```

## CI/CD Architecture

```mermaid
graph LR
    Push[Git Push] --> GHA[GitHub Actions]
    GHA --> Lint[Lint Job: Ruff + Black + MyPy]
    Lint -->|pass| Unit[Unit Test Job: pytest --cov=app]
    Lint -->|pass| Integration[Integration Test Job: Postgres + Alembic]
    Unit --> Codecov[Codecov Coverage Upload]
    Integration --> Migrations[alembic upgrade head]
```

## Architectural Decisions

| Decision | Rationale |
|----------|-----------|
| Requests + Playwright dual-fetcher | Static pages are cheaper via Requests; JS-rendered ATS boards require Playwright. Both share the same `TrafilaturaParser`. |
| Trafilatura as primary extractor | Best-in-class HTML→text for article/job pages; configurable `MIN_EXTRACTED_SIZE` to accept short JDs. |
| BeautifulSoup last-resort fallback | Ensures _something_ is returned even from heavily obfuscated pages. |
| `FetchedDocument.to_output()` contract | Normalizes all fetcher types into a single dict shape for downstream pipeline stages. |
| SourceType enum as string enum | String values enable JSON serialization without extra transformations. |
