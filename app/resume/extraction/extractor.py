"""Resume extraction using Mistral AI client."""

from app.logging.logger import get_logger
from app.orchestration.mistral.mistral_client import MistralClient
from app.resume.schemas.schemas import ResumeIntelligenceReport

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a professional Resume Parser agent.
Analyze the provided resume text and extract the candidate's structured profile data.

Follow these rules strictly:
1. Extract the candidate name accurately.
2. Segment and format the education history into the 'education' field under 'candidate_profile'.
3. Extract all work history items into the 'experience' field, calculating duration in years if possible.
4. Extract all listed projects into the 'projects' field.
5. Extract a list of all technical/non-technical skills mentioned in the resume and output them in the 'skills' list (populate the 'raw_skill' field for each). Do not normalize them yet; simply extract them as written.
6. Extract certifications, summary, achievements, and publications.
7. Return ONLY a valid JSON object matching the requested JSON SCHEMA TEMPLATE below. Do not fabricate or hallucinate any details. Only extract information present in the resume.

JSON SCHEMA TEMPLATE:
{
  "candidate_profile": {
    "candidate_name": "Full name of the candidate",
    "education": [
      {
        "degree": "Degree name (e.g. Bachelor of Science)",
        "field_of_study": "Field of study (e.g. Computer Science)",
        "school": "Name of the institution",
        "graduation_year": 2024
      }
    ],
    "years_experience": 2.5,
    "certifications": ["List of certifications"],
    "summary": "Professional summary or bio",
    "achievements": ["List of notable achievements"],
    "publications": ["List of publications"]
  },
  "skills": [
    {
      "raw_skill": "Name of the skill as written",
      "normalized_skill": null,
      "confidence": 0.0,
      "esco_id": null
    }
  ],
  "experience": [
    {
      "job_title": "Job title or role",
      "company": "Company name",
      "start_date": "Start date",
      "end_date": "End date or Present",
      "description": "Description of duties/responsibilities",
      "years": 1.5
    }
  ],
  "projects": [
    {
      "project_title": "Project title",
      "description": "Description of project scope and details",
      "technologies": ["Technologies used"]
    }
  ]
}

Ensure all fields conform EXACTLY to this nested structure. Do NOT output "profile" instead of "candidate_profile". Do NOT output nested dictionaries for "skills".
"""


class ResumeExtractor:
    """Uses Mistral LLM to extract structured sections and info from raw resume text."""

    def __init__(self, client: MistralClient | None = None) -> None:
        self.client = client or MistralClient()

    async def extract(self, text: str) -> ResumeIntelligenceReport:
        """Extract structured resume data from raw text using Mistral.

        Args:
            text: Raw resume text.

        Returns:
            Structured ResumeIntelligenceReport with raw skills extracted.
        """
        logger.info("Sending resume text to Mistral for structured extraction")

        prompt = f"Resume text to parse:\n\n{text}"

        try:
            report = await self.client.generate_structured(
                prompt=prompt,
                schema=ResumeIntelligenceReport,
                system_prompt=SYSTEM_PROMPT,
                prompt_version="resume_extraction_v1",
            )
            logger.info("Successfully extracted resume data using Mistral")
            return report
        except Exception as e:
            logger.error("Mistral resume extraction failed", error=str(e))
            raise RuntimeError(f"Error during resume extraction: {str(e)}") from e
