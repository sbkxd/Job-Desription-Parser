"""MCP tool for persisting parsed job descriptions to the database."""

import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from sqlalchemy import select

from app.database.session import async_session_maker
from app.models.models import (
    Job,
    JobSkill,
    JobStatus,
    RequirementType,
    ReviewQueue,
    ReviewStatus,
    Skill,
)
from app.orchestration.mcp.base_tool import BaseMCPTool


class SkillMappingInput(BaseModel):
    """Pydantic model for individual skill details inside save_parsed_jd."""

    raw_skill: str = Field(..., description="The raw extracted skill string.")
    normalized_skill: Optional[str] = Field(
        default=None, description="The canonical skill string."
    )
    esco_id: Optional[str] = Field(default=None, description="The standard ESCO ID.")
    confidence: float = Field(default=1.0, description="Match confidence score.")


class SaveParsedJDInput(BaseModel):
    """Input parameters for the save_parsed_jd tool."""

    title: str = Field(..., description="The job title.")
    company: Optional[str] = Field(default=None, description="Company name.")
    location: Optional[str] = Field(default=None, description="Job location.")
    seniority: Optional[str] = Field(default=None, description="Target seniority.")
    url: Optional[str] = Field(default=None, description="Source URL of JD.")
    raw_text: str = Field(..., description="The raw text content.")
    skills: List[SkillMappingInput] = Field(
        default_factory=list, description="Extracted and normalized skills."
    )
    review_required: bool = Field(
        default=False, description="Flag indicating if human review is needed."
    )
    flagged_reasons: Optional[str] = Field(
        default=None, description="JSON string details of validation flags."
    )


class SaveParsedJDTool(BaseMCPTool):
    """MCP tool to save parsed job description attributes to the database."""

    name: str = "save_parsed_jd"
    description: str = (
        "Saves job attributes, skills mappings, and review items to the persistent database."
    )
    input_schema = SaveParsedJDInput

    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Save job description.

        Returns:
            Dict containing job_id and number of skills persisted.
        """
        title = kwargs["title"]
        raw_text = kwargs["raw_text"]
        company = kwargs.get("company")
        location = kwargs.get("location")
        seniority = kwargs.get("seniority")
        url = kwargs.get("url")
        skills = kwargs.get("skills")
        review_required = kwargs.get("review_required", False)
        flagged_reasons = kwargs.get("flagged_reasons")

        job_id = uuid.uuid4()
        skill_ids = []

        async with async_session_maker() as session:
            try:
                # 1. Create Job record
                job_status = (
                    JobStatus.REVIEW_REQUIRED
                    if review_required
                    else JobStatus.COMPLETED
                )
                job = Job(
                    id=job_id,
                    title=title,
                    company=company,
                    location=location,
                    seniority=seniority,
                    source_url=url,
                    raw_text=raw_text,
                    status=job_status,
                    review_required=review_required,
                )
                await session.merge(job)
                await session.flush()

                # 2. Persist Skills
                skills_list = skills or []
                for s in skills_list:
                    # Support both Pydantic models or dict inputs
                    raw_name = (
                        s.get("raw_skill") if isinstance(s, dict) else s.raw_skill
                    )
                    norm_name = (
                        s.get("normalized_skill")
                        if isinstance(s, dict)
                        else s.normalized_skill
                    )
                    esco_id = s.get("esco_id") if isinstance(s, dict) else s.esco_id
                    conf = (
                        s.get("confidence", 1.0)
                        if isinstance(s, dict)
                        else s.confidence
                    )

                    stmt = select(Skill).where(Skill.name.ilike(raw_name))
                    res = await session.execute(stmt)
                    skill_record = res.scalars().first()

                    if not skill_record:
                        skill_record = Skill(
                            id=uuid.uuid4(),
                            name=raw_name,
                            normalized_name=norm_name,
                            esco_code=esco_id,
                            category="Extracted Skill",
                        )
                        session.add(skill_record)
                        await session.flush()

                    skill_ids.append(str(skill_record.id))

                    # Create JobSkill link
                    job_skill = JobSkill(
                        id=uuid.uuid4(),
                        job_id=job_id,
                        skill_id=skill_record.id,
                        requirement_type=RequirementType.MUST_HAVE,
                        confidence_score=conf,
                    )
                    session.add(job_skill)

                # 3. Create ReviewQueue entry
                if review_required:
                    review_queue = ReviewQueue(
                        id=uuid.uuid4(),
                        job_id=job_id,
                        status=ReviewStatus.PENDING,
                        flagged_reasons=flagged_reasons,
                    )
                    session.add(review_queue)

                await session.commit()
            except Exception:
                await session.rollback()
                raise

        return {
            "job_id": str(job_id),
            "skills_persisted": len(skill_ids),
        }
