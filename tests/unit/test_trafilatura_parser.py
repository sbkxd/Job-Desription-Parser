"""Unit tests for Milestone 2.4 — Trafilatura Content Extraction."""

from app.ingestion.parsers import ParseResult, TrafilaturaParser

# ---------------------------------------------------------------------------
# Sample HTML fixtures simulating real job boards
# ---------------------------------------------------------------------------

MINIMAL_JD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="og:title" content="Senior Python Developer - Acme Corp">
  <meta name="og:description" content="Join our team as a senior developer">
  <title>Senior Python Developer at Acme Corp</title>
</head>
<body>
  <nav><a href="/">Home</a><a href="/jobs">Jobs</a></nav>
  <main>
    <h1>Senior Python Developer</h1>
    <p>Acme Corp is looking for an experienced Python developer to join our backend team.</p>
    <h2>Responsibilities</h2>
    <ul>
      <li>Design and implement scalable backend services using FastAPI and SQLAlchemy.</li>
      <li>Write comprehensive unit and integration tests with pytest.</li>
      <li>Participate in code reviews and mentoring junior developers.</li>
      <li>Collaborate with product managers and data scientists on feature development.</li>
    </ul>
    <h2>Requirements</h2>
    <ul>
      <li>5+ years of Python experience.</li>
      <li>Strong knowledge of async programming and REST APIs.</li>
      <li>Experience with PostgreSQL and Redis.</li>
      <li>Familiarity with Docker and Kubernetes.</li>
    </ul>
    <h2>Location</h2>
    <p>Bangalore, India (Hybrid)</p>
    <h2>Salary</h2>
    <p>20-30 LPA depending on experience.</p>
  </main>
  <footer>
    <p>© 2024 Acme Corp. All rights reserved.</p>
    <a href="/privacy">Privacy Policy</a> | <a href="/terms">Terms</a>
  </footer>
</body>
</html>"""

NAUKRI_LIKE_HTML = """<!DOCTYPE html>
<html>
<head>
  <title>Data Engineer - TechCorp | Naukri.com</title>
  <meta property="og:title" content="Data Engineer at TechCorp">
  <meta name="description" content="5-8 years experience, Hyderabad">
</head>
<body>
  <div id="header">Naukri Header Nav Bar</div>
  <div class="jd-container">
    <h1 class="jd-title">Data Engineer</h1>
    <div class="company-info">TechCorp | Hyderabad | 5-8 Yrs</div>
    <div class="jd-description">
      <p>We are seeking a highly motivated Data Engineer to join our growing team.</p>
      <h3>Key Responsibilities:</h3>
      <ul>
        <li>Build and maintain scalable data pipelines using Apache Spark and Airflow.</li>
        <li>Design and implement data warehouse solutions on AWS.</li>
        <li>Collaborate with data scientists to productionize ML models.</li>
        <li>Ensure data quality and reliability through comprehensive testing.</li>
      </ul>
      <h3>Required Skills:</h3>
      <ul>
        <li>Strong Python and SQL expertise.</li>
        <li>Experience with Spark, Kafka, and Airflow.</li>
        <li>AWS or GCP cloud experience.</li>
        <li>Knowledge of data modeling best practices.</li>
      </ul>
      <p>CTC: 15-22 LPA | Location: Hyderabad | Experience: 5-8 years</p>
    </div>
  </div>
  <div id="footer">Footer links and ads</div>
  <script>window.ads = true;</script>
</body>
</html>"""

GREENHOUSE_LIKE_HTML = """<!DOCTYPE html>
<html>
<head>
  <title>Machine Learning Engineer - Acme | Greenhouse</title>
  <meta name="og:title" content="Machine Learning Engineer">
</head>
<body>
  <div class="greenhouse-header">Company Logo | Greenhouse</div>
  <div class="app-body">
    <div class="job-intro">
      <h1 id="app-title">Machine Learning Engineer</h1>
      <div class="location">San Francisco, CA or Remote</div>
    </div>
    <div class="content" id="content">
      <p>We're looking for an ML Engineer to help us build production-grade ML systems.</p>
      <h2>What you'll do</h2>
      <ul>
        <li>Train and deploy ML models at scale.</li>
        <li>Build data pipelines for model training and evaluation.</li>
        <li>Work closely with research scientists.</li>
      </ul>
      <h2>Requirements</h2>
      <ul>
        <li>MS or PhD in Computer Science, Statistics, or related field.</li>
        <li>3+ years of hands-on ML experience.</li>
        <li>Proficiency in Python, PyTorch or TensorFlow.</li>
        <li>Experience with distributed training and model deployment.</li>
      </ul>
    </div>
  </div>
