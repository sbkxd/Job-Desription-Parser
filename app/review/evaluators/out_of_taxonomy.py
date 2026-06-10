"""Detector for identifying skills and technologies outside of the ESCO taxonomy."""

from typing import TypedDict


class OutOfTaxonomyResult(TypedDict):
    raw_skill: str
    normalized_skill: str | None
    review_required: bool
    reason: str


class OutOfTaxonomyDetector:
    """Detects modern technologies not represented in the ESCO taxonomy."""

    def __init__(self, known_gaps: list[str] | None = None) -> None:
        # Standard known gaps in modern tech stack (e.g. LLM frameworks, MCP, auto-agents)
        self.known_gaps = known_gaps or [
            "langchain",
            "crewai",
            "autogen",
            "llamaindex",
            "mcp",
            "langgraph",
            "chromadb",
            "milvus",
            "qdrant",
            "vector database",
        ]

    def detect(self, raw_skill: str, esco_id: str | None = None) -> OutOfTaxonomyResult:
        """Evaluates whether the raw skill is considered out of taxonomy.

        Args:
            raw_skill: The raw skill name mentioned in the JD.
            esco_id: The resolved ESCO ID, if any.

        Returns:
            OutOfTaxonomyResult detailing classification.
        """
        cleaned_skill = raw_skill.strip().lower()

        # Check if skill matches any known out-of-taxonomy terms or if ESCO ID is 'unmapped'
        is_known_gap = cleaned_skill in self.known_gaps
        is_unmapped = esco_id is None or esco_id.lower() == "unmapped"

        if is_known_gap or is_unmapped:
            return {
                "raw_skill": raw_skill,
                "normalized_skill": None,
                "review_required": True,
                "reason": "OUT_OF_TAXONOMY",
            }

        return {
            "raw_skill": raw_skill,
            "normalized_skill": raw_skill,
            "review_required": False,
            "reason": "IN_TAXONOMY",
        }
