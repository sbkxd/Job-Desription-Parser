"""Trafilatura-based HTML → clean text extractor for job description pages."""

from dataclasses import dataclass, field
from typing import Any

import trafilatura
from trafilatura.settings import use_config


@dataclass
class ParseResult:
    """Output of the HTML parsing stage."""

    raw_text: str
    title: str | None = None
    description: str | None = None
    author: str | None = None
    date: str | None = None
    url: str | None = None
    language: str | None = None
    word_count: int = 0
    success: bool = True
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class TrafilaturaParser:
    """
    Extracts clean, readable text from raw HTML using Trafilatura.

    Trafilatura applies content heuristics to strip navigation, ads,
    boilerplate and return the main textual content — ideal for JD pages.

    Strategy:
    1. Try Trafilatura extraction (primary).
    2. If result is empty/None, fall back to include_tables/comments modes.
    3. If all Trafilatura modes fail, return a minimal BeautifulSoup
       plaintext fallback.
    """

    def __init__(self, favor_recall: bool = True) -> None:
        """
        Args:
            favor_recall: When True, prefer broader extraction (fewer false
                          negatives). Recommended for job descriptions.
        """
        self.favor_recall = favor_recall
        self._config = use_config()
        # Tune: accept shorter documents (JDs can be sparse)
        self._config.set("DEFAULT", "MIN_EXTRACTED_SIZE", "200")
        self._config.set("DEFAULT", "MIN_DUPLCHECK_SIZE", "100")

    def parse(self, html: str, url: str | None = None) -> ParseResult:
        """
        Parse HTML and return a ParseResult.

        Never raises — all errors captured in ParseResult.error.
        """
        if not html or not html.strip():
            return ParseResult(
                raw_text="",
                success=False,
                error="Empty HTML input",
            )

        # Primary extraction attempt
        text = self._extract_text(html, url)

        # Fallback: try with include_tables enabled
        if not text:
            text = self._extract_text_fallback(html, url)

        # Last resort: BS4 plaintext
        if not text:
            text = self._bs4_fallback(html)

        if not text:
            return ParseResult(
                raw_text="",
                success=False,
                url=url,
                error="Trafilatura could not extract meaningful content",
            )

        # Extract metadata separately
        meta = self._extract_metadata(html, url)

        word_count = len(text.split())

        return ParseResult(
            raw_text=text.strip(),
            title=meta.get("title"),
            description=meta.get("description"),
            author=meta.get("author"),
            date=meta.get("date"),
            url=url or meta.get("url"),
            language=meta.get("language"),
            word_count=word_count,
            success=True,
            metadata=meta,
        )

    def _extract_text(self, html: str, url: str | None) -> str:
        """Primary trafilatura extraction."""
        try:
            result = trafilatura.extract(
                html,
                url=url,
                favor_recall=self.favor_recall,
                include_tables=True,
                include_links=False,
                include_images=False,
                deduplicate=True,
                no_fallback=False,
                config=self._config,
            )
            return result or ""
        except Exception:
            return ""

    def _extract_text_fallback(self, html: str, url: str | None) -> str:
        """Secondary trafilatura mode: broader recall."""
        try:
            result = trafilatura.extract(
                html,
                url=url,
                favor_recall=True,
                include_tables=True,
                include_comments=True,
                include_links=False,
                include_images=False,
                fast=True,
                config=self._config,
            )
            return result or ""
        except Exception:
            return ""

    def _bs4_fallback(self, html: str) -> str:
        """Last-resort: strip all HTML tags using BeautifulSoup."""
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style", "nav", "header", "footer"]):
                tag.decompose()
            return " ".join(soup.get_text(separator=" ").split())
        except ImportError:
            # Strip HTML naively if BS4 not installed
            import re

            return re.sub(r"<[^>]+>", " ", html).strip()
        except Exception:
            return ""

    def _extract_metadata(self, html: str, url: str | None) -> dict[str, Any]:
        """Extract metadata fields using trafilatura.extract_metadata."""
        meta: dict[str, Any] = {}
        try:
            result = trafilatura.extract_metadata(html, default_url=url)
            if result:
                meta["title"] = result.title
                meta["description"] = result.description
                meta["author"] = result.author
                meta["date"] = result.date
                meta["url"] = result.url
                meta["language"] = result.language
                meta["tags"] = result.tags
                meta["categories"] = result.categories
        except Exception:
            pass
        return {k: v for k, v in meta.items() if v is not None}
