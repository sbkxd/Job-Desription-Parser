from app.preprocessing.cleaners.text_cleaner import TextCleaner


def test_text_cleaner_basics():
    cleaner = TextCleaner()
    assert cleaner.clean("") == ""
    assert cleaner.clean("   ") == ""


def test_line_endings():
    cleaner = TextCleaner()
    assert cleaner.clean("Line 1\r\nLine 2\rLine 3") == "Line 1\nLine 2\nLine 3"


def test_html_tags_and_entities():
    cleaner = TextCleaner()
    raw = "<div>Hello &amp; welcome <br/> to Altrosyn &nbsp; HR.</div>"
    # <br/> -> \n, <div>/</div> -> space/removed, &amp; -> &, &nbsp; -> space
    cleaned = cleaner.clean(raw)
    assert "Hello & welcome" in cleaned
    assert "to Altrosyn" in cleaned


def test_smart_characters():
    cleaner = TextCleaner()
    raw = "“Smart Quotes” and ‘single quotes’ — em dash – en dash"
    cleaned = cleaner.clean(raw)
    assert '"Smart Quotes"' in cleaned
    assert "'single quotes'" in cleaned
    assert " - em dash - en dash" in cleaned


def test_bullet_unification():
    cleaner = TextCleaner()
    # Unicode bullets
    assert cleaner.clean("• First item\n▪ Second item") == "- First item\n- Second item"
    # Dash bullets
    assert cleaner.clean("- First item\n– Second item") == "- First item\n- Second item"
    # Indentation preservation
    assert cleaner.clean("Line 1\n  • Nested") == "Line 1\n  - Nested"


def test_numbered_lists():
    # Preserve numbering
    cleaner = TextCleaner(preserve_numbering=True)
    assert (
        cleaner.clean("1. First item\n2) Second item\n(3) Third")
        == "1. First item\n2) Second item\n(3) Third"
    )

    # Strip numbering
    cleaner_strip = TextCleaner(preserve_numbering=False)
    assert cleaner_strip.clean("1. First item\n2) Second") == "- First item\n- Second"


def test_whitespace_and_blank_lines():
    cleaner = TextCleaner()
    assert cleaner.clean("Line 1  with   spaces") == "Line 1 with spaces"
    assert cleaner.clean("Line 1\n\n\n\nLine 2") == "Line 1\n\nLine 2"
