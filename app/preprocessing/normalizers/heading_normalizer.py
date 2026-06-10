"""Heading normalizer — standardizes heading surface forms.

Strips trailing punctuation, normalizes casing, and resolves
well-known heading aliases into canonical representation.
"""

import re

from app.preprocessing.schemas.schemas import SectionType

# ---------------------------------------------------------------------------
# Compiled patterns
# ---------------------------------------------------------------------------

_RE_TRAILING_PUNCT = re.compile(r"[\s:*\-_#]+$")
_RE_LEADING_PUNCT = re.compile(r"^[\s\-_*#]+")
_RE_MULTI_SPACE = re.compile(r"\s+")

# ---------------------------------------------------------------------------
# Heading alias table
#
# Maps every known surface form (lowercased, stripped) → SectionType
# ---------------------------------------------------------------------------

_HEADING_ALIASES: dict[str, SectionType] = {
    # --- RESPONSIBILITIES ---
    "responsibilities": SectionType.RESPONSIBILITIES,
    "job responsibilities": SectionType.RESPONSIBILITIES,
    "key responsibilities": SectionType.RESPONSIBILITIES,
    "core responsibilities": SectionType.RESPONSIBILITIES,
    "role responsibilities": SectionType.RESPONSIBILITIES,
    "your responsibilities": SectionType.RESPONSIBILITIES,
    "what you will do": SectionType.RESPONSIBILITIES,
    "what you'll do": SectionType.RESPONSIBILITIES,
    "what you'd do": SectionType.RESPONSIBILITIES,
    "what you would do": SectionType.RESPONSIBILITIES,
    "you will": SectionType.RESPONSIBILITIES,
    "you'll": SectionType.RESPONSIBILITIES,
    "the role": SectionType.RESPONSIBILITIES,
    "role overview": SectionType.RESPONSIBILITIES,
    "position overview": SectionType.RESPONSIBILITIES,
    "job description": SectionType.RESPONSIBILITIES,
    "position summary": SectionType.RESPONSIBILITIES,
    "overview": SectionType.RESPONSIBILITIES,
    "day to day": SectionType.RESPONSIBILITIES,
    "day-to-day": SectionType.RESPONSIBILITIES,
    "duties": SectionType.RESPONSIBILITIES,
    "key duties": SectionType.RESPONSIBILITIES,
    "primary duties": SectionType.RESPONSIBILITIES,
    "main duties": SectionType.RESPONSIBILITIES,
    "essential duties": SectionType.RESPONSIBILITIES,
    "essential functions": SectionType.RESPONSIBILITIES,
    "essential job functions": SectionType.RESPONSIBILITIES,
    "functions": SectionType.RESPONSIBILITIES,
    "tasks": SectionType.RESPONSIBILITIES,
    "key tasks": SectionType.RESPONSIBILITIES,
    "scope of work": SectionType.RESPONSIBILITIES,
    "deliverables": SectionType.RESPONSIBILITIES,
    "in this role you will": SectionType.RESPONSIBILITIES,
    "in this role": SectionType.RESPONSIBILITIES,
    "what does the job involve": SectionType.RESPONSIBILITIES,
    "what does the role involve": SectionType.RESPONSIBILITIES,
    "you will be responsible for": SectionType.RESPONSIBILITIES,
    "your role": SectionType.RESPONSIBILITIES,
    "your day": SectionType.RESPONSIBILITIES,
    # --- REQUIREMENTS ---
    "requirements": SectionType.REQUIREMENTS,
    "job requirements": SectionType.REQUIREMENTS,
    "role requirements": SectionType.REQUIREMENTS,
    "key requirements": SectionType.REQUIREMENTS,
    "must have": SectionType.REQUIREMENTS,
    "must-have": SectionType.REQUIREMENTS,
    "required qualifications": SectionType.REQUIREMENTS,
    "qualifications": SectionType.REQUIREMENTS,
    "skills": SectionType.REQUIREMENTS,
    "minimum qualifications": SectionType.REQUIREMENTS,
    "basic qualifications": SectionType.REQUIREMENTS,
    "required skills": SectionType.REQUIREMENTS,
    "required experience": SectionType.REQUIREMENTS,
    "required": SectionType.REQUIREMENTS,
    "experience required": SectionType.REQUIREMENTS,
    "skills required": SectionType.REQUIREMENTS,
    "skills and experience": SectionType.REQUIREMENTS,
    "skills and qualifications": SectionType.REQUIREMENTS,
    "education and experience": SectionType.REQUIREMENTS,
    "education": SectionType.REQUIREMENTS,
    "educational requirements": SectionType.REQUIREMENTS,
    "experience": SectionType.REQUIREMENTS,
    "work experience": SectionType.REQUIREMENTS,
    "professional experience": SectionType.REQUIREMENTS,
    "technical skills": SectionType.REQUIREMENTS,
    "technical requirements": SectionType.REQUIREMENTS,
    "competencies": SectionType.REQUIREMENTS,
    "core competencies": SectionType.REQUIREMENTS,
    "key competencies": SectionType.REQUIREMENTS,
    "who you are": SectionType.REQUIREMENTS,
    "what we're looking for": SectionType.REQUIREMENTS,
    "what we are looking for": SectionType.REQUIREMENTS,
    "what you bring": SectionType.REQUIREMENTS,
    "what you'll bring": SectionType.REQUIREMENTS,
    "you bring": SectionType.REQUIREMENTS,
    "you have": SectionType.REQUIREMENTS,
    "you should have": SectionType.REQUIREMENTS,
    "you must have": SectionType.REQUIREMENTS,
    "ideal candidate": SectionType.REQUIREMENTS,
    "ideal candidate will have": SectionType.REQUIREMENTS,
    "candidate requirements": SectionType.REQUIREMENTS,
    "we require": SectionType.REQUIREMENTS,
    "we need": SectionType.REQUIREMENTS,
    "we're looking for someone who": SectionType.REQUIREMENTS,
    "we are looking for someone who": SectionType.REQUIREMENTS,
    "mandatory skills": SectionType.REQUIREMENTS,
    "mandatory requirements": SectionType.REQUIREMENTS,
    "essential requirements": SectionType.REQUIREMENTS,
    "essential skills": SectionType.REQUIREMENTS,
    "core skills": SectionType.REQUIREMENTS,
    "profile": SectionType.REQUIREMENTS,
    "candidate profile": SectionType.REQUIREMENTS,
    # --- NICE TO HAVE ---
    "nice to have": SectionType.NICE_TO_HAVE,
    "nice-to-have": SectionType.NICE_TO_HAVE,
    "good to have": SectionType.NICE_TO_HAVE,
    "good-to-have": SectionType.NICE_TO_HAVE,
    "preferred qualifications": SectionType.NICE_TO_HAVE,
    "preferred skills": SectionType.NICE_TO_HAVE,
    "preferred experience": SectionType.NICE_TO_HAVE,
    "preferred": SectionType.NICE_TO_HAVE,
    "desirable": SectionType.NICE_TO_HAVE,
    "desirable skills": SectionType.NICE_TO_HAVE,
    "desirable qualifications": SectionType.NICE_TO_HAVE,
    "additional skills": SectionType.NICE_TO_HAVE,
    "bonus skills": SectionType.NICE_TO_HAVE,
    "bonus points": SectionType.NICE_TO_HAVE,
    "bonus": SectionType.NICE_TO_HAVE,
    "plus": SectionType.NICE_TO_HAVE,
    "a plus": SectionType.NICE_TO_HAVE,
    "would be a plus": SectionType.NICE_TO_HAVE,
    "optional": SectionType.NICE_TO_HAVE,
    "optional skills": SectionType.NICE_TO_HAVE,
    "what would be great": SectionType.NICE_TO_HAVE,
    "what would make you stand out": SectionType.NICE_TO_HAVE,
    "advantageous": SectionType.NICE_TO_HAVE,
    "an advantage": SectionType.NICE_TO_HAVE,
    "if you have": SectionType.NICE_TO_HAVE,
    "extra points": SectionType.NICE_TO_HAVE,
    # --- ABOUT COMPANY ---
    "about us": SectionType.ABOUT_COMPANY,
    "about the company": SectionType.ABOUT_COMPANY,
    "about the team": SectionType.ABOUT_COMPANY,
    "about the role": SectionType.ABOUT_COMPANY,
    "about this role": SectionType.ABOUT_COMPANY,
    "about": SectionType.ABOUT_COMPANY,
    "company overview": SectionType.ABOUT_COMPANY,
    "company description": SectionType.ABOUT_COMPANY,
    "who we are": SectionType.ABOUT_COMPANY,
    "who are we": SectionType.ABOUT_COMPANY,
    "our company": SectionType.ABOUT_COMPANY,
    "our team": SectionType.ABOUT_COMPANY,
    "our culture": SectionType.ABOUT_COMPANY,
    "culture": SectionType.ABOUT_COMPANY,
    "the company": SectionType.ABOUT_COMPANY,
    "our mission": SectionType.ABOUT_COMPANY,
    "our vision": SectionType.ABOUT_COMPANY,
    "our story": SectionType.ABOUT_COMPANY,
    "organization overview": SectionType.ABOUT_COMPANY,
    "team overview": SectionType.ABOUT_COMPANY,
    # --- BENEFITS ---
    "benefits": SectionType.BENEFITS,
    "what we offer": SectionType.BENEFITS,
    "what's in it for you": SectionType.BENEFITS,
    "whats in it for you": SectionType.BENEFITS,
    "perks": SectionType.BENEFITS,
    "perks and benefits": SectionType.BENEFITS,
    "compensation and benefits": SectionType.BENEFITS,
    "salary and benefits": SectionType.BENEFITS,
    "remuneration": SectionType.BENEFITS,
    "compensation": SectionType.BENEFITS,
    "pay and benefits": SectionType.BENEFITS,
    "employee benefits": SectionType.BENEFITS,
    "what you get": SectionType.BENEFITS,
    "we offer": SectionType.BENEFITS,
    "offer": SectionType.BENEFITS,
    "our offer": SectionType.BENEFITS,
    "package": SectionType.BENEFITS,
    "total rewards": SectionType.BENEFITS,
    "why join us": SectionType.BENEFITS,
    "why work with us": SectionType.BENEFITS,
    "why us": SectionType.BENEFITS,
    "incentives": SectionType.BENEFITS,
}


