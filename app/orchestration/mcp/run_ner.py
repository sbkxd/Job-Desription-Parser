"""MCP tool for running information extraction (NER) on specific job description sections."""

from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.extraction.services.extraction_service import ExtractionService
from app.orchestration.mcp.base_tool import BaseMCPTool


class RunNERInput(BaseModel):
    """Input parameters for the run_ner tool."""

    text: str = Field(
        ..., description="The textual content of the job description section."
    )
    section: str = Field(
        default="requirements",
        description="The section type (e.g. responsibilities, requirements, nice_to_have, other).",
    )


class RunNERTool(BaseMCPTool):
    """MCP tool to extract structured attributes (skills, experience, seniority) using NER."""

    name: str = "run_ner"
    description: str = (
        "Extracts structured skills, experience, seniority, and requirements classification "
        "from a section of job description text."
    )
    input_schema = RunNERInput

    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute NER extraction.

        Returns:
            Dict containing skills, experience, seniority, and requirements classification.
        """
        text = kwargs["text"]
        section = kwargs.get("section", "requirements")

        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # Initialize full segmented structure
        segmented_doc: Dict[str, List[str]] = {
            "responsibilities": [],
            "requirements": [],
            "nice_to_have": [],
            "about_company": [],
            "benefits": [],
            "other": [],
        }

        sec_key = section.lower().strip()
        if sec_key in segmented_doc:
            segmented_doc[sec_key] = lines
        else:
            segmented_doc["requirements"] = lines

        service = ExtractionService()
        result = service.extract(segmented_doc)

        if not result.success:
            raise RuntimeError(f"NER Extraction failed: {result.error}")

        # Serialize results to simple dictionary matching tool expectations
        return {
            "skills": [
                {"name": s.name, "confidence": s.confidence} for s in result.skills
            ],
            "experience": {
                "min_years": result.experience.min_years,
                "max_years": result.experience.max_years,
            },
            "seniority": result.seniority.seniority if result.seniority else "",
            "requirements": [
                {
                    "text": req.text,
                    "classification": req.classification,
                    "confidence": req.confidence,
                }
                for req in result.requirements_classification
            ],
        }
