"""Concrete implementations of NoiseRule using the patterns library."""

from typing import Any, Dict

from app.preprocessing.noise.patterns import patterns
from app.preprocessing.noise.rules.base import NoiseRule


class ContactInfoRule(NoiseRule):
    """Rule to detect emails, phone numbers, and social links."""

    def evaluate(self, text: str) -> Dict[str, Any]:
        text_strip = text.strip()
        if patterns.EMAIL_PATTERN.search(text_strip):
            return {
                "is_noise": True,
                "category": "CONTACT_INFORMATION",
                "confidence": 1.0,
            }
        if patterns.PHONE_PATTERN.search(text_strip):
            return {
                "is_noise": True,
                "category": "CONTACT_INFORMATION",
                "confidence": 0.95,
            }
        if patterns.SOCIAL_MEDIA_PATTERN.search(text_strip):
            return {
                "is_noise": True,
                "category": "CONTACT_INFORMATION",
                "confidence": 0.90,
            }
        return {"is_noise": False, "category": "NONE", "confidence": 0.0}


class AtsArtifactRule(NoiseRule):
    """Rule to detect ATS form helpers like 'This section auto-populates'."""

    def evaluate(self, text: str) -> Dict[str, Any]:
        text_strip = text.strip()
        for p in patterns.ATS_FORM_PATTERNS:
            if p.search(text_strip):
                return {
                    "is_noise": True,
                    "category": "ATS_FORM_ARTIFACTS",
                    "confidence": 1.0,
                }
        return {"is_noise": False, "category": "NONE", "confidence": 0.0}


class LinkedInArtifactRule(NoiseRule):
    """Rule to detect LinkedIn specific platform text and recommendations."""

    def evaluate(self, text: str) -> Dict[str, Any]:
        text_strip = text.strip()
        for p in patterns.LINKEDIN_PATTERNS:
            if p.search(text_strip):
                return {
                    "is_noise": True,
                    "category": "LINKEDIN_ARTIFACTS",
                    "confidence": 0.95,
                }
        return {"is_noise": False, "category": "NONE", "confidence": 0.0}


class JobBoardRule(NoiseRule):
    """Rule to detect Naukri or generic job board artifacts."""

    def evaluate(self, text: str) -> Dict[str, Any]:
        text_strip = text.strip()
        for p in patterns.NAUKRI_PATTERNS:
            if p.search(text_strip):
                return {
                    "is_noise": True,
                    "category": "JOB_BOARD_ARTIFACTS",
                    "confidence": 0.95,
                }
        return {"is_noise": False, "category": "NONE", "confidence": 0.0}


class MetadataRule(NoiseRule):
    """Rule to detect employment metadata headers (e.g. 'Employment Type')."""

    def evaluate(self, text: str) -> Dict[str, Any]:
        text_strip = text.strip()
        for p in patterns.METADATA_LABELS:
            if p.match(text_strip):
                return {
                    "is_noise": True,
                    "category": "EMPLOYMENT_METADATA",
                    "confidence": 0.95,
                }
        return {"is_noise": False, "category": "NONE", "confidence": 0.0}


class LegalRule(NoiseRule):
    """Rule to detect company legal disclaimers (e.g. 'Equal Opportunity Employer')."""

    def evaluate(self, text: str) -> Dict[str, Any]:
        text_strip = text.strip()
        for p in patterns.LEGAL_PATTERNS:
            if p.search(text_strip):
                return {
                    "is_noise": True,
                    "category": "COMPANY_LEGAL_TEXT",
                    "confidence": 0.90,
                }
        return {"is_noise": False, "category": "NONE", "confidence": 0.0}


class NavigationRule(NoiseRule):
    """Rule to detect website navigation and calls to action (e.g. 'Back to Search')."""

    def evaluate(self, text: str) -> Dict[str, Any]:
        text_strip = text.strip()
        for p in patterns.NAVIGATION_PATTERNS:
            if p.match(text_strip):
                return {
                    "is_noise": True,
                    "category": "NAVIGATION_TEXT",
                    "confidence": 0.95,
                }
        return {"is_noise": False, "category": "NONE", "confidence": 0.0}
