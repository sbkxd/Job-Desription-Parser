"""Fetchers package."""

from app.ingestion.fetchers.playwright_fetcher import (
    PlaywrightFetcher,
    PlaywrightResult,
)
from app.ingestion.fetchers.requests_fetcher import FetchResult, RequestsFetcher

__all__ = ["RequestsFetcher", "FetchResult", "PlaywrightFetcher", "PlaywrightResult"]
