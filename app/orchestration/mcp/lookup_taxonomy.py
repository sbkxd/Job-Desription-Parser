"""MCP tool for standardizing skill strings against the ESCO taxonomy."""

from typing import Any, Dict

from pydantic import BaseModel, Field

from app.normalization.services.normalization_service import SkillNormalizationService
from app.orchestration.mcp.base_tool import BaseMCPTool


class LookupTaxonomyInput(BaseModel):
    """Input parameters for the lookup_taxonomy tool."""

    skill: str = Field(..., description="The raw skill name string to standardize.")


class LookupTaxonomyTool(BaseMCPTool):
    """MCP tool to normalize a raw skill against the canonical ESCO taxonomy."""

    name: str = "lookup_taxonomy"
    description: str = (
        "Maps a raw skill name to a standard canonical concept in the ESCO taxonomy."
    )
    input_schema = LookupTaxonomyInput

    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Normalize a skill.

        Returns:
            Dict containing normalized_skill, esco_id, and confidence.
        """
        skill = kwargs["skill"]
        if not skill or not skill.strip():
            raise ValueError("Skill string must not be empty.")

        service = SkillNormalizationService()
        res = service.normalize([skill])
        normalized_skills = res.normalized_skills

        if not normalized_skills:
            return {
                "normalized_skill": skill,
                "esco_id": "unmapped",
                "confidence": 0.0,
            }

        ns = normalized_skills[0]
        return {
            "normalized_skill": ns.normalized_skill,
            "esco_id": ns.esco_id,
            "confidence": ns.confidence,
        }
