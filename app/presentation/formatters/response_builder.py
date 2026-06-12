"""Response builder helper class for presentation layer."""

from typing import Any, Dict

from app.presentation.formatters.job_intelligence_formatter import (
    JobIntelligenceFormatter,
)
from app.presentation.schemas.job_intelligence import JobIntelligenceReport


class ResponseBuilder:
    """Builder class that maps raw pipeline state outputs to standard API response models."""

    @staticmethod
    def build_report(state: Dict[str, Any]) -> JobIntelligenceReport:
        """Transform internal PipelineState into the canonical JobIntelligenceReport contract."""
        return JobIntelligenceFormatter.format(state)
