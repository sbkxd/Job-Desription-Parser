"""HTTP fetcher using requests with retry logic, timeout, and UA rotation."""

import time
from dataclasses import dataclass, field
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Realistic browser user-agent pool for anti-bot evasion
_USER_AGENTS: list[str] = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) "
        "Gecko/20100101 Firefox/121.0"
    ),
]

_DEFAULT_HEADERS: dict[str, str] = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


@dataclass
class FetchResult:
    """Raw result of a single HTTP fetch attempt."""

    url: str
    html: str
    status_code: int
    content_type: str
    duration_ms: float
    final_url: str  # After redirects
    success: bool
    error: str | None = None
    response_headers: dict[str, Any] = field(default_factory=dict)


class RequestsFetcher:
    """
    Synchronous HTTP fetcher built on `requests`.

    Features:
    - Rotating user-agent pool
    - Configurable timeouts
    - Exponential backoff retry on transient errors
    - Graceful error handling (no exceptions propagate to caller)
    - Connection pooling via HTTPAdapter
    """

    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        user_agent_index: int = 0,
    ) -> None:
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self._ua_index = user_agent_index % len(_USER_AGENTS)
        self._session = self._build_session()

    def _build_session(self) -> requests.Session:
        """Build a session with retry adapter and default headers."""
        session = requests.Session()
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        headers = {**_DEFAULT_HEADERS, "User-Agent": _USER_AGENTS[self._ua_index]}
        session.headers.update(headers)
        return session

    def fetch(
        self, url: str, extra_headers: dict[str, str] | None = None
    ) -> FetchResult:
        """
        Fetch a URL and return a FetchResult.

        Never raises — all errors are captured in FetchResult.error.
        """
        if extra_headers:
            self._session.headers.update(extra_headers)

        start = time.monotonic()
        try:
            response = self._session.get(
                url, timeout=self.timeout, allow_redirects=True
            )
            duration_ms = (time.monotonic() - start) * 1000

            # Determine encoding
            if response.encoding is None or response.encoding.lower() == "iso-8859-1":
                response.encoding = response.apparent_encoding or "utf-8"

            html = response.text
            content_type = response.headers.get("Content-Type", "")

            return FetchResult(
                url=url,
                html=html,
                status_code=response.status_code,
                content_type=content_type,
                duration_ms=round(duration_ms, 2),
                final_url=response.url,
                success=response.status_code < 400,
                response_headers=dict(response.headers),
            )

        except requests.exceptions.Timeout:
            duration_ms = (time.monotonic() - start) * 1000
            return FetchResult(
                url=url,
                html="",
                status_code=0,
                content_type="",
                duration_ms=round(duration_ms, 2),
                final_url=url,
                success=False,
                error=f"Request timed out after {self.timeout}s",
            )

        except requests.exceptions.ConnectionError as exc:
            duration_ms = (time.monotonic() - start) * 1000
            return FetchResult(
                url=url,
                html="",
                status_code=0,
                content_type="",
                duration_ms=round(duration_ms, 2),
                final_url=url,
                success=False,
                error=f"Connection error: {exc}",
            )

        except requests.exceptions.RequestException as exc:
            duration_ms = (time.monotonic() - start) * 1000
            return FetchResult(
                url=url,
                html="",
                status_code=0,
                content_type="",
                duration_ms=round(duration_ms, 2),
                final_url=url,
                success=False,
                error=f"Request error: {exc}",
            )

    def close(self) -> None:
        """Close the underlying session."""
        self._session.close()

    def __enter__(self) -> "RequestsFetcher":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