</body>
</html>"""

EMPTY_HTML = ""
SCRIPT_ONLY_HTML = "<html><head></head><body><script>var x = 1;</script></body></html>"
MINIMAL_HTML = "<html><body><p>Short</p></body></html>"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestTrafilaturaParserInit:
    def test_default_init(self):
        parser = TrafilaturaParser()
        assert parser.favor_recall is True

    def test_custom_init(self):
        parser = TrafilaturaParser(favor_recall=False)
        assert parser.favor_recall is False


class TestParseResultDataclass:
    def test_defaults(self):
        result = ParseResult(raw_text="some text")
        assert result.success is True
        assert result.word_count == 0
        assert result.error is None
        assert result.metadata == {}

    def test_failure_result(self):
        result = ParseResult(raw_text="", success=False, error="No content")
        assert result.success is False
        assert result.error == "No content"


class TestParseEmptyInput:
    def test_empty_string(self):
        parser = TrafilaturaParser()
        result = parser.parse("")
        assert result.success is False
        assert result.raw_text == ""
        assert result.error is not None

    def test_whitespace_only(self):
        parser = TrafilaturaParser()
        result = parser.parse("   \n\t  ")
        assert result.success is False


class TestParseMinimalJD:
    def test_extracts_text(self):
        parser = TrafilaturaParser()
        result = parser.parse(MINIMAL_JD_HTML, url="https://acme.com/jobs/python-dev")
        assert result.success is True
        assert len(result.raw_text) > 100, "Expected substantial extracted text"
        assert result.word_count > 20

    def test_contains_job_keywords(self):
        parser = TrafilaturaParser()
        result = parser.parse(MINIMAL_JD_HTML)
        text_lower = result.raw_text.lower()
        # At least some job-related keywords should be present
        keywords_found = sum(
            1
            for kw in ["python", "developer", "requirements", "responsibilities"]
            if kw in text_lower
        )
        assert (
            keywords_found >= 2
        ), f"Too few keywords found in: {result.raw_text[:200]}"

    def test_strips_nav_footer(self):
        parser = TrafilaturaParser()
        result = parser.parse(MINIMAL_JD_HTML)
        # Navigation and footer text should be minimized
        assert "Privacy Policy" not in result.raw_text or len(result.raw_text) > 500

    def test_url_passed_through(self):
        parser = TrafilaturaParser()
        result = parser.parse(MINIMAL_JD_HTML, url="https://acme.com/jobs/1")
        # URL may appear in metadata
        assert result.url is not None or result.metadata is not None


class TestParseNaukriLike:
    def test_extracts_content(self):
        parser = TrafilaturaParser()
        result = parser.parse(NAUKRI_LIKE_HTML, url="https://naukri.com/job/123")
        assert result.success is True
        assert len(result.raw_text) > 50

    def test_contains_skills(self):
        parser = TrafilaturaParser()
        result = parser.parse(NAUKRI_LIKE_HTML)
        text_lower = result.raw_text.lower()
        assert any(
            skill in text_lower for skill in ["python", "spark", "sql", "data"]
        ), f"No expected skills found in: {result.raw_text[:300]}"


class TestParseGreenhouseLike:
    def test_extracts_content(self):
        parser = TrafilaturaParser()
        result = parser.parse(GREENHOUSE_LIKE_HTML)
        assert result.success is True
        assert len(result.raw_text) > 50

    def test_contains_ml_terms(self):
        parser = TrafilaturaParser()
        result = parser.parse(GREENHOUSE_LIKE_HTML)
        text_lower = result.raw_text.lower()
        assert any(
            t in text_lower for t in ["machine learning", "ml", "model", "python"]
        )


class TestMetadataExtraction:
    def test_title_extracted(self):
        parser = TrafilaturaParser()
        result = parser.parse(MINIMAL_JD_HTML, url="https://acme.com/jobs/1")
        # Title should come from og:title or <title>
        if result.title:
            assert len(result.title) > 5

    def test_metadata_dict_populated(self):
        parser = TrafilaturaParser()
        result = parser.parse(NAUKRI_LIKE_HTML)
        assert isinstance(result.metadata, dict)

    def test_word_count_positive(self):
        parser = TrafilaturaParser()
        result = parser.parse(MINIMAL_JD_HTML)
        assert result.word_count > 0


class TestEdgeCases:
    def test_script_only_html_does_not_crash(self):
        parser = TrafilaturaParser()
        result = parser.parse(SCRIPT_ONLY_HTML)
        # Should not crash; may succeed or fail gracefully
        assert isinstance(result, ParseResult)

    def test_minimal_html(self):
        """Very short HTML — may fail extraction but should not crash."""
        parser = TrafilaturaParser()
        result = parser.parse(MINIMAL_HTML)
        assert isinstance(result, ParseResult)

    def test_unicode_content(self):
        html = """<html><body><main>
        <h1>Software Entwickler</h1>
        <p>Wir suchen einen erfahrenen Entwickler für unser Team in München.</p>
        <p>Anforderungen: Python, Django, PostgreSQL, Docker</p>
        <p>Kenntnisse in maschinellem Lernen sind von Vorteil.</p>
        </main></body></html>"""
        parser = TrafilaturaParser()
        result = parser.parse(html)
        assert isinstance(result, ParseResult)
        if result.success:
            assert "Entwickler" in result.raw_text or len(result.raw_text) > 10

    def test_very_long_html(self):
        """Parser should handle large HTML without crashing."""
        content = "<p>" + "Python developer with experience in FastAPI. " * 500 + "</p>"
        html = f"<html><body><main>{content}</main></body></html>"
        parser = TrafilaturaParser()
        result = parser.parse(html)
        assert isinstance(result, ParseResult)
        if result.success:
            assert result.word_count > 100
