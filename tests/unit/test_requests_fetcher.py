"""Unit tests for Milestone 2.3 — Requests Fetcher."""

from unittest.mock import MagicMock, patch

import requests

from app.ingestion.fetchers import FetchResult, RequestsFetcher


def _make_mock_response(
    status_code: int = 200,
    text: str = "<html><body>Job content</body></html>",
    url: str = "https://example.com/job",
    content_type: str = "text/html; charset=utf-8",
    encoding: str = "utf-8",
) -> MagicMock:
    """Build a mock requests.Response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text
    resp.url = url
    resp.encoding = encoding
    resp.apparent_encoding = encoding
    resp.headers = {"Content-Type": content_type, "X-Custom": "value"}
    return resp


# ---------------------------------------------------------------------------
# FetchResult dataclass
# ---------------------------------------------------------------------------


class TestFetchResult:
    def test_success_result(self):
        result = FetchResult(
            url="https://example.com",
            html="<html>test</html>",
            status_code=200,
            content_type="text/html",
            duration_ms=123.4,
            final_url="https://example.com",
            success=True,
        )
        assert result.success is True
        assert result.error is None
        assert result.html == "<html>test</html>"

    def test_failure_result(self):
        result = FetchResult(
            url="https://example.com",
            html="",
            status_code=0,
            content_type="",
            duration_ms=30000.0,
            final_url="https://example.com",
            success=False,
            error="Timeout",
        )
        assert result.success is False
        assert result.error == "Timeout"
        assert result.html == ""


# ---------------------------------------------------------------------------
# RequestsFetcher
# ---------------------------------------------------------------------------


class TestRequestsFetcherInit:
    def test_default_init(self):
        fetcher = RequestsFetcher()
        assert fetcher.timeout == 30
        assert fetcher.max_retries == 3
        assert fetcher.backoff_factor == 0.5

    def test_custom_init(self):
        fetcher = RequestsFetcher(timeout=10, max_retries=1, backoff_factor=1.0)
        assert fetcher.timeout == 10
        assert fetcher.max_retries == 1

    def test_ua_index_rotation(self):
        # Index 0
        f0 = RequestsFetcher(user_agent_index=0)
        # Index wraps around
        f_large = RequestsFetcher(user_agent_index=100)
        # Both should have valid user agents set
        assert "User-Agent" in f0._session.headers
        assert "User-Agent" in f_large._session.headers


class TestRequestsFetcherFetch:
    def test_successful_fetch(self):
        mock_resp = _make_mock_response(status_code=200, text="<html>Job!</html>")

        with patch("requests.Session.get", return_value=mock_resp):
            fetcher = RequestsFetcher()
            result = fetcher.fetch("https://example.com/job")

        assert result.success is True
        assert result.status_code == 200
        assert result.html == "<html>Job!</html>"
        assert result.duration_ms >= 0

    def test_404_response(self):
        mock_resp = _make_mock_response(status_code=404, text="Not found")

        with patch("requests.Session.get", return_value=mock_resp):
            fetcher = RequestsFetcher()
            result = fetcher.fetch("https://example.com/missing")

        assert result.success is False
        assert result.status_code == 404

    def test_timeout_returns_failure(self):
        with patch(
            "requests.Session.get",
            side_effect=requests.exceptions.Timeout("Timed out"),
        ):
            fetcher = RequestsFetcher(timeout=5)
            result = fetcher.fetch("https://slow.example.com/job")

        assert result.success is False
        assert result.status_code == 0
        assert "timed out" in result.error.lower()  # type: ignore[union-attr]

    def test_connection_error_returns_failure(self):
        with patch(
            "requests.Session.get",
            side_effect=requests.exceptions.ConnectionError("Cannot connect"),
        ):
            fetcher = RequestsFetcher()
            result = fetcher.fetch("https://unreachable.example.com/job")

        assert result.success is False
        assert "Connection error" in result.error  # type: ignore[operator]

    def test_general_request_exception(self):
        with patch(
            "requests.Session.get",
            side_effect=requests.exceptions.RequestException("Generic error"),
        ):
            fetcher = RequestsFetcher()
            result = fetcher.fetch("https://example.com")

        assert result.success is False
        assert result.error is not None

    def test_redirect_final_url(self):
        mock_resp = _make_mock_response(
            status_code=200,
            url="https://example.com/job/redirected",
        )
        with patch("requests.Session.get", return_value=mock_resp):
            fetcher = RequestsFetcher()
            result = fetcher.fetch("https://example.com/job/original")

        assert result.final_url == "https://example.com/job/redirected"

    def test_extra_headers_applied(self):
        mock_resp = _make_mock_response()
        with patch("requests.Session.get", return_value=mock_resp):
            fetcher = RequestsFetcher()
            fetcher.fetch("https://example.com", extra_headers={"X-Token": "abc"})
            assert "X-Token" in fetcher._session.headers

    def test_content_type_captured(self):
        mock_resp = _make_mock_response(content_type="text/html; charset=utf-8")
        with patch("requests.Session.get", return_value=mock_resp):
            fetcher = RequestsFetcher()
            result = fetcher.fetch("https://example.com")

        assert "text/html" in result.content_type

    def test_response_headers_captured(self):
        mock_resp = _make_mock_response()
        with patch("requests.Session.get", return_value=mock_resp):
            fetcher = RequestsFetcher()
            result = fetcher.fetch("https://example.com")

        assert "X-Custom" in result.response_headers

    def test_null_encoding_falls_back(self):
        mock_resp = _make_mock_response(encoding=None, text="<html>content</html>")  # type: ignore[arg-type]
        mock_resp.apparent_encoding = "utf-8"
        with patch("requests.Session.get", return_value=mock_resp):
            fetcher = RequestsFetcher()
            result = fetcher.fetch("https://example.com")

        assert result.html == "<html>content</html>"


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------


class TestContextManager:
    def test_context_manager_usage(self):
        mock_resp = _make_mock_response()
        with patch("requests.Session.get", return_value=mock_resp):
            with RequestsFetcher() as fetcher:
                result = fetcher.fetch("https://example.com")
            assert result.success is True

    def test_close_called_on_exit(self):
        fetcher = RequestsFetcher()
        with patch.object(fetcher._session, "close") as mock_close:
            fetcher.close()
            mock_close.assert_called_once()
