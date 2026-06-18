"""Compatibility matching and scoring engine logic."""

from typing import List, Tuple

from app.compatibility.schemas.schemas import (
    CompatibilityReport,
    EducationMatch,
    ExperienceMatch,
    GapAnalysis,
    SkillMatch,
    StrengthAnalysis,
)
from app.presentation.schemas.job_intelligence import JobIntelligenceReport
from app.resume.schemas.schemas import ResumeIntelligenceReport


class CompatibilityEngine:
    """Computes resume compatibility against job description intelligence."""

    def analyze(
        self, resume: ResumeIntelligenceReport, job: JobIntelligenceReport
    ) -> CompatibilityReport:
        """Analyze and calculate compatibility between resume and job description.

        Args:
            resume: Structured resume intelligence report.
            job: Structured job description intelligence report.

        Returns:
            CompatibilityReport containing score, matching details, and gaps.
        """
        # 1. Skill Matching
        skill_match = self._match_skills(resume, job)

        # 2. Experience Matching
        exp_match = self._match_experience(resume, job)

        # 3. Education Matching
        edu_match = self._match_education(resume, job)

        # 4. Scoring (Weighted Compatibility Score)
        score, proj_score, cert_score = self._calculate_scores(
            resume, job, skill_match, exp_match, edu_match
        )

        # 5. Gap Analysis
        gaps = self._analyze_gaps(resume, job, skill_match, exp_match, edu_match)

        # 6. Strength Analysis
        strengths = self._analyze_strengths(
            resume, job, skill_match, exp_match, edu_match
        )

        return CompatibilityReport(
            compatibility_score=score,
            skill_match=skill_match,
            experience_match=exp_match,
            education_match=edu_match,
            gap_analysis=gaps,
            strength_analysis=strengths,
        )

    def _match_skills(
        self, resume: ResumeIntelligenceReport, job: JobIntelligenceReport
    ) -> SkillMatch:
        """Compare resume skills against required and preferred job skills."""
        # Standardize JD skills
        jd_required = {s.strip().lower() for s in job.skills.required if s}
        jd_preferred = {s.strip().lower() for s in job.skills.preferred if s}
        jd_all = jd_required.union(jd_preferred)

        # Candidate skills
        candidate_normalized = {
            s.normalized_skill.strip().lower()
            for s in resume.skills
            if s.normalized_skill
        }
        candidate_raw = {
            s.raw_skill.strip().lower() for s in resume.skills if s.raw_skill
        }
        {s.esco_id.strip().lower() for s in resume.skills if s.esco_id}
        candidate_all = candidate_normalized.union(candidate_raw)

        # Map matches
        matched_skills: List[str] = []
        missing_skills: List[str] = []
        additional_skills: List[str] = []

        # Check JD required/preferred
        for skill_list, _target_set in [
            (job.skills.required, jd_required),
            (job.skills.preferred, jd_preferred),
        ]:
            for s in skill_list:
                s_lower = s.strip().lower()
                # Match by raw name, normalized name, or substring
                is_matched = s_lower in candidate_all or any(
                    s_lower in cs or cs in s_lower for cs in candidate_all
                )
                if is_matched:
                    if s not in matched_skills:
                        matched_skills.append(s)
                else:
                    if s not in missing_skills:
                        missing_skills.append(s)

        # Additional skills in resume not in JD
        for skill in resume.skills:
            s_name = skill.normalized_skill or skill.raw_skill
            if not s_name:
                continue
            s_lower = s_name.strip().lower()
            is_in_jd = s_lower in jd_all or any(
                s_lower in js or js in s_lower for js in jd_all
            )
            if not is_in_jd:
                if s_name not in additional_skills:
                    additional_skills.append(s_name)

        return SkillMatch(
            matched=matched_skills,
            missing=missing_skills,
            additional=additional_skills,
        )

    def _match_experience(
        self, resume: ResumeIntelligenceReport, job: JobIntelligenceReport
    ) -> ExperienceMatch:
        """Compare candidate experience against job experience requirements."""
        required = job.role_profile.minimum_experience_years or 0.0
        candidate = resume.candidate_profile.years_experience
        gap = max(0.0, required - candidate)

        return ExperienceMatch(
            required=job.role_profile.minimum_experience_years,
            candidate=candidate,
            gap=round(gap, 2),
        )

    def _match_education(
        self, resume: ResumeIntelligenceReport, job: JobIntelligenceReport
    ) -> EducationMatch:
        """Compare candidate education against job requirements."""
        # 1. Parse required degree level from job description
        jd_edu_text = " ".join(job.education_requirements).lower()
        required_level = 0
        required_degree = None

        if "phd" in jd_edu_text or "ph.d" in jd_edu_text or "doctorate" in jd_edu_text:
            required_level = 4
            required_degree = "Ph.D."
        elif (
            "master" in jd_edu_text
            or "m.s" in jd_edu_text
            or "msc" in jd_edu_text
            or "mba" in jd_edu_text
        ):
            required_level = 3
            required_degree = "Master's Degree"
        elif (
            "bachelor" in jd_edu_text
            or "b.s" in jd_edu_text
            or "bsc" in jd_edu_text
            or "btech" in jd_edu_text
            or "degree" in jd_edu_text
        ):
            required_level = 2
            required_degree = "Bachelor's Degree"

        # 2. Parse candidate degrees
        candidate_degrees: List[str] = []
        candidate_max_level = 0

        for edu in resume.candidate_profile.education:
            deg_name = edu.degree or ""
            candidate_degrees.append(deg_name)
            deg_lower = deg_name.lower()

            if "phd" in deg_lower or "ph.d" in deg_lower or "doctor" in deg_lower:
                candidate_max_level = max(candidate_max_level, 4)
            elif (
                "master" in deg_lower
                or "m.s" in deg_lower
                or "msc" in deg_lower
                or "mba" in deg_lower
            ):
                candidate_max_level = max(candidate_max_level, 3)
            elif (
                "bachelor" in deg_lower
                or "b.s" in deg_lower
                or "bsc" in deg_lower
                or "btech" in deg_lower
                or "b.e" in deg_lower
            ):
                candidate_max_level = max(candidate_max_level, 2)
            else:
                candidate_max_level = max(candidate_max_level, 1)

        # If JD has no specific requirement, default is matched
        matches = True
        if required_level > 0:
            matches = candidate_max_level >= required_level

        return EducationMatch(
            required_degree=required_degree,
            candidate_degrees=candidate_degrees,
            matches=matches,
        )

    def _calculate_scores(
        self,
        resume: ResumeIntelligenceReport,
        job: JobIntelligenceReport,
        skills: SkillMatch,
        experience: ExperienceMatch,
        education: EducationMatch,
    ) -> Tuple[int, float, float]:
        """Compute the weighted compatibility score between 0 and 100."""
        skills_score = self._score_skills(job, skills)
        exp_score = self._score_experience(experience)
        edu_score = 100.0 if education.matches else 0.0
        proj_score = self._score_projects(resume, skills)
        cert_score = self._score_certifications(resume, job)

        # Weighted calculation
        total_score = (
            (skills_score * 0.50)
            + (exp_score * 0.25)
            + (edu_score * 0.10)
            + (proj_score * 0.10)
            + (cert_score * 0.05)
        )

        return int(round(total_score)), proj_score, cert_score

    def _score_skills(self, job: JobIntelligenceReport, skills: SkillMatch) -> float:
        """Calculate skill match score."""
        total_weight = 0.0
        earned_weight = 0.0

        for s in job.skills.required:
            total_weight += 1.0
            if s in skills.matched:
                earned_weight += 1.0

        for s in job.skills.preferred:
            total_weight += 0.5
            if s in skills.matched:
                earned_weight += 0.5

        return (earned_weight / total_weight * 100.0) if total_weight > 0 else 100.0

    def _score_experience(self, experience: ExperienceMatch) -> float:
        """Calculate experience match score."""
        req_years = experience.required or 0.0
        if req_years == 0:
            return 100.0
        return min(100.0, (experience.candidate / req_years) * 100.0)

    def _score_projects(
        self, resume: ResumeIntelligenceReport, skills: SkillMatch
    ) -> float:
        """Calculate projects match score."""
        techs_in_projects = set()
        for p in resume.projects:
            for tech in p.technologies:
                techs_in_projects.add(tech.lower())
            desc = p.description or ""
            for s in skills.matched:
                if s.lower() in desc.lower():
                    techs_in_projects.add(s.lower())

        matched_skills_lower = {s.lower() for s in skills.matched}
        overlap = matched_skills_lower.intersection(techs_in_projects)

        if len(resume.projects) == 0:
            return 0.0
        if len(overlap) > 0:
            return min(100.0, len(overlap) * 20.0)
        return 30.0

    def _score_certifications(
        self, resume: ResumeIntelligenceReport, job: JobIntelligenceReport
    ) -> float:
        """Calculate certifications match score."""
        if resume.candidate_profile.certifications:
            cert_score = 70.0
            qual_text = " ".join(job.qualifications).lower()
            for cert in resume.candidate_profile.certifications:
                if cert.lower() in qual_text:
                    cert_score = 100.0
                    break
            return cert_score
        if not job.qualifications:
            return 100.0
        return 0.0

    def _analyze_gaps(
        self,
        resume: ResumeIntelligenceReport,
        job: JobIntelligenceReport,
        skills: SkillMatch,
        experience: ExperienceMatch,
        education: EducationMatch,
    ) -> GapAnalysis:
        """Categorize critical, moderate, and minor gaps."""
        critical: List[str] = []
        moderate: List[str] = []
        minor: List[str] = []

        # Experience Gap
        if experience.gap >= 2.0:
            critical.append(
                f"Significant experience gap of {experience.gap} years (has {experience.candidate} yrs, requires {experience.required} yrs)."
            )
        elif experience.gap > 0.0:
            moderate.append(
                f"Minor experience gap of {experience.gap} years (has {experience.candidate} yrs, requires {experience.required} yrs)."
            )

        # Skill Gaps
        for ms in skills.missing:
            # Check if it's a required skill
            is_req = any(ms.lower() == r.lower() for r in job.skills.required)
            if is_req:
                critical.append(f"Missing critical required skill: {ms}")
            else:
                moderate.append(f"Missing preferred skill: {ms}")

        # Education Gap
        if not education.matches:
            moderate.append(
                f"Candidate level of education does not meet required degree: {education.required_degree}."
            )

        # Project / Tech Gaps
        if len(resume.projects) == 0:
            minor.append(
                "No projects listed in resume to demonstrate hands-on application."
            )

        # Certification gaps
        qual_text = " ".join(job.qualifications).lower()
        if "certif" in qual_text and not resume.candidate_profile.certifications:
            minor.append(
                "Missing potential certifications mentioned in qualifications."
            )

        return GapAnalysis(
            critical_gaps=critical,
            moderate_gaps=moderate,
            minor_gaps=minor,
        )

    def _analyze_strengths(
        self,
        resume: ResumeIntelligenceReport,
        job: JobIntelligenceReport,
        skills: SkillMatch,
        experience: ExperienceMatch,
        education: EducationMatch,
    ) -> StrengthAnalysis:
        """Identify key candidate strengths matching the job requirements."""
        strengths: List[str] = []

        # Skills match strength
        if len(skills.matched) >= 3:
            top_matches = ", ".join(skills.matched[:3])
            strengths.append(
                f"Strong skill alignment with match on core tools: {top_matches}."
            )

        # Experience strength
        req_exp = experience.required or 0.0
        if experience.candidate > req_exp and req_exp > 0:
            strengths.append(
                f"Candidate exceeds the required experience by {round(experience.candidate - req_exp, 1)} years."
            )
        elif experience.candidate >= req_exp and req_exp > 0:
            strengths.append("Candidate meets the required experience level.")

        # Education strength
        if education.matches and education.required_degree:
            strengths.append(
                f"Candidate meets or exceeds education requirement with {education.candidate_degrees[0] if education.candidate_degrees else 'matching degree'}."
            )

        # Projects strength
        matching_projects = []
        for p in resume.projects:
            desc = p.description or ""
            overlap = [s for s in skills.matched if s.lower() in desc.lower()]
            if overlap and p.project_title:
                matching_projects.append(p.project_title)
        if matching_projects:
            strengths.append(
                f"Demonstrates hands-on project experience in: {', '.join(matching_projects[:2])}."
            )

        # Certifications strength
        if resume.candidate_profile.certifications:
            strengths.append(
                f"Possesses key industry certifications: {', '.join(resume.candidate_profile.certifications[:2])}."
            )

        return StrengthAnalysis(strong_matches=strengths)
