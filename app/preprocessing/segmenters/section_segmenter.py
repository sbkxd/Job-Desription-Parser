"""Rule-based section segmenter.

Splits a list of clean text lines into raw sections at heading boundaries.
Preserves content order, paragraph grouping, and bullet hierarchy.
"""

from dataclasses import dataclass, field

from app.preprocessing.schemas.schemas import SectionType
from app.preprocessing.segmenters.heading_detector import HeadingDetector


@dataclass
class RawSection:
    """An unstyled section block before final classification."""

    heading: str | None
    detected_type: SectionType | None
    confidence: float
    lines: list[str] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return not any(ln.strip() for ln in self.lines)


class SectionSegmenter:
    """Splits cleaned JD text lines into ordered RawSection blocks.

    Algorithm:
    1. Iterate lines in order.
    2. When a heading line is detected → close the current section and
       open a new one with the heading's detected type and confidence.
    3. Non-heading lines are appended to the current section's content.
    4. If no heading is ever found → all content goes into a single
       section with type=OTHER and confidence=1.0.

    Usage::

        segmenter = SectionSegmenter()
        sections = segmenter.segment(lines)
    """

    def __init__(self) -> None:
        self._detector = HeadingDetector()

    def segment(self, lines: list[str]) -> list[RawSection]:
        """Segment lines into ordered RawSection objects.

        Args:
            lines: Cleaned, normalized text lines (one per element).

        Returns:
            List of RawSection objects in document order.
            Empty sections (no content lines) are dropped.
        """
        sections: list[RawSection] = []
        current: RawSection | None = None

        for line in lines:
            if self._detector.is_heading(line):
                detected_type, confidence = self._detector.classify_heading(line)

                # Close previous section
                if current is not None and not current.is_empty:
                    sections.append(current)

                current = RawSection(
                    heading=line.strip(),
                    detected_type=detected_type,
                    confidence=confidence,
                )
            else:
                if current is None:
                    # Content before any heading → implicit preamble section
                    current = RawSection(
                        heading=None,
                        detected_type=SectionType.OTHER,
                        confidence=0.5,
                    )
                current.lines.append(line)

        # Close final section
        if current is not None and not current.is_empty:
            sections.append(current)

        # If nothing was segmented at all, return a single OTHER block
        if not sections:
            all_text = "\n".join(lines)
            if all_text.strip():
                sections.append(
                    RawSection(
                        heading=None,
                        detected_type=SectionType.OTHER,
                        confidence=1.0,
                        lines=lines,
                    )
                )

        return sections
