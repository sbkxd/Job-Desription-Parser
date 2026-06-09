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
```

## Data Flow
```mermaid
sequenceDiagram
    participant Client
    participant API as API / MCP Layer
    participant Orc as Orchestrator
    participant Fetch as Fetcher & Preprocessor
    participant NLP as NLP NER Engine
    participant Norm as Normalization Engine (ESCO)
    participant DB as PostgreSQL Database

    Client->>API: POST /pipeline/run (URL/PDF)
    API->>Orc: Trigger Pipeline Run
    Orc->>Fetch: Ingest & Preprocess Content
    Fetch-->>Orc: Clean Text & Metadata
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
        string raw_text
        string status
        timestamp created_at
    }
    SKILLS {
        UUID id PK
        string name
        string esco_code
        string esco_uri
        timestamp created_at
    }
    JOB_SKILLS {
        UUID job_id FK
        UUID skill_id FK
        string requirement_type
        float confidence_score
    }
    REVIEWS {
        UUID id PK
        UUID job_id FK
        string status
        string flagged_reasons
        timestamp created_at
    }
    AUDIT_LOGS {
        UUID id PK
        UUID job_id FK
        string action
        string user_id
        timestamp timestamp
    }

    JOBS ||--o{ JOB_SKILLS : "has"
    SKILLS ||--o{ JOB_SKILLS : "referenced in"
    JOBS ||--o| REVIEWS : "requires"
    JOBS ||--o{ AUDIT_LOGS : "tracks"
```
