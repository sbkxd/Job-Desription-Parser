"""Playwright-based async fetcher for JavaScript-rendered job pages."""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any

_PLAYWRIGHT_AVAILABLE = False
try:
    from playwright.async_api import (
        Browser,
        BrowserContext,
        Page,
        async_playwright,
    )

    _PLAYWRIGHT_AVAILABLE = True
except ImportError:
    pass

_DEFAULT_VIEWPORT = {"width": 1280, "height": 800}
_DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


@dataclass
class PlaywrightResult:
    """Output of a Playwright-based fetch attempt."""

    url: str
    html: str
    final_url: str
    status_code: int
    duration_ms: float
    success: bool
    error: str | None = None
    console_errors: list[str] = field(default_factory=list)
    response_headers: dict[str, Any] = field(default_factory=dict)


class PlaywrightFetcher:
    """
    Async Playwright fetcher for JavaScript-heavy job pages.

    Supports:
    - Headless Chromium rendering
    - Configurable wait strategies (networkidle / load / domcontentloaded)
    - Scroll to trigger lazy-loaded content
    - Cookie/bot detection evasion headers
    - Configurable timeout
    - Never raises — all errors captured in PlaywrightResult.error
    """

    def __init__(
        self,
        timeout_ms: int = 30_000,
        wait_until: str = "networkidle",
        headless: bool = True,
        scroll: bool = True,
    ) -> None:
        """
        Args:
            timeout_ms: Navigation timeout in milliseconds.
            wait_until: Playwright wait event. One of:
                        'load', 'domcontentloaded', 'networkidle', 'commit'.
            headless: Run browser in headless mode.
            scroll: Scroll the page after load to trigger lazy content.
        """
        self.timeout_ms = timeout_ms
        self.wait_until = wait_until
        self.headless = headless
        self.scroll = scroll

    @property
    def is_available(self) -> bool:
        """Return True if playwright is installed."""
        return _PLAYWRIGHT_AVAILABLE

    async def fetch(self, url: str) -> PlaywrightResult:
        """
        Fetch a URL using a headless Chromium browser.

        Returns PlaywrightResult — never raises.
        """
        if not _PLAYWRIGHT_AVAILABLE:
            return PlaywrightResult(
                url=url,
                html="",
                final_url=url,
                status_code=0,
                duration_ms=0.0,
                success=False,
                error="Playwright is not installed. Run: playwright install chromium",
            )

        start = time.monotonic()
        try:
            return await self._do_fetch(url, start)
        except Exception as exc:
            duration_ms = (time.monotonic() - start) * 1000
            return PlaywrightResult(
                url=url,
                html="",
                final_url=url,
                status_code=0,
                duration_ms=round(duration_ms, 2),
                success=False,
                error=f"Unexpected error: {exc}",
            )

    async def _do_fetch(self, url: str, start: float) -> PlaywrightResult:
        """Internal async fetch with browser lifecycle management."""
        console_errors: list[str] = []

        async with async_playwright() as pw:
            browser: Browser = await pw.chromium.launch(headless=self.headless)
            context: BrowserContext = await browser.new_context(
                viewport=_DEFAULT_VIEWPORT,
                user_agent=_DEFAULT_USER_AGENT,
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept": (
                        "text/html,application/xhtml+xml,application/xml;"
                        "q=0.9,image/webp,*/*;q=0.8"
                    ),
                },
            )

            page: Page = await context.new_page()

            # Capture console errors for diagnostics
            page.on(
                "console",
                lambda msg: (
                    console_errors.append(msg.text) if msg.type == "error" else None
                ),
            )

            try:
                response = await page.goto(
                    url,
                    timeout=self.timeout_ms,
                    wait_until=self.wait_until,  # type: ignore[arg-type]
                )

                if self.scroll:
                    await self._scroll_page(page)

                html = await page.content()
                duration_ms = (time.monotonic() - start) * 1000

                status_code = response.status if response else 0
                final_url = page.url
                headers = dict(response.headers) if response else {}

                return PlaywrightResult(
                    url=url,
                    html=html,
                    final_url=final_url,
                    status_code=status_code,
                    duration_ms=round(duration_ms, 2),
                    success=status_code < 400 if status_code else len(html) > 0,
                    console_errors=console_errors[:10],  # Cap at 10
                    response_headers=headers,
                )

            except asyncio.TimeoutError:
                duration_ms = (time.monotonic() - start) * 1000
                return PlaywrightResult(
                    url=url,
                    html="",
                    final_url=url,
                    status_code=0,
                    duration_ms=round(duration_ms, 2),
                    success=False,
                    error=f"Navigation timed out after {self.timeout_ms}ms",
                )

            except Exception as exc:
                duration_ms = (time.monotonic() - start) * 1000
                # Try to get partial HTML before giving up
                html = ""
                try:
                    html = await page.content()
                except Exception:
                    pass

                return PlaywrightResult(
                    url=url,
                    html=html,
                    final_url=page.url if page else url,
                    status_code=0,
                    duration_ms=round(duration_ms, 2),
                    success=len(html) > 100,
                    error=str(exc),
                )

            finally:
                await context.close()
                await browser.close()

    async def _scroll_page(self, page: "Page") -> None:
        """Scroll the page to trigger lazy-loaded content."""
        try:
            await page.evaluate(
                """
                () => new Promise((resolve) => {
                    let totalHeight = 0;
                    const distance = 300;
                    const timer = setInterval(() => {
                        window.scrollBy(0, distance);
                        totalHeight += distance;
                        if (totalHeight >= document.body.scrollHeight) {
                            clearInterval(timer);
                            resolve();
                        }
                    }, 100);
                    setTimeout(() => { clearInterval(timer); resolve(); }, 3000);
                })
                """
            )
        except Exception:
            pass  # Scroll failure is non-fatal
