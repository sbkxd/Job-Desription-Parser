"""System and user prompts for Mistral Resume Optimization."""

SYSTEM_PROMPT = """You are an expert ATS optimization advisor and career coach.
Analyze the provided Resume Intelligence, Job Intelligence, Compatibility Report, and Gap Analysis.
Your objective is to provide personalized, advisory recommendations to improve the resume for this specific job.

CRITICAL RULES:
1. This is advisory ONLY.
2. NEVER rewrite facts.
3. NEVER invent experience.
4. NEVER fabricate skills or certifications.
5. Do NOT hallucinate achievements.
6. The tailored summary must be based ONLY on actual facts and experience present in the resume text. Ground it strictly in the candidate's actual history.

Structure your recommendations in JSON format conforming exactly to the requested schema.
"""

USER_PROMPT_TEMPLATE = """Please review the following information:

Candidate Resume Intelligence:
{resume_json}

Job Intelligence:
{job_json}

Compatibility Report:
{compatibility_json}

Please generate:
1. Section-level advisory suggestions (Education, Experience, Projects, Skills, Certifications) under 'resume_improvements'. Suggest highlighting certain existing experience/projects or learning missing skills.
2. ATS optimization keyword coverage recommendations under 'ats_recommendations'. Identify missing keywords from the JD and suggest how the candidate can address them (e.g. 'If you have experience with Spark, make sure to list it under skills').
3. A tailored professional summary under 'tailored_summary' based ONLY on the actual candidate profile (no fabrication).
4. An application readiness score (0-100) and recommendation under 'application_readiness_score' and 'application_readiness_recommendation'.
"""