class HeadingNormalizer:
    """Normalizes raw heading text and resolves aliases to SectionType.

    Usage::

        normalizer = HeadingNormalizer()
        cleaned = normalizer.normalize_line("KEY RESPONSIBILITIES:")
        section_type = normalizer.resolve(cleaned)
    """

    def normalize_line(self, line: str) -> str:
        """Strip punctuation, collapse whitespace, title-case a heading line.

        Examples:
            "KEY RESPONSIBILITIES:" → "Key Responsibilities"
            "  requirements --"    → "Requirements"
            "### About Us ###"     → "About Us"
        """
        # Strip markdown / decorative leading characters
        line = _RE_LEADING_PUNCT.sub("", line)
        # Strip trailing punctuation
        line = _RE_TRAILING_PUNCT.sub("", line)
        # Collapse internal whitespace
        line = _RE_MULTI_SPACE.sub(" ", line)
        return line.strip().title()

    def normalize_key(self, line: str) -> str:
        """Return a lowercase, stripped version for alias lookup."""
        line = _RE_LEADING_PUNCT.sub("", line)
        line = _RE_TRAILING_PUNCT.sub("", line)
        line = _RE_MULTI_SPACE.sub(" ", line)
        return line.strip().lower()

    def resolve(self, heading_text: str) -> SectionType | None:
        """Resolve a heading text to a SectionType via the alias table.

        Returns None when no match is found (caller handles fallback).
        """
        key = self.normalize_key(heading_text)
        if key in _HEADING_ALIASES:
            return _HEADING_ALIASES[key]

        if key.startswith("about "):
            return SectionType.ABOUT_COMPANY

        return None

    @property
    def alias_table(self) -> dict[str, SectionType]:
        """Read-only access to the full alias table."""
        return dict(_HEADING_ALIASES)
