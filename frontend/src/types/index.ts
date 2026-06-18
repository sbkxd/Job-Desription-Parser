export interface JobInformation {
  job_title: string;
  company: string;
  location: string;
  source_type: string;
  source_url: string;
}

export interface RoleProfile {
  seniority: string;
  minimum_experience_years: number | null;
  maximum_experience_years: number | null;
}

export interface Skills {
  required: string[];
  preferred: string[];
  normalized: string[];
}

export interface ReviewSummary {
  review_required: boolean;
  flagged_skills: string[];
  low_confidence_items: string[];
}

export interface JobIntelligenceReport {
  job_information: JobInformation;
  role_profile: RoleProfile;
  skills: Skills;
  education_requirements: string[];
  responsibilities: string[];
  qualifications: string[];
  technology_stack: string[];
  review_summary: ReviewSummary;
}

// Resume Intelligence
export interface EducationEntry {
  degree: string | null;
  field_of_study: string | null;
  school: string | null;
  graduation_year: number | null;
}

export interface ExperienceEntry {
  job_title: string | null;
  company: string | null;
  start_date: string | null;
  end_date: string | null;
  description: string | null;
  years: number | null;
}

export interface ProjectEntry {
  project_title: string | null;
  description: string | null;
  technologies: string[];
}

export interface CandidateProfile {
  candidate_name: string | null;
  education: EducationEntry[];
  years_experience: number;
  certifications: string[];
  summary: string | null;
  achievements: string[];
  publications: string[];
}

export interface ResumeSkill {
  raw_skill: string;
  normalized_skill: string | null;
  confidence: number;
  esco_id: string | null;
}

export interface ResumeIntelligenceReport {
  candidate_profile: CandidateProfile;
  skills: ResumeSkill[];
  experience: ExperienceEntry[];
  projects: ProjectEntry[];
}

// Compatibility Engine
export interface SkillMatch {
  matched: string[];
  missing: string[];
  additional: string[];
}

export interface ExperienceMatch {
  required: number | null;
  candidate: number;
  gap: number;
}

export interface EducationMatch {
  required_degree: string | null;
  candidate_degrees: string[];
  matches: boolean;
}

export interface GapAnalysis {
  critical_gaps: string[];
  moderate_gaps: string[];
  minor_gaps: string[];
}

export interface StrengthAnalysis {
  strong_matches: string[];
}

export interface CompatibilityReport {
  compatibility_score: number;
  skill_match: SkillMatch;
  experience_match: ExperienceMatch;
  education_match: EducationMatch;
  gap_analysis: GapAnalysis;
  strength_analysis: StrengthAnalysis;
}

// Optimization & Recommendations
export interface ImprovementSuggestion {
  type: string;
  section: string;
  message: string;
}

export interface AtsRecommendation {
  keyword: string;
  coverage_status: string;
  recommendation: string;
}

export interface ResumeOptimizationReport {
  compatibility_score: number;
  matched_skills: string[];
  missing_skills: string[];
  critical_gaps: string[];
  strengths: string[];
  resume_improvements: ImprovementSuggestion[];
  ats_recommendations: AtsRecommendation[];
  application_readiness_score: number;
  application_readiness_recommendation: string;
  tailored_summary: string;
}

export type PipelineStageStatus = 'idle' | 'processing' | 'success' | 'failed';

export interface PipelineProgress {
  stage: 'ingestion' | 'segmentation' | 'extraction' | 'normalization' | 'compatibility' | 'recommendations' | 'report';
  status: PipelineStageStatus;
  message?: string;
}
