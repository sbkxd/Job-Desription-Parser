"""Unit tests for Milestone 2.5 — Playwright Fetcher."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ingestion.fetchers.playwright_fetcher import (
    PlaywrightFetcher,
    PlaywrightResult,
)


class TestPlaywrightResultDataclass:
    def test_success_result(self):
        result = PlaywrightResult(
            url="https://jobs.lever.co/acme/123",
            html="<html><body>Job content</body></html>",
            final_url="https://jobs.lever.co/acme/123",
            status_code=200,
            duration_ms=1234.5,
            success=True,
        )
        assert result.success is True
        assert result.error is None
        assert result.console_errors == []
        assert result.response_headers == {}

    def test_failure_result(self):
        result = PlaywrightResult(
            url="https://example.com",
            html="",
            final_url="https://example.com",
            status_code=0,
            duration_ms=30000.0,
            success=False,
            error="Navigation timed out after 30000ms",
        )
        assert result.success is False
        assert "timed out" in result.error


class TestPlaywrightFetcherInit:
    def test_defaults(self):
        fetcher = PlaywrightFetcher()
        assert fetcher.timeout_ms == 30_000
        assert fetcher.wait_until == "networkidle"
        assert fetcher.headless is True
        assert fetcher.scroll is True

    def test_custom_init(self):
        fetcher = PlaywrightFetcher(
            timeout_ms=15_000,
            wait_until="load",
            headless=False,
            scroll=False,
        )
        assert fetcher.timeout_ms == 15_000
        assert fetcher.wait_until == "load"
        assert fetcher.headless is False
        assert fetcher.scroll is False

    def test_is_available_when_playwright_installed(self):
        fetcher = PlaywrightFetcher()
        # Playwright is installed in the project
        assert fetcher.is_available is True


class TestPlaywrightFetcherMocked:
    """Tests using mocked Playwright internals — no real browser launched."""

    def _make_mock_response(self, status: int = 200) -> MagicMock:
        resp = MagicMock()
        resp.status = status
        resp.headers = {"content-type": "text/html"}
        return resp

    @pytest.mark.asyncio
    async def test_successful_fetch(self):
        """Mock the internal _do_fetch to simulate a successful result."""
        fetcher = PlaywrightFetcher()
        expected = PlaywrightResult(
            url="https://jobs.lever.co/acme/123",
            html="<html><body>Senior Engineer at Acme Corp</body></html>",
            final_url="https://jobs.lever.co/acme/123",
            status_code=200,
            duration_ms=1500.0,
            success=True,
        )
        with patch.object(
            fetcher, "_do_fetch", new_callable=AsyncMock, return_value=expected
        ):
            result = await fetcher.fetch("https://jobs.lever.co/acme/123")
        assert result.success is True
        assert result.status_code == 200
        assert "Senior Engineer" in result.html

    @pytest.mark.asyncio
    async def test_timeout_result(self):
        fetcher = PlaywrightFetcher(timeout_ms=5_000)
        timeout_result = PlaywrightResult(
            url="https://slow.example.com",
            html="",
            final_url="https://slow.example.com",
            status_code=0,
            duration_ms=5000.0,
            success=False,
            error="Navigation timed out after 5000ms",
        )
        with patch.object(
            fetcher, "_do_fetch", new_callable=AsyncMock, return_value=timeout_result
        ):
            result = await fetcher.fetch("https://slow.example.com")
        assert result.success is False
        assert "timed out" in result.error.lower()

    @pytest.mark.asyncio
    async def test_unexpected_exception_captured(self):
        """If _do_fetch raises, fetch() should catch it and return failure."""
        fetcher = PlaywrightFetcher()
        with patch.object(
            fetcher,
            "_do_fetch",
            new_callable=AsyncMock,
            side_effect=RuntimeError("crash"),
        ):
            result = await fetcher.fetch("https://example.com")
        assert result.success is False
        assert result.error is not None
        assert "crash" in result.error

    @pytest.mark.asyncio
    async def test_returns_playwright_result_type(self):
        fetcher = PlaywrightFetcher()
        mock_result = PlaywrightResult(
            url="https://apply.workable.com/acme/j/123/",
            html="<html><body>Workable Job</body></html>",
            final_url="https://apply.workable.com/acme/j/123/",
            status_code=200,
            duration_ms=2000.0,
            success=True,
        )
        with patch.object(
            fetcher, "_do_fetch", new_callable=AsyncMock, return_value=mock_result
        ):
            result = await fetcher.fetch("https://apply.workable.com/acme/j/123/")
        assert isinstance(result, PlaywrightResult)

    @pytest.mark.asyncio
    async def test_404_not_success(self):
        fetcher = PlaywrightFetcher()
        not_found = PlaywrightResult(
            url="https://example.com/nonexistent",
            html="<html><body>Not Found</body></html>",
            final_url="https://example.com/nonexistent",
            status_code=404,
            duration_ms=500.0,
            success=False,
        )
        with patch.object(
            fetcher, "_do_fetch", new_callable=AsyncMock, return_value=not_found
        ):
            result = await fetcher.fetch("https://example.com/nonexistent")
        assert result.success is False
        assert result.status_code == 404

    @pytest.mark.asyncio
    async def test_console_errors_captured(self):
        fetcher = PlaywrightFetcher()
        with_errors = PlaywrightResult(
            url="https://greenhouse.io/acme/123",
            html="<html>content</html>",
            final_url="https://greenhouse.io/acme/123",
            status_code=200,
            duration_ms=3000.0,
            success=True,
            console_errors=["Failed to load resource", "TypeError: x is undefined"],
        )
        with patch.object(
            fetcher, "_do_fetch", new_callable=AsyncMock, return_value=with_errors
        ):
            result = await fetcher.fetch("https://greenhouse.io/acme/123")
        assert len(result.console_errors) == 2
        assert "Failed to load resource" in result.console_errors


class TestPlaywrightUnavailable:
    """Test graceful degradation when Playwright is not installed."""

    @pytest.mark.asyncio
    async def test_unavailable_returns_failure(self):
        fetcher = PlaywrightFetcher()
        with patch(
            "app.ingestion.fetchers.playwright_fetcher._PLAYWRIGHT_AVAILABLE", False
        ):
            result = await fetcher.fetch("https://jobs.lever.co/acme/123")
        assert result.success is False
        assert result.error is not None
        assert (
            "not installed" in result.error.lower()
            or "playwright" in result.error.lower()
        )
