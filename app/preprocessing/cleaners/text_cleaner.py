"""Text cleaning pipeline for raw JD content.

Applies deterministic, order-preserving transformations to normalize
whitespace, unicode, HTML artifacts, bullets, and line breaks.
"""

import html
import re
import unicodedata

# ---------------------------------------------------------------------------
# Compile patterns once at module load for performance
# ---------------------------------------------------------------------------

# HTML tags and artifacts
_RE_HTML_TAG = re.compile(r"<[^>]{1,200}>")
_RE_HTML_ENTITY = re.compile(r"&[a-zA-Z]{2,8};|&#\d{1,6};|&#x[0-9a-fA-F]{1,6};")

# Whitespace variants
_RE_HORIZONTAL_WS = re.compile(r"[ \t\u00a0\u2002\u2003\u2009]+")
_RE_MULTIPLE_BLANK_LINES = re.compile(r"\n{3,}")

# Unicode bullets and dashes to unify
_BULLET_CHARS = frozenset("•·▪◦▸▷►▶❯❱‣⁃◆◇★✓✔✗✘➤➢➣➡→⇒" "∙○●□■▲△*")
_DASH_BULLETS = frozenset("-–—−")

# Smart quotes and typographic characters
_SMART_QUOTE_MAP: dict[str, str] = {
    "\u2018": "'",  # left single quote
    "\u2019": "'",  # right single quote / apostrophe
    "\u201a": "'",  # single low-9 quotation
    "\u201b": "'",  # single high-reversed-9
    "\u201c": '"',  # left double quote
    "\u201d": '"',  # right double quote
    "\u201e": '"',  # double low-9 quotation
    "\u2022": "-",  # bullet → dash prefix
    "\u2013": "-",  # en dash
    "\u2014": "-",  # em dash
    "\u2015": "-",  # horizontal bar
    "\u00b7": "-",  # middle dot
    "\u2212": "-",  # minus sign
}

# Numbered list pattern: "1. ", "1) ", "(1) "
_RE_NUMBERED_LIST = re.compile(r"^\s*(?:\(\d+\)|\d+[.):])\s+")

# Trailing punctuation after headings (handled in normalizer, not here)
# Residual HTML line-break tags
_RE_BR_TAG = re.compile(r"<br\s*/?>", re.IGNORECASE)
_RE_HR_TAG = re.compile(r"<hr\s*/?>", re.IGNORECASE)


class TextCleaner:
    """Deterministic text cleaner for raw JD content.

    All operations are:
    - Deterministic: same input → same output
    - Lossless: semantic content is preserved
    - Non-extracting: no NLP, no classification

    Usage::

        cleaner = TextCleaner()
        clean = cleaner.clean(raw_text)
    """

    def __init__(self, preserve_numbering: bool = True) -> None:
        """Args:
        preserve_numbering: When True, numbered list prefixes (1. 2. 3.)
            are kept intact. When False, they are stripped to leave only
            the bullet content.
        """
        self.preserve_numbering = preserve_numbering

    def clean(self, text: str) -> str:
        """Apply the full cleaning pipeline.

        Pipeline order:
        1. CRLF → LF
        2. HTML unescape
        3. Remove HTML tags (residual from trafilatura)
        4. Unicode normalization (NFC)
        5. Smart quote/dash substitution
        6. Bullet unification → '- ' prefix
        7. Horizontal whitespace collapse (within line)
        8. Strip trailing whitespace per line
        9. Collapse excessive blank lines (>2 → 2)

        Returns:
            Cleaned text with consistent bullet/whitespace/encoding.
        """
        if not text:
            return ""

        text = self._normalize_line_endings(text)
        text = self._unescape_html(text)
        text = self._remove_html_tags(text)
        text = self._normalize_unicode(text)
        text = self._replace_smart_chars(text)
        lines = text.splitlines()
        lines = [self._unify_bullets(line) for line in lines]
        lines = [self._collapse_horizontal_whitespace(line) for line in lines]
        lines = [line.rstrip() for line in lines]
        text = "\n".join(lines)
        text = self._collapse_blank_lines(text)
        return text.strip()

    # ------------------------------------------------------------------
    # Individual cleaning steps
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_line_endings(text: str) -> str:
        """Replace CRLF and bare CR with LF."""
        return text.replace("\r\n", "\n").replace("\r", "\n")

    @staticmethod
    def _unescape_html(text: str) -> str:
        """Decode HTML entities like &amp; &lt; &nbsp; &#160;."""
        text = _RE_BR_TAG.sub("\n", text)
        text = _RE_HR_TAG.sub("\n", text)
        return html.unescape(text)

    @staticmethod
    def _remove_html_tags(text: str) -> str:
        """Strip residual HTML tags left by trafilatura edge cases."""
        return _RE_HTML_TAG.sub(" ", text)

    @staticmethod
    def _normalize_unicode(text: str) -> str:
        """Apply NFC normalization so decomposed glyphs become composed."""
        return unicodedata.normalize("NFC", text)

    @staticmethod
    def _replace_smart_chars(text: str) -> str:
        """Replace typographic characters with their ASCII equivalents."""
        for char, replacement in _SMART_QUOTE_MAP.items():
            text = text.replace(char, replacement)
        return text

    def _unify_bullets(self, line: str) -> str:
        """Normalize diverse bullet characters to a consistent '- ' prefix.

        Handles:
        - Unicode bullet chars (•, ·, ▪, ◦, etc.)
        - Dash bullets (-, –, —) in bullet position
        - Numbered list items (1. item) optionally stripped

        Result: each bullet line starts with '- ' followed by content.
        """
        stripped = line.lstrip()
        leading_spaces = len(line) - len(stripped)
        indent = " " * leading_spaces

        if not stripped:
            return line

        # Check if line starts with a known bullet character
        first_char = stripped[0]
        if first_char in _BULLET_CHARS:
            content = stripped[1:].lstrip()
            return f"{indent}- {content}"

        # Dash bullets: only treat as bullet if followed by whitespace
        if first_char in _DASH_BULLETS and len(stripped) > 1 and stripped[1] in " \t":
            content = stripped[1:].lstrip()
            return f"{indent}- {content}"

        # Numbered list items
        m = _RE_NUMBERED_LIST.match(stripped)
        if m:
            if not self.preserve_numbering:
                content = stripped[m.end() :]
                return f"{indent}- {content}"
            # Keep but normalize spacing
            content = stripped[m.end() :]
            number = stripped[: m.end()].strip()
            return f"{indent}{number} {content}"

        return line

    @staticmethod
    def _collapse_horizontal_whitespace(line: str) -> str:
        """Collapse runs of horizontal whitespace to a single space, preserving indentation."""
        stripped = line.lstrip()
        leading_spaces = len(line) - len(stripped)
        indent = line[:leading_spaces]
        collapsed_content = _RE_HORIZONTAL_WS.sub(" ", stripped)
        return indent + collapsed_content

    @staticmethod
    def _collapse_blank_lines(text: str) -> str:
        """Reduce sequences of 3+ blank lines to exactly 2."""
        return _RE_MULTIPLE_BLANK_LINES.sub("\n\n", text)
