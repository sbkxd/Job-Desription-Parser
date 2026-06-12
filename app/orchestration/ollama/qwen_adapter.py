"""Adapter for mapping prompt templates and executing resolutions using Qwen3."""

import os
from typing import Any, Dict, List, Optional

from app.orchestration.ollama.ollama_client import OllamaClient

PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")


class QwenAdapter:
    """Formats inputs into prompt templates and delegates tasks to OllamaClient."""

    def __init__(self, client: Optional[OllamaClient] = None) -> None:
        self.client = client or OllamaClient()

    def _load_prompt(self, filename: str) -> str:
        path = os.path.join(PROMPTS_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    async def resolve_ambiguous_skill(
        self, skill: str, context: str, candidates: List[str]
    ) -> Dict[str, Any]:
        """Resolve an ambiguous skill name against a candidate list.

        Args:
            skill: The raw skill string.
            context: Sentence/context snippet.
            candidates: List of canonical ESCO skill names.

        Returns:
            Dict matching OllamaResolution schema.
        """
        template = self._load_prompt("ambiguous_skill_resolution.md")
        # Format candidate names list
        candidates_str = ", ".join(candidates)
        prompt = template.format(
            skill=skill, context=context, candidates=candidates_str
        )
        return await self.client.generate_json(prompt)

    async def disambiguate_taxonomy(
        self, skill: str, context: str, candidates: List[str]
    ) -> Dict[str, Any]:
        """Disambiguate a skill against ESCO taxonomy candidates.

        Args:
            skill: The raw skill string.
            context: Job description context snippet.
            candidates: Candidate dictionary representations.

        Returns:
            Dict matching OllamaResolution schema.
        """
        template = self._load_prompt("taxonomy_disambiguation.md")
        candidates_str = str(candidates)
        prompt = template.format(
            skill=skill, context=context, candidates=candidates_str
        )
        return await self.client.generate_json(prompt)

    async def assist_review(
        self, skill: str, context: str, review_reason: str
    ) -> Dict[str, Any]:
        """Suggest category and confidence suggestions for out-of-taxonomy review support.

        Args:
            skill: The raw skill name.
            context: Surrounding job description text context.
            review_reason: Reason for verification (e.g. OUT_OF_TAXONOMY).

        Returns:
            Dict containing category and confidence.
        """
        template = self._load_prompt("review_assistance.md")
        prompt = template.format(
            skill=skill, context=context, review_reason=review_reason
        )
        return await self.client.generate_json(prompt)
