'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useStore } from '../store/useStore';
import {
  Download,
  Layers,
  Cpu,
  MapPin,
  CheckSquare,
  FileCheck,
  Loader2,
  CheckCircle,
  AlertTriangle
} from 'lucide-react';

const stageMetadata = {
  ingestion: {
    label: 'Ingestion',
    description: 'Fetching source content',
    icon: Download,
    color: '#00E5FF',
  },
  segmentation: {
    label: 'Segmentation',
    description: 'Deconstructing sections',
    icon: Layers,
    color: '#8B5CF6',
  },
  extraction: {
    label: 'Extraction',
    description: 'NER skill tagging',
    icon: Cpu,
    color: '#3B82F6',
  },
  normalization: {
    label: 'Normalization',
    description: 'ESCO taxonomy alignment',
    icon: MapPin,
    color: '#F59E0B',
  },
  review: {
    label: 'Review Queue',
    description: 'AI confidence thresholding',
    icon: CheckSquare,
    color: '#EF4444',
  },
  report: {
    label: 'Intelligence Report',
    description: 'Compiling structural model',
    icon: FileCheck,
    color: '#10B981',
  },
};

export default function PipelineVisualizer() {
  const { isAnalyzing, progress, error, activeStageIndex } = useStore();

  if (!isAnalyzing && !error) return null;

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <div className="rounded-2xl border border-border-dark bg-[#111113]/40 glass-panel p-6 sm:p-8 space-y-8 relative overflow-hidden">
        {/* Header info */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-border-dark pb-4 gap-2">
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-text-secondary">Pipeline Telemetry</h3>
            <p className="text-2xs font-mono text-zinc-500">LangGraph Executor: state_graph_flow_v1</p>
          </div>
          {error ? (
            <div className="flex items-center space-x-1.5 text-xs text-error-bg font-semibold">
              <AlertTriangle className="h-4 w-4" />
              <span>Execution Fault Encountered</span>
            </div>
          ) : (
            <div className="flex items-center space-x-2 text-xs text-accent-primary font-mono">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Orchestrating agent workflows...</span>
            </div>
          )}
        </div>

        {/* Horizontal Pipeline Grid */}
        <div className="grid grid-cols-2 md:grid-cols-6 gap-6 relative">
          {progress.map((stageProg, index) => {
            const meta = stageMetadata[stageProg.stage];
            const IconComponent = meta.icon;

            const isIdle = stageProg.status === 'idle';
            const isProcessing = stageProg.status === 'processing';
            const isSuccess = stageProg.status === 'success';
            const isFailed = stageProg.status === 'failed';

            return (
              <div key={stageProg.stage} className="flex flex-col items-center text-center space-y-3 relative group">
                {/* Node bubble */}
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className={`flex h-12 w-12 items-center justify-center rounded-xl border transition-all duration-300 relative ${
                    isSuccess
                      ? 'border-success-bg bg-success-bg/10 text-success-bg shadow-lg shadow-success-bg/10'
                      : isProcessing
                      ? 'border-accent-primary bg-accent-primary/10 text-accent-primary shadow-lg shadow-accent-primary/20 animate-pulse'
                      : isFailed
                      ? 'border-error-bg bg-error-bg/10 text-error-bg shadow-lg shadow-error-bg/10'
                      : 'border-border-dark bg-background text-zinc-600'
                  }`}
                  style={{
                    borderColor: isProcessing ? meta.color : undefined,
                    boxShadow: isProcessing ? `0 0 15px ${meta.color}33` : undefined,
                  }}
                >
                  <IconComponent className="h-5 w-5" />

                  {/* Small Success Badge */}
                  {isSuccess && (
                    <span className="absolute -top-1 -right-1 flex h-4.5 w-4.5 items-center justify-center rounded-full bg-success-bg text-black">
                      <CheckCircle className="h-3 w-3 text-[#09090B] fill-current" />
                    </span>
                  )}
                </motion.div>

                {/* Info Text */}
                <div className="space-y-1">
                  <p className={`text-xs font-semibold ${isIdle ? 'text-zinc-600' : 'text-white'}`}>
                    {meta.label}
                  </p>
                  <p className="text-3xs text-zinc-500 leading-tight">
                    {meta.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Detailed Logs Box */}
        <div className="rounded-lg border border-border-dark bg-background/50 p-4 font-mono text-2xs space-y-2 max-h-40 overflow-y-auto">
          <p className="text-zinc-600">[{new Date().toLocaleTimeString()}] Initializing StateGraph engine...</p>
          {progress.map((stageProg, idx) => {
            if (stageProg.status === 'idle') return null;
            const meta = stageMetadata[stageProg.stage];
            return (
              <div key={idx} className="flex items-start space-x-2">
                <span className="text-zinc-600">[{new Date().toLocaleTimeString()}]</span>
                <span style={{ color: meta.color }}>[{meta.label.toUpperCase()}]</span>
                <span className={stageProg.status === 'success' ? 'text-success-bg' : stageProg.status === 'failed' ? 'text-error-bg' : 'text-zinc-300'}>
                  {stageProg.status === 'success' && `Successfully completed.`}
                  {stageProg.status === 'processing' && `${stageProg.message || 'Processing section content...'}`}
                  {stageProg.status === 'failed' && `Error: ${stageProg.message}`}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
