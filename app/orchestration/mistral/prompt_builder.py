"""Module for loading and constructing prompts for Mistral Small Latest."""

import os
from typing import Any, Dict, List

PROMPTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts"
)


class PromptBuilder:
    """Helper to build strict JSON-enforcing prompts for Mistral."""

    def __init__(self, prompts_dir: str = PROMPTS_DIR) -> None:
        self.prompts_dir = prompts_dir

    def _load_prompt(self, filename: str) -> str:
        path = os.path.join(self.prompts_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def build_ambiguous_skill_prompt(
        self, skill: str, context: str, candidates: List[str]
    ) -> str:
        """Construct a prompt to resolve ambiguous tech skill mapping."""
        template = self._load_prompt("ambiguous_skill_resolution.md")
        candidates_str = ", ".join(candidates)
        # Ensure we escape curly braces for JSON instructions
        prompt = template.format(
            skill=skill, context=context, candidates=candidates_str
        )
        return (
            prompt
            + "\nStrictly output ONLY valid JSON. No conversational introduction, ending, or explanation."
        )

    def build_taxonomy_disambiguation_prompt(
        self, skill: str, context: str, candidates: List[Dict[str, Any]]
    ) -> str:
        """Construct a prompt to disambiguate a skill against ESCO taxonomy candidates."""
        template = self._load_prompt("taxonomy_disambiguation.md")
        candidates_str = str(candidates)
        prompt = template.format(
            skill=skill, context=context, candidates=candidates_str
        )
        return (
            prompt
            + "\nStrictly output ONLY valid JSON. No conversational introduction, ending, or explanation."
        )

    def build_review_assistance_prompt(
        self, skill: str, context: str, review_reason: str
    ) -> str:
        """Construct a prompt to suggest category and confidence suggestions for reviews."""
        template = self._load_prompt("review_assistance.md")
        prompt = template.format(
            skill=skill, context=context, review_reason=review_reason
        )
        return (
            prompt
            + "\nStrictly output ONLY valid JSON. No conversational introduction, ending, or explanation."
        )
