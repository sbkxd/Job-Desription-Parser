"""Skill extraction engine combining DeBERTa NER with a Gazetteer."""

import re

from app.extraction.models.model_manager import ModelManager
from app.extraction.schemas.schemas import SkillMention

# Gazette of common skills grouped by type for exact/fuzzy regex matching
_GAZETTEER_SKILLS = [
    # Languages
    "Python",
    "JavaScript",
    "TypeScript",
    "Go",
    "Golang",
    "Java",
    "C++",
    "C#",
    "C-sharp",
    "Ruby",
    "PHP",
    "Rust",
    "Scala",
    "Kotlin",
    "Swift",
    "Objective-C",
    "HTML",
    "HTML5",
    "CSS",
    "CSS3",
    "SQL",
    "PostgreSQL",
    "MySQL",
    "NoSQL",
    "GraphQL",
    "Bash",
    "Shell",
    "Perl",
    "R",
    # Frameworks & Libraries
    "FastAPI",
    "Django",
    "Flask",
    "React",
    "React.js",
    "ReactJS",
    "Angular",
    "Vue",
    "Vue.js",
    "Node",
    "Node.js",
    "Express",
    "Spring",
    "Spring Boot",
    "Rails",
    "Laravel",
    "Symfony",
    "PyTorch",
    "TensorFlow",
    "Keras",
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "Spark",
    "Hadoop",
    "Bootstrap",
    "Tailwind",
    "Next.js",
    "ASP.NET",
    # Tools, Platforms & DevOps
    "AWS",
    "GCP",
    "Azure",
    "Docker",
    "Kubernetes",
    "Git",
    "GitHub",
    "GitLab",
    "Jenkins",
    "Jira",
    "Linux",
    "Unix",
    "Windows",
    "MacOS",
    "Kubectl",
    "Terraform",
    "Ansible",
    # Databases & Caches
    "MongoDB",
    "Redis",
    "Elasticsearch",
    "Cassandra",
    "SQLite",
    "Oracle",
    "MariaDB",
    # Concepts
    "REST",
    "RESTful",
    "Microservices",
    "CI/CD",
    "Agile",
    "Scrum",
    "TDD",
    "OOP",
    "Machine Learning",
    "Deep Learning",
    "NLP",
    "Computer Vision",
    "Data Science",
]

# Compile patterns with word boundaries (handling special chars like C++ and C# carefully)
_GAZETTEER_PATTERNS = []
for skill in _GAZETTEER_SKILLS:
    escaped_skill = re.escape(skill)
    # If the skill ends in special characters like ++ or #, word boundaries \b won't match properly at the end
    if skill.endswith("++") or skill.endswith("#"):
        pattern_str = rf"(?i)\b{escaped_skill}"
    else:
        pattern_str = rf"(?i)\b{escaped_skill}\b"
    _GAZETTEER_PATTERNS.append((re.compile(pattern_str), skill))


class SkillsExtractor:
    """Extracts and post-processes skill mentions from job descriptions."""

    def __init__(self) -> None:
        self.model_manager = ModelManager()

    def extract(self, sections: dict[str, list[str]]) -> list[SkillMention]:
        """Extract skills from responsibilities, requirements, and nice_to_have sections.

        Args:
            sections: Dictionary of section_type -> list of lines.

        Returns:
            List of unique SkillMention objects.
        """
        mentions: list[SkillMention] = []

        # Target only the relevant sections for skill extraction
        target_sections = ["responsibilities", "requirements", "nice_to_have"]

        for sec_name in target_sections:
            lines = sections.get(sec_name, [])
            if not lines:
                continue

            # Process line by line
            for line in lines:
                line_mentions = self._extract_from_line(line, sec_name)
                mentions.extend(line_mentions)

        return self._post_process(mentions)

    def _extract_from_line(self, line: str, section: str) -> list[SkillMention]:
        """Extract mentions from a single line using Gazetteer and DeBERTa NER."""
        found: dict[str, SkillMention] = {}

        # 1. Gazetteer Matching (high confidence)
        for pattern, canonical_name in _GAZETTEER_PATTERNS:
            for match in pattern.finditer(line):
                matched_text = match.group(0)
                # Resolve canonical casing if matched in different casings (e.g. PYTHON -> Python)
                resolved_name = self._resolve_casing(matched_text, canonical_name)
                found[resolved_name.lower()] = SkillMention(
                    name=resolved_name,
                    confidence=0.95,
                    section=section,
                )

        # 2. DeBERTa NER Pipeline Inference
        try:
            nlp = self.model_manager.get_pipeline()
            entities = nlp(line)
            for ent in entities:
                # Token classifiers return dicts with 'word', 'score', 'entity_group', etc.
                word = ent.get("word", "").strip()
                score = float(ent.get("score", 0.0))

                # Clean up word (remove special tokens like ## if using WordPiece, sub-words, etc.)
                word = word.replace("##", "").strip(" .,:;()[]-")

                # Filter out short/meaningless entities or low confidence
                if len(word) > 1 and score > 0.6:
                    # Check if it looks like a valid skill (not already found by gazetteer)
                    key = word.lower()
                    if key not in found:
                        # Standardize version or casing
                        resolved_name = self._resolve_casing(word)
                        found[key] = SkillMention(
                            name=resolved_name,
                            confidence=round(score, 2),
                            section=section,
                        )
        except Exception:
            # NER failure is handled gracefully; gazetteer fallback provides robustness
            pass

        return list(found.values())

    @staticmethod
    def _resolve_casing(text: str, canonical: str | None = None) -> str:
        """Resolve casing variations (e.g. python/PYTHON -> Python)."""
        text_stripped = text.strip(" .,:;()[]-")
        if canonical:
            return canonical

        # Simple common casing rule
        if text_stripped.lower() == "python":
            return "Python"
        if text_stripped.lower() == "sql":
            return "SQL"
        if text_stripped.lower() in (
            "aws",
            "gcp",
            "api",
            "rest",
            "nosql",
            "html",
            "css",
            "ip",
        ):
            return text_stripped.upper()

        # Default: Title Case
        return text_stripped.title()

    @staticmethod
    def _post_process(mentions: list[SkillMention]) -> list[SkillMention]:
        """Milestone 4.4: Post-process raw skill mentions.

        - Deduplicates (taking the highest confidence and preferred section).
        - Version/Case unification.
        - Keeps distinct framework variations separate (e.g. React vs ReactJS).
        """
        deduped: dict[str, SkillMention] = {}

        for m in mentions:
            # Normalize casing for deduplication key
            key = m.name.lower()

            if key not in deduped:
                deduped[key] = m
            else:
                # Keep the one with higher confidence
                existing = deduped[key]
                if m.confidence > existing.confidence:
                    deduped[key] = m
                elif m.confidence == existing.confidence:
                    # Prefer 'requirements' > 'responsibilities' > 'nice_to_have'
                    pref = {"requirements": 3, "responsibilities": 2, "nice_to_have": 1}
                    if pref.get(m.section, 0) > pref.get(existing.section, 0):
                        deduped[key] = m

        # Convert back to sorted list of mentions by name
        return sorted(deduped.values(), key=lambda x: x.name)
