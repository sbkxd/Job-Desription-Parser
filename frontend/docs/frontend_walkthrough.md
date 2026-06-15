# Frontend Walkthrough & User Guide

This document describes how to execute, verify, and interact with the JD Skill Intelligence Platform frontend.

## Quick Start Guide

### Prerequisites
- Node.js >= 18.x
- npm >= 9.x
- Running backend server (`http://localhost:8000`)

### Installation
From the root of the workspace, navigate to the `frontend/` directory and install the packages:
```bash
cd frontend
npm install
```

### Run Local Development Server
Execute the Next.js local server:
```bash
npm run dev
```
Open `http://localhost:3000` in your web browser.

---

## User Flow Walkthrough

### 1. Ingest Job Description
- **Option A (URL)**: Paste a valid job posting web link (e.g., a LinkedIn job posting or ATS career page) in the URL input tab and click **Analyze URL**.
- **Option B (PDF)**: Drag a local PDF file and drop it in the drop zone, or click to upload one from your computer. Click **Analyze PDF**.

### 2. Live Telemetry Inspection
Once submitted, the UI automatically scrolls to reveal the **Pipeline Telemetry** visualization panel. You will see the LangGraph nodes animate sequentially:
1. Ingestion
2. Segmentation
3. Extraction (NER)
4. Normalization (ESCO Mapping)
5. Review Queue (AI Validation)
6. Report Creation

### 3. Review Results
Upon completion, the dashboard displays structured information cards:
- **Job metadata & profile requirements**
- **Skills badges** categorized into Required, Preferred, and Normalized.
- **Technology tag cloud** color-coded.
- **Interactive charts** built with Recharts.
- **Export tools**: Download JSON, download CSV, or copy formatting straight to your clipboard.
