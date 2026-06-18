# Implementation Plan - Mistral Resume Optimization Engine (Phase 10)

## Current Phase
- **None** (All Phases Completed)

## Completed Phases
- **Phase 10**: Mistral Resume Optimization Engine
- **Phase 9**: Job ↔ Resume Compatibility Engine
- **Phase 8**: Resume Ingestion & Resume Intelligence
- **Phase 0 - 7 & 8A/9/10**: Previous JD Skill Extraction Pipeline implementation.


---

## Goal Description
We are building the Mistral Resume Optimization Engine. This module provides personalized suggestions to improve the resume for a specific job description. This is strictly advisory; the system must never rewrite facts, invent experience, or fabricate skills.

---

## Key Decisions
1. **Scaffolding**:
   Create `app/recommendations/` containing prompts, services, schemas.
2. **Mistral AI Integration**:
   We will pass Resume Intelligence, Job Intelligence, Compatibility Report, and Gap Analysis to Mistral AI using the `MistralClient` and the `mistral-small-latest` model.
3. **Structured Outputs**:
   We will define Pydantic schemas for the LLM output:
   - `ImprovementSuggestion`: type (e.g. MISSING_SKILL, KEYWORD, EXPERIENCE, PROJECT, EDUCATION, CERTIFICATION), message (advisory details).
   - `AtsRecommendation`: keyword, coverage_status (e.g. MISSING, LOW_COVERAGE), recommendation (details).
   - `TailoredSummary`: summary text based strictly on existing resume content.
   - `ApplicationReadiness`: readiness_score (int 0-100), recommendation (str).
   - `ResumeOptimizationReport`: compatibility_score (from Phase 9), matched_skills, missing_skills, critical_gaps, strengths, resume_improvements, ats_recommendations, application_readiness.
4. **API Endpoint**:
   - `POST /api/v1/resume/recommendations` (and root `POST /resume/recommendations`): Accepts Resume Intelligence and Job Intelligence Reports (or parses them if files/URLs are given), calculates compatibility, calls Mistral to generate recommendations, and returns the combined output schema.

---

## Risks
1. **Fact Fabrication**: LLMs tend to invent skills or details to improve match scores. We will include strict instructions in the system prompts: "Never fabricate skills, projects, or experience not present in the candidate resume."
2. **Latency**: Recommendations call LLMs, adding latency. We will reuse the async MistralClient structure with timeouts.

---

## Proposed Changes

### Recommendations Module

#### [NEW] [schemas.py](file:///d:/Altrosyn%20-%20JD%20Parser/JD%20Parser/app/recommendations/schemas/schemas.py)
Define Pydantic v2 schemas:
- `ImprovementSuggestion`: type, message.
- `AtsRecommendation`: keyword, coverage_status, recommendation.
- `TailoredSummary`: summary.
- `ApplicationReadiness`: readiness_score, recommendation.
- `MistralRecommendationsResponse`: suggestions list, ats_recommendations list, tailored_summary, readiness_score, readiness_recommendation.
- `ResumeOptimizationReport`: compatibility_score, matched_skills, missing_skills, critical_gaps, strengths, resume_improvements, ats_recommendations, application_readiness_score, tailored_summary.

#### [NEW] [prompts.py](file:///d:/Altrosyn%20-%20JD%20Parser/JD%20Parser/app/recommendations/prompts/prompts.py)
Define system and user prompts instructing Mistral AI to parse reports, analyze gaps, and format output.

#### [NEW] [service.py](file:///d:/Altrosyn%20-%20JD%20Parser/JD%20Parser/app/recommendations/services/service.py)
Implement `RecommendationService` orchestrating the comparison, calling Mistral, and compiling the unified output schema.

#### [NEW] [recommendations_api.py](file:///d:/Altrosyn%20-%20JD%20Parser/JD%20Parser/app/api/v1/endpoints/recommendations_api.py)
Implement `POST /resume/recommendations` endpoint. Register this router in `app/main.py` and `app/api/v1/router.py`.

---

## Verification Plan

### Automated Tests
- Implement unit tests in `tests/unit/test_recommendations.py` covering:
  - Prompt generation.
  - LLM response parsing and structured formatting using mocked Mistral outputs.
  - End-to-end service validation.
  - API endpoint routing using `TestClient`.
