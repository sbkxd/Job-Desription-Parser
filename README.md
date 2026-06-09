# JD Skill Extraction Pipeline

An enterprise-grade Job Description Skill Extraction Pipeline.

## Overview
This system reads job descriptions (JDs) from multiple ATS and public sources (Naukri, Foundit, Indeed, Greenhouse, Lever, Workable, public URLs, and PDFs), parses them, extracts structured skills, experience, seniority, requirements classification, and maps/normalizes skills to the ESCO taxonomy.

## Architecture
The system is designed using a Layered + Modular + Domain Driven approach:
1. API Layer (FastAPI)
2. Service Layer (Pipeline Orchestration)
3. NLP Layer (NER using DeBERTa-v3-small)
4. Skill Layer (Skill normalization & taxonomy matching)
5. MCP Layer (Model Context Protocol Integration)
6. Persistence Layer (PostgreSQL & SQLAlchemy 2.0)
7. Infrastructure Layer (Docker & Compose)
