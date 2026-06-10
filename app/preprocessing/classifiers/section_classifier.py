"""Section classification engine — resolves raw section types and confidence scores.

Uses a multi-tiered strategy:
1. Exact or fuzzy heading match from heading detector (highest confidence).
2. Content keyword heuristic scoring (lower confidence) if heading is heuristic or missing.
3. Fallback to SectionType.OTHER if no clear signals exist.
"""

import re

from app.preprocessing.schemas.schemas import SectionType

# Heuristic keyword regexes for content classification
_RESPONSIBILITIES_KEYWORDS = [
    r"\bresponsibilit(y|ies)\b",
    r"\bdut(y|ies)\b",
    r"\btask(s)?\b",
    r"\bdevelop(ing|s|ed)?\b",
    r"\bmaintain(ing|s|ed)?\b",
    r"\bdesign(ing|s|ed)?\b",
    r"\bbuild(ing|s)?\b",
    r"\bimplement(ing|s|ed)?\b",
    r"\bcollaborat(e|ing|es|ed)?\b",
    r"\blead(ing|s)?\b",
    r"\bmanag(e|ing|es|ed)?\b",
    r"\bdeliver(ing|s|ed)?\b",
    r"\bsupport(ing|s|ed)?\b",
    r"\bdriv(e|ing|es)?\b",
    r"\bcreat(e|ing|es|ed)?\b",
    r"\bexecut(e|ing|es|ed)?\b",
    r"\bwrite\s+code\b",
    r"\barchitect\b",
    r"\btesting\b",
    r"\bdeploy(ing|s)?\b",
]

_REQUIREMENTS_KEYWORDS = [
    r"\brequirement(s)?\b",
    r"\bqualification(s)?\b",
    r"\bskill(s)?\b",
    r"\bexperience(s)?\b",
    r"\byear(s)?\b",
    r"\bdegree(s)?\b",
    r"\b(bs|ms|phd|bachelor|master|doctorate)\b",
    r"\bproficien(t|cy)\b",
    r"\bknowledge\b",
    r"\bability\s+to\b",
    r"\bexpert(ise)?\b",
    r"\bunderstand(ing)?\b",
    r"\bbackground\b",
    r"\bcompetenc(y|ies)\b",
    r"\btrack\s+record\b",
    r"\bfamiliar(ity)?\b",
    r"\bfluent\b",
    r"\bstrong\b",
    r"\bmust\s+have\b",
]

_NICE_TO_HAVE_KEYWORDS = [
    r"\bnice\s+to\s+have(s)?\b",
    r"\bplus\b",
    r"\bpreferred\b",
    r"\bdesir(e|able|ed)\b",
    r"\bbonus\b",
    r"\badvantage\b",
    r"\boptional\b",
    r"\bextra\s+points\b",
    r"\bhighly\s+regarded\b",
    r"\bbeneficial\b",
    r"\bplusses\b",
    r"\bhelpful\b",
    r"\bideal\b",
]

_ABOUT_COMPANY_KEYWORDS = [
    r"\babout\s+us\b",
    r"\bwho\s+we\s+are\b",
    r"\bour\s+company\b",
    r"\bculture\b",
    r"\bmission\b",
    r"\bvision\b",
    r"\bstartup\b",
    r"\bfounded\b",
    r"\bleading\s+provider\b",
    r"\bour\s+team\b",
    r"\bwe\s+are\b",
    r"\bworld's\s+leading\b",
    r"\bheadquartered\b",
    r"\bcompany\s+overview\b",
    r"\bscale-up\b",
    r"\bvalues\b",
    r"\bour\s+story\b",
]

_BENEFITS_KEYWORDS = [
    r"\bbenefit(s)?\b",
    r"\bperk(s)?\b",
    r"\bcompensation\b",
    r"\bsalary\b",
    r"\bmedical\b",
    r"\bdental\b",
    r"\b401\(k\)\b",
    r"\b401k\b",
    r"\bequity\b",
    r"\bremote\b",
    r"\bflexible\s+hours\b",
    r"\bvacation\b",
    r"\bhealth\s+insurance\b",
    r"\bwellness\b",
    r"\bpension\b",
    r"\bleave\b",
    r"\bpto\b",
    r"\bpaid\s+time\s+off\b",
    r"\bgym\b",
    r"\bper\s+annum\b",
    r"\bstipend\b",
]

_KEYWORD_MAP = {
    SectionType.RESPONSIBILITIES: [
        re.compile(p, re.I) for p in _RESPONSIBILITIES_KEYWORDS
    ],
    SectionType.REQUIREMENTS: [re.compile(p, re.I) for p in _REQUIREMENTS_KEYWORDS],
    SectionType.NICE_TO_HAVE: [re.compile(p, re.I) for p in _NICE_TO_HAVE_KEYWORDS],
    SectionType.ABOUT_COMPANY: [re.compile(p, re.I) for p in _ABOUT_COMPANY_KEYWORDS],
    SectionType.BENEFITS: [re.compile(p, re.I) for p in _BENEFITS_KEYWORDS],
}


class SectionClassifier:
    """Classifies job description sections using heading type and content heuristics."""

    def classify(
        self,
        heading: str | None,
        lines: list[str],
        detected_type: SectionType | None = None,
        heading_confidence: float = 0.0,
    ) -> tuple[SectionType, float]:
        """Classify a section based on heading information and content.

        Args:
            heading: The heading text of the section (if any).
            lines: The content lines of the section.
            detected_type: Pre-detected SectionType from the heading (if any).
            heading_confidence: Confidence from the heading detector.

        Returns:
            A tuple of (SectionType, confidence) where confidence is in [0.0, 1.0].
        """
        # 1. High-confidence heading match (exact or strong fuzzy)
        if detected_type is not None and heading_confidence >= 0.7:
            # We can trust the heading classifier's decision
            return detected_type, heading_confidence

        # Combine lines to analyze content
        content_text = "\n".join(lines)

        # 2. Content-based keyword scoring
        scores = dict.fromkeys(_KEYWORD_MAP, 0)
        for sec_type, patterns in _KEYWORD_MAP.items():
            for pattern in patterns:
                matches = pattern.findall(content_text)
                scores[sec_type] += len(matches)

        # Find the highest scoring type
        best_type = SectionType.OTHER
        best_score = 0
        for sec_type, score in scores.items():
            if score > best_score:
                best_score = score
                best_type = sec_type

        # If we have keyword signals, return them with content heuristic confidence
        if best_score > 0:
            # Map score intensity to confidence range [0.3, 0.69]
            confidence = min(0.3 + (best_score * 0.05), 0.69)
            # If the heading detector gave a weak heuristic, we can use it to boost confidence if they agree
            if detected_type == best_type:
                confidence = min(confidence + 0.1, 0.69)
            return best_type, round(confidence, 2)

        # 3. Weak heading fallback if no content signals override it
        if detected_type is not None:
            # e.g., heuristic heading (confidence 0.5) but no content keywords
            return detected_type, heading_confidence

        # 4. Fallback to OTHER with low confidence
        return SectionType.OTHER, 0.2
