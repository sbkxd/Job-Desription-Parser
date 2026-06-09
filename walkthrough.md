# Walkthrough - JD Skill Extraction Pipeline

## What Was Built
- Initial repository scaffolding (Phase 0).
- Development tooling configuration (Milestone 1.1) including pre-commit, Black, Ruff, and MyPy.
- Centralized application settings (Milestone 1.2) using Pydantic Settings supporting environment overrides, and automatically calculating PostgreSQL async/sync URLs.

## Why It Exists
The settings module (`app/config/settings.py`) provides validation for all system-level configuration parameters (environment names, database credentials, logging levels, etc.), ensuring the application fails fast if configuration is missing or invalid.

## How It Works
1. `app/config/settings.py`: Declares `Settings` model sub-classing `BaseSettings` which reads variables from environment or a `.env` file.
2. `app/config/environment.py`: Contains `AppEnv` Enum (local, dev, staging, prod).
3. `app/config/constants.py`: Stores default configuration values.
4. Computed properties `database_url` and `sync_database_url` build valid PostgreSQL connection URIs dynamically.

## How to Run
Create a `.env` file in the root directory and define settings. If no `.env` is present, defaults will be used.

## How to Test
Run pytest inside the virtual environment:
```bash
.\.venv\Scripts\pytest
```
This runs the configuration tests in `tests/unit/test_config.py`.
