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

export type PipelineStageStatus = 'idle' | 'processing' | 'success' | 'failed';

export interface PipelineProgress {
  stage: 'ingestion' | 'segmentation' | 'extraction' | 'normalization' | 'review' | 'report';
  status: PipelineStageStatus;
  message?: string;
}
