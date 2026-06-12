"""MCP tool for fetching job description content from URLs or PDF files."""

import os
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.ingestion.detectors.url_detector import detector
from app.ingestion.fetchers.playwright_fetcher import PlaywrightFetcher
from app.ingestion.fetchers.requests_fetcher import RequestsFetcher
from app.ingestion.parsers.trafilatura_parser import TrafilaturaParser
from app.orchestration.mcp.base_tool import BaseMCPTool


class FetchJDInput(BaseModel):
    """Input parameters for the fetch_jd tool."""

    url: Optional[str] = Field(
        default=None, description="The URL of the job description to fetch."
    )
    pdf_path: Optional[str] = Field(
        default=None, description="The local path to a PDF job description."
    )


class FetchJDTool(BaseMCPTool):
    """MCP tool to retrieve job description text from URLs or local PDF files."""

    name: str = "fetch_jd"
    description: str = (
        "Fetches raw job description text and metadata from a URL or local PDF file."
    )
    input_schema = FetchJDInput

    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Fetch the JD content.

        Returns:
            Dict containing raw_text and metadata.
        """
        url = kwargs.get("url")
        pdf_path = kwargs.get("pdf_path")

        if not url and not pdf_path:
            raise ValueError("Either 'url' or 'pdf_path' must be provided.")

        if pdf_path:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

            from pdfminer.high_level import extract_text as extract_pdf_text

            text = extract_pdf_text(pdf_path)
            return {
                "raw_text": text or "",
                "metadata": {
                    "source_type": "pdf",
                    "file_path": pdf_path,
                    "file_size": os.path.getsize(pdf_path),
                },
            }

        # Handle URL fetching
        assert url is not None
        source_type = detector.detect(url)
        html_content = ""
        status_code = 0
        fetch_error = None
        duration_ms = 0.0

        if detector.requires_javascript(source_type):
            playwright_fetcher = PlaywrightFetcher()
            pw_res = await playwright_fetcher.fetch(url)
            html_content = pw_res.html
            status_code = pw_res.status_code
            fetch_error = pw_res.error
            duration_ms = pw_res.duration_ms
        else:
            with RequestsFetcher() as requests_fetcher:
                req_res = requests_fetcher.fetch(url)
                html_content = req_res.html
                status_code = req_res.status_code
                fetch_error = req_res.error
                duration_ms = req_res.duration_ms

        if fetch_error or not html_content:
            raise RuntimeError(
                f"Failed to fetch URL (status {status_code}): {fetch_error or 'No content returned'}"
            )

        # Parse content using Trafilatura
        parser = TrafilaturaParser()
        parse_res = parser.parse(html_content, url=url)

        if not parse_res.success:
            raise RuntimeError(f"Parsing failed: {parse_res.error}")

        metadata = {
            "source_type": source_type.value,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "title": parse_res.title,
            "word_count": parse_res.word_count,
            "url": url,
        }

        return {
            "raw_text": parse_res.raw_text,
            "metadata": metadata,
        }
