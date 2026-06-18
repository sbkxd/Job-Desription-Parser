# API Integration Guide

This guide details how the Next.js frontend integrates with the FastAPI backend services.

## Base URL
All API requests are routed to the base address:
```text
http://localhost:8000/api/v1
```
This is customizable using the environment variable `NEXT_PUBLIC_API_URL`.

---

## Endpoint Details

### 1. Job URL Analysis
* **Route**: `POST /pipeline/run/url`
* **Payload**:
  ```json
  {
    "url": "https://careers.google.com/jobs/results/..."
  }
  ```
* **Returns**: `JobIntelligenceReport`

### 2. Job PDF Upload Ingestion
* **Route**: `POST /pipeline/run/upload`
* **Payload**: `Multipart/Form-Data` containing `file`
* **Returns**: `JobIntelligenceReport`

### 3. Resume Ingestion & Intelligence
* **Route**: `POST /resume/analyze`
* **Payload**: `Multipart/Form-Data` containing `file`
* **Returns**: `ResumeIntelligenceReport`

### 4. Compatibility Analysis
* **Route**: `POST /compatibility/analyze`
* **Payload**:
  ```json
  {
    "resume": ResumeIntelligenceReport,
    "job": JobIntelligenceReport
  }
  ```
* **Returns**: `CompatibilityReport`

### 5. Resume Improvements & Optimization Suggestions
* **Route**: `POST /resume/recommendations`
* **Payload**:
  ```json
  {
    "resume": ResumeIntelligenceReport,
    "job": JobIntelligenceReport
  }
  ```
* **Returns**: `ResumeOptimizationReport`

### 6. Health Checks
* **Route**: `GET /health`
* **Returns**:
  ```json
  {
    "status": "healthy",
    "environment": "development"
  }
  ```

---

## Integration Workflow
The client initiates a chained promise resolution to execute all steps sequentially:
1. Upload and parse the job specification (URL or PDF).
2. Upload and parse the candidate resume PDF.
3. Compare both models to obtain compatibility alignment metrics.
4. Execute Mistral LLM to generate section improvements, ATS keywords, tailored summary, and readiness metrics.
5. Render the consolidated response to the Results Dashboard.
