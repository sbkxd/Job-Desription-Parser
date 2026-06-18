"""Resume PDF Parser using pdfminer."""

import os

from app.logging.logger import get_logger

logger = get_logger(__name__)


class ResumeParser:
    """PDF parser extracting raw text content from resume documents."""

    def parse(self, pdf_path: str) -> str:
        """Parse text from local PDF file path.

        Args:
            pdf_path: Path to the local PDF file.

        Returns:
            The raw text content.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Resume PDF file not found at: {pdf_path}")

        logger.info("Parsing resume PDF", file_path=pdf_path)

        try:
            from pdfminer.high_level import extract_text as extract_pdf_text

            text = extract_pdf_text(pdf_path)
            if not text:
                logger.warning("Extracted empty text from PDF", file_path=pdf_path)
                return ""

            logger.info(
                "Successfully extracted text from resume PDF", size_bytes=len(text)
            )
            return text
        except Exception as e:
            logger.error("Failed to parse resume PDF", file_path=pdf_path, error=str(e))
            raise RuntimeError(f"Error parsing resume PDF: {str(e)}") from e
