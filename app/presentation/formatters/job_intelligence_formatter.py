"""Presentation formatter transforming raw PipelineState dicts into structured JobIntelligenceReport."""

import re
from typing import Any, Dict, List, Set

from app.presentation.schemas.job_intelligence import (
    JobInformation,
    JobIntelligenceReport,
    ReviewSummary,
    RoleProfile,
    Skills,
)


class JobIntelligenceFormatter:
    """Formatter to clean, normalize, and restructure internal pipeline state into reports."""

    # Keywords to detect education requirements
    _EDUCATION_KEYWORDS = re.compile(
        r"\b(degree|bachelor|master|phd|doctorate|bs/ms|b\.s\.|m\.s\.|university|education|academic|diploma)\b",
        re.IGNORECASE,
    )

    # Keywords to filter out boilerplate from responsibilities
    _BOILERPLATE_KEYWORDS = re.compile(
        r"\b(equal opportunity|accommodation|diversity|disability|visa|background check|recruiter|disclaimer|privacy policy|equal employer|affirmative action|lawful work|veteran|gender identity|sexual orientation)\b",
        re.IGNORECASE,
    )

    @classmethod
    def format(cls, state: Dict[str, Any]) -> JobIntelligenceReport:
        """Process PipelineState and return the standardized JobIntelligenceReport."""
        job_source = state.get("job_source") or {}
        segmented_doc = state.get("segmented_document") or {}
        extraction_result = state.get("extraction_result") or {}
        normalization_result = state.get("normalization_result") or {}
        review_result = state.get("review_result") or {}

        job_info = cls._build_job_info(job_source)
        role_profile = cls._build_role_profile(extraction_result)
        responsibilities = cls._build_responsibilities(segmented_doc)
        education, qualifications = cls._build_education_and_qualifications(
            segmented_doc, extraction_result
        )
        skills_obj, tech_stack = cls._build_skills_and_tech_stack(
            segmented_doc, extraction_result, normalization_result
        )
        review_summary = cls._build_review_summary(review_result)

        return JobIntelligenceReport(
            job_information=job_info,
            role_profile=role_profile,
            skills=skills_obj,
            education_requirements=education,
            responsibilities=responsibilities,
            qualifications=qualifications,
            technology_stack=tech_stack,
            review_summary=review_summary,
        )

    @classmethod
    def _build_job_info(cls, job_source: Dict[str, Any]) -> JobInformation:
        """Construct the JobInformation schema."""
        return JobInformation(
            job_title=job_source.get("title") or "Unknown Title",
            company=job_source.get("company") or "",
            location=job_source.get("location") or "",
            source_type=job_source.get("source_type") or "",
            source_url=job_source.get("url") or "",
        )

    @classmethod
    def _build_role_profile(cls, extraction_result: Dict[str, Any]) -> RoleProfile:
        """Construct the RoleProfile schema."""
        exp = extraction_result.get("experience") or {}
        return RoleProfile(
            seniority=extraction_result.get("seniority") or "",
            minimum_experience_years=exp.get("min_years"),
            maximum_experience_years=exp.get("max_years"),
        )

    @classmethod
    def _build_responsibilities(cls, segmented_doc: Dict[str, Any]) -> List[str]:
        """Construct responsibilities, removing boilerplate."""
        raw_resp_lines = segmented_doc.get("responsibilities") or []
        responsibilities: List[str] = []
        for line in raw_resp_lines:
            stripped = line.strip()
            if stripped and not cls._BOILERPLATE_KEYWORDS.search(stripped):
                responsibilities.append(stripped)
        return responsibilities

    @classmethod
    def _build_education_and_qualifications(
        cls, segmented_doc: Dict[str, Any], extraction_result: Dict[str, Any]
    ) -> tuple[List[str], List[str]]:
        """Construct education and qualifications lists."""
        raw_req_items = extraction_result.get("requirements") or []
        education_requirements: List[str] = []
        qualifications: List[str] = []

        if not raw_req_items:
            fallback_lines = (segmented_doc.get("requirements") or []) + (
                segmented_doc.get("nice_to_have") or []
            )
            for line in fallback_lines:
                stripped = line.strip()
                if not stripped:
                    continue
                if cls._EDUCATION_KEYWORDS.search(stripped):
                    education_requirements.append(stripped)
                else:
                    qualifications.append(stripped)
        else:
            for req in raw_req_items:
                text = req.get("text", "").strip()
                if not text:
                    continue
                if cls._EDUCATION_KEYWORDS.search(text):
                    education_requirements.append(text)
                else:
                    qualifications.append(text)

        return (
            cls._deduplicate_list(education_requirements),
            cls._deduplicate_list(qualifications),
        )

    @classmethod
    def _build_skills_and_tech_stack(
        cls,
        segmented_doc: Dict[str, Any],
        extraction_result: Dict[str, Any],
        normalization_result: Dict[str, Any],
    ) -> tuple[Skills, List[str]]:
        """Extract and categorize required/preferred/normalized skills and tech stack."""
        raw_req_items = extraction_result.get("requirements") or []
        norm_skills = normalization_result.get("skills") or []

        required_skills: Set[str] = set()
        preferred_skills: Set[str] = set()
        normalized_skills: Set[str] = set()
        technology_stack: Set[str] = set()

        nice_to_have_lines = [
            line.lower() for line in (segmented_doc.get("nice_to_have") or [])
        ]
        preferred_reqs = [
            req.get("text", "").lower()
            for req in raw_req_items
            if req.get("classification") in ("Preferred", "Optional")
        ]

        for s in norm_skills:
            raw_name = s.get("raw_skill", "")
            norm_name = s.get("normalized_skill", "")

            display_name = norm_name if norm_name else raw_name
            if not display_name:
                continue

            technology_stack.add(display_name)
            if norm_name:
                normalized_skills.add(norm_name)

            is_preferred = False
            for line in nice_to_have_lines:
                if raw_name.lower() in line or (
                    norm_name and norm_name.lower() in line
                ):
                    is_preferred = True
                    break

            if not is_preferred:
                for line in preferred_reqs:
                    if raw_name.lower() in line or (
                        norm_name and norm_name.lower() in line
                    ):
                        is_preferred = True
                        break

            if is_preferred:
                preferred_skills.add(display_name)
            else:
                required_skills.add(display_name)

        skills_obj = Skills(
            required=sorted(required_skills),
            preferred=sorted(preferred_skills),
            normalized=sorted(normalized_skills),
        )
        return skills_obj, sorted(technology_stack)

    @classmethod
    def _build_review_summary(cls, review_result: Dict[str, Any]) -> ReviewSummary:
        """Construct the ReviewSummary schema."""
        flagged_skills_raw = review_result.get("flagged_skills") or []
        flagged_skills_names: List[str] = []
        low_confidence_items: List[str] = []

        for fs in flagged_skills_raw:
            raw_s = fs.get("raw_skill")
            norm_s = fs.get("normalized_skill")
            conf = fs.get("confidence")
            reason = fs.get("reason")

            name = raw_s or norm_s
            if name:
                flagged_skills_names.append(name)
                low_confidence_items.append(
                    f"{name} (confidence: {conf}, reason: {reason})"
                )

        return ReviewSummary(
            review_required=review_result.get("needs_review", False),
            flagged_skills=flagged_skills_names,
            low_confidence_items=low_confidence_items,
        )

    @staticmethod
    def _deduplicate_list(lst: List[str]) -> List[str]:
        """Keep list ordered and remove duplicate values."""
        seen = set()
        result = []
        for x in lst:
            if x not in seen:
                seen.add(x)
                result.append(x)
        return result
