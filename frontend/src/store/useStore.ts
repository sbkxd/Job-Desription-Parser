import { create } from 'zustand';
import { JobIntelligenceReport, PipelineProgress, PipelineStageStatus } from '../types';

interface State {
  isAnalyzing: boolean;
  error: string | null;
  report: JobIntelligenceReport | null;
  progress: PipelineProgress[];
  activeStageIndex: number;

  // Actions
  startAnalysis: () => void;
  updateStage: (stageName: PipelineProgress['stage'], status: PipelineStageStatus, message?: string) => void;
  setReport: (report: JobIntelligenceReport) => void;
  setError: (error: string) => void;
  reset: () => void;
}

const initialProgress: PipelineProgress[] = [
  { stage: 'ingestion', status: 'idle', message: 'Retrieving job description text...' },
  { stage: 'segmentation', status: 'idle', message: 'Structuring text sections...' },
  { stage: 'extraction', status: 'idle', message: 'Extracting key attributes...' },
  { stage: 'normalization', status: 'idle', message: 'Mapping to ESCO taxonomy...' },
  { stage: 'review', status: 'idle', message: 'Evaluating confidence thresholds...' },
  { stage: 'report', status: 'idle', message: 'Assembling intelligence report...' },
];

export const useStore = create<State>((set, get) => ({
  isAnalyzing: false,
  error: null,
  report: null,
  progress: initialProgress,
  activeStageIndex: -1,

  startAnalysis: () => set({
    isAnalyzing: true,
    error: null,
    report: null,
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
    isAnalyzing: false,
    report,
    progress: get().progress.map(p => ({ ...p, status: 'success' })),
    activeStageIndex: 5
  }),

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
    progress: initialProgress,
    activeStageIndex: -1
  })
}));
