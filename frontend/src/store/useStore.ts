import { create } from 'zustand';
import {
  JobIntelligenceReport,
  ResumeIntelligenceReport,
  CompatibilityReport,
  ResumeOptimizationReport,
  PipelineProgress,
  PipelineStageStatus
} from '../types';

interface State {
  isAnalyzing: boolean;
  error: string | null;
  report: JobIntelligenceReport | null; // job report
  resumeReport: ResumeIntelligenceReport | null;
  compatibilityReport: CompatibilityReport | null;
  recommendationReport: ResumeOptimizationReport | null;
  progress: PipelineProgress[];
  activeStageIndex: number;
  activeTab: 'job' | 'resume' | 'compatibility' | 'recommendations' | 'analytics';

  // Actions
  startAnalysis: () => void;
  updateStage: (stageName: PipelineProgress['stage'], status: PipelineStageStatus, message?: string) => void;
  setReport: (report: JobIntelligenceReport) => void;
  setResumeReport: (resumeReport: ResumeIntelligenceReport) => void;
  setCompatibilityReport: (compatibilityReport: CompatibilityReport) => void;
  setRecommendationReport: (recommendationReport: ResumeOptimizationReport) => void;
  setActiveTab: (tab: 'job' | 'resume' | 'compatibility' | 'recommendations' | 'analytics') => void;
  setError: (error: string) => void;
  reset: () => void;
}

const initialProgress: PipelineProgress[] = [
  { stage: 'ingestion', status: 'idle', message: 'Ingesting Job & Resume documents...' },
  { stage: 'segmentation', status: 'idle', message: 'Structuring document layouts...' },
  { stage: 'extraction', status: 'idle', message: 'Extracting key attributes...' },
  { stage: 'normalization', status: 'idle', message: 'Mapping terms to taxonomy...' },
  { stage: 'compatibility', status: 'idle', message: 'Evaluating candidate compatibility...' },
  { stage: 'recommendations', status: 'idle', message: 'Generating advisory recommendations...' },
  { stage: 'report', status: 'idle', message: 'Compiling structured report...' },
];

export const useStore = create<State>((set, get) => ({
  isAnalyzing: false,
  error: null,
  report: null,
  resumeReport: null,
  compatibilityReport: null,
  recommendationReport: null,
  progress: initialProgress,
  activeStageIndex: -1,
  activeTab: 'compatibility',

  startAnalysis: () => set({
    isAnalyzing: true,
    error: null,
    report: null,
    resumeReport: null,
    compatibilityReport: null,
    recommendationReport: null,
    progress: initialProgress.map((p, idx) => ({
      ...p,
      status: idx === 0 ? 'processing' : 'idle'
    })),
    activeStageIndex: 0
  }),

  updateStage: (stageName, status, message) => set((state) => {
    const updatedProgress = state.progress.map((p) => {
      if (p.stage === stageName) {
        return { ...p, status, ...(message ? { message } : {}) };
      }
      return p;
    });

    const activeIndex = updatedProgress.findIndex((p) => p.status === 'processing');

    return {
      progress: updatedProgress,
      activeStageIndex: activeIndex !== -1 ? activeIndex : state.activeStageIndex
    };
  }),

  setReport: (report) => set({
    report,
  }),

  setResumeReport: (resumeReport) => set({
    resumeReport,
  }),

  setCompatibilityReport: (compatibilityReport) => set({
    compatibilityReport,
  }),

  setRecommendationReport: (recommendationReport) => set({
    isAnalyzing: false,
    recommendationReport,
    progress: get().progress.map(p => ({ ...p, status: 'success' })),
    activeStageIndex: 6
  }),

  setActiveTab: (activeTab) => set({ activeTab }),

  setError: (error) => set({
    isAnalyzing: false,
    error,
    progress: get().progress.map(p => {
      if (p.status === 'processing') return { ...p, status: 'failed', message: error };
      return p;
    })
  }),

  reset: () => set({
    isAnalyzing: false,
    error: null,
    report: null,
    resumeReport: null,
    compatibilityReport: null,
    recommendationReport: null,
    progress: initialProgress,
    activeStageIndex: -1,
    activeTab: 'compatibility'
  })
}));
