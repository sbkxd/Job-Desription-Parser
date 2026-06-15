# Frontend Architecture

This document describes the design, routing, state management, and API integration layers for the JD Skill Intelligence Platform frontend.

## Overview

The frontend is a single-page workflow application built using **Next.js 15** and **React 19** with TypeScript. It communicates with the Python FastAPI backend to process job description inputs (URLs or PDFs) and renders structured reports.

## Project Structure

```text
frontend/
├── docs/                      # Architectural & design documentation
├── public/                    # Static assets
└── src/
    ├── app/                   # App Router config, layout, pages
    ├── components/            # Reusable UI elements (Header, Footer, Hero, dashboards)
    ├── services/              # API communications client
    ├── store/                 # Zustand state stores
    └── types/                 # TypeScript type interface declarations
```

## Architectural Layers

### 1. Presentation Layer
- **Layout & Routing**: Next.js App Router (`src/app/layout.tsx`, `src/app/page.tsx`).
- **Interactive UI Components**: Functional UI components styled with Tailwind CSS v4 and animated using Framer Motion.

### 2. State Management Layer
- **useStore (Zustand)**: Controls active status, error handling, progress flow tracker, and caches the final output report locally.
- **React Query**: Standard provider configuration for caching and mutation wrappers.

### 3. Service Layer
- **ApiService**: Isolated API caller handling fetch requests to backend endpoints:
  - `POST /api/v1/pipeline/run/url` (URL analysis payload)
  - `POST /api/v1/pipeline/run/upload` (multipart/form-data for browser PDF uploads)
  - `GET /api/v1/health` (connectivity checks)
