"""Content type classifier categorizing text lines without calling LLMs."""

import re

from app.preprocessing.noise.rules import (
    AtsArtifactRule,
    ContactInfoRule,
    JobBoardRule,
    LegalRule,
    LinkedInArtifactRule,
    MetadataRule,
    NavigationRule,
)


class ContentTypeClassifier:
    """Classifies raw lines into semantic categories based on heuristics and lexicons."""

    def __init__(self) -> None:
        self.rules = [
            ContactInfoRule(),
            AtsArtifactRule(),
            LinkedInArtifactRule(),
            JobBoardRule(),
            MetadataRule(),
            LegalRule(),
            NavigationRule(),
        ]

        # Verb action list for responsibilities
        self.verbs = {
            "develop",
            "design",
            "implement",
            "build",
            "maintain",
            "collaborate",
            "analyze",
            "lead",
            "support",
            "create",
            "manage",
            "optimize",
            "deliver",
            "write",
            "test",
            "deploy",
        }

        # Keyphrase lists
        self.education_keywords = {
            "bachelor",
            "degree",
            "master",
            "phd",
            "bs",
            "ms",
            "computer science",
        }
        self.benefit_keywords = {
            "health insurance",
            "401k",
            "remote work",
            "flexible schedule",
            "dental",
            "vision",
            "pto",
        }
        self.company_keywords = {
            "our mission",
            "we are a",
            "founded in",
            "company culture",
            "about us",
        }
        self.skill_keywords = {
            "python",
            "sql",
            "spark",
            "aws",
            "docker",
            "kubernetes",
            "git",
            "java",
            "c++",
            "c#",
            "rust",
            "typescript",
            "react",
        }

    def _check_noise_rules(self, line_clean: str) -> str | None:
        """Check line against noise rules."""
        for rule in self.rules:
            result = rule.evaluate(line_clean)
            if result["is_noise"]:
                if result["category"] == "CONTACT_INFORMATION":
                    return "CONTACT_INFO"
                if result["category"] == "EMPLOYMENT_METADATA":
                    return "METADATA"
                return "NOISE"
        return None

    def _check_keyword_cues(self, line_lower: str) -> str | None:
        """Check line against keyword categories."""
        if any(kw in line_lower for kw in self.education_keywords):
            return "EDUCATION"
        if any(kw in line_lower for kw in self.benefit_keywords):
            return "BENEFIT"
        if any(kw in line_lower for kw in self.company_keywords):
            return "COMPANY_INFO"
        if any(kw in line_lower for kw in self.skill_keywords):
            return "SKILL"
        return None

    def classify_line(self, line: str) -> str:
        """Classify a single text line into a canonical category.

        Args:
            line: The text line to inspect.

        Returns:
            A string representing the classification category.
        """
        line_clean = line.strip()
        if not line_clean:
            return "NOISE"

        # 1. Run Noise Rules first
        noise_cat = self._check_noise_rules(line_clean)
        if noise_cat is not None:
            return noise_cat

        # 2. Check keyword cues
        line_lower = line_clean.lower()
        cue_cat = self._check_keyword_cues(line_lower)
        if cue_cat is not None:
            return cue_cat

        # 3. Check Qualifications (cues like "years experience", "3+ years")
        if re.search(r"\d+\+?\s+years?", line_lower) or any(
            kw in line_lower
            for kw in {"required", "preferred", "qualification", "requirement"}
        ):
            return "QUALIFICATION"

        # 4. Check Responsibilities (action statements starting with action verbs)
        words = [w.strip("-,. ") for w in line_lower.split()]
        if words and (
            words[0] in self.verbs
            or (len(words) > 1 and words[0] == "to" and words[1] in self.verbs)
        ):
            return "RESPONSIBILITY"

        # Default fallback
        return "RESPONSIBILITY"  # Default assumption for body items unless flagged
