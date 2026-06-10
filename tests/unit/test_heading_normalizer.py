from app.preprocessing.normalizers.heading_normalizer import HeadingNormalizer
from app.preprocessing.schemas.schemas import SectionType


def test_heading_normalization():
    normalizer = HeadingNormalizer()

    # Normalization of surface forms
    assert normalizer.normalize_line("KEY RESPONSIBILITIES:") == "Key Responsibilities"
    assert normalizer.normalize_line("### About Us ###") == "About Us"
    assert normalizer.normalize_line("  requirements -- ") == "Requirements"

    # Normalize key (lowercase and stripped)
    assert (
        normalizer.normalize_key("  KEY RESPONSIBILITIES: ") == "key responsibilities"
    )


def test_alias_resolution():
    normalizer = HeadingNormalizer()

    assert normalizer.resolve("Key Responsibilities") == SectionType.RESPONSIBILITIES
    assert normalizer.resolve("what we are looking for") == SectionType.REQUIREMENTS
    assert normalizer.resolve("nice to have") == SectionType.NICE_TO_HAVE
    assert normalizer.resolve("about the company") == SectionType.ABOUT_COMPANY
    assert normalizer.resolve("perks and benefits") == SectionType.BENEFITS
    assert normalizer.resolve("unknown heading form") is None
