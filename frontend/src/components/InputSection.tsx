'use client';

import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link2, Upload, FileText, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { ApiService } from '../services/api';
import { useStore } from '../store/useStore';

export default function InputSection() {
  const [activeTab, setActiveTab] = useState<'url' | 'pdf'>('url');
  const [url, setUrl] = useState('');
  const [file, setFile] = useState<File | null>(null);

  // Progress & error states
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const { isAnalyzing, startAnalysis, setReport, setError, updateStage } = useStore();

  const handleUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) {
      setLocalError('Please paste a job description URL');
      return;
    }
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      setLocalError('URL must start with http:// or https://');
      return;
    }

    setLocalError(null);
    startAnalysis();
    simulatePipelineStages();

    try {
      const data = await ApiService.analyzeUrl(url);
      setReport(data);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Pipeline execution failed');
    }
  };

  const handleFileSubmit = async () => {
    if (!file) {
      setLocalError('Please select or drop a PDF file first');
      return;
    }

    setLocalError(null);
    startAnalysis();
    simulatePipelineStages();

    try {
      const data = await ApiService.analyzeFile(file);
      setReport(data);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Pipeline execution failed');
    }
  };

  // Helper to progress stages visually so the user has an animated dashboard experience
  const simulatePipelineStages = () => {
    const sequence: { stage: 'ingestion' | 'segmentation' | 'extraction' | 'normalization' | 'review' | 'report'; ms: number }[] = [
      { stage: 'ingestion', ms: 1500 },
      { stage: 'segmentation', ms: 2500 },
      { stage: 'extraction', ms: 4000 },
      { stage: 'normalization', ms: 5500 },
      { stage: 'review', ms: 7500 },
      { stage: 'report', ms: 9000 },
    ];

    sequence.forEach(({ stage, ms }) => {
      setTimeout(() => {
        const storeState = useStore.getState();
        // Only update to processing if we are still active and no error has occurred
        if (storeState.isAnalyzing && !storeState.error) {
          // Complete previous stages
          if (stage === 'segmentation') storeState.updateStage('ingestion', 'success');
          if (stage === 'extraction') storeState.updateStage('segmentation', 'success');
          if (stage === 'normalization') storeState.updateStage('extraction', 'success');
          if (stage === 'review') storeState.updateStage('normalization', 'success');
          if (stage === 'report') storeState.updateStage('review', 'success');

          storeState.updateStage(stage, 'processing');
        }
      }, ms);
    });
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      validateAndSetFile(selectedFile);
    }
  };

  const validateAndSetFile = (selectedFile: File) => {
    if (selectedFile.type !== 'application/pdf' && !selectedFile.name.toLowerCase().endsWith('.pdf')) {
      setLocalError('Only PDF files are supported.');
      setFile(null);
      return;
    }

    setLocalError(null);
    setFile(selectedFile);
    setIsUploading(true);
    setUploadProgress(0);

    // Simulate standard upload progress bar filling
    const interval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsUploading(false);
          return 100;
        }
        return prev + 10;
      });
    }, 100);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) {
      validateAndSetFile(droppedFile);
    }
  };

  const triggerFileSelect = () => {
    fileInputRef.current?.click();
  };

  return (
    <div id="analyze-section" className="mx-auto max-w-4xl px-4 py-12 scroll-mt-20">
      <div className="rounded-2xl border border-border-dark bg-[#111113]/60 glass-panel p-6 sm:p-8 shadow-2xl">
        {/* Tab Headers */}
        <div className="flex border-b border-border-dark mb-6">
          <button
            onClick={() => {
              if (isAnalyzing) return;
              setActiveTab('url');
              setLocalError(null);
            }}
            className={`flex items-center space-x-2 border-b-2 px-4 py-3 text-sm font-semibold transition-all duration-300 cursor-pointer ${
              activeTab === 'url'
                ? 'border-accent-primary text-accent-primary'
                : 'border-transparent text-text-secondary hover:text-zinc-300'
            } ${isAnalyzing ? 'opacity-50 cursor-not-allowed' : ''}`}
            disabled={isAnalyzing}
          >
            <Link2 className="h-4 w-4" />
            <span>Job URL Analysis</span>
          </button>
          <button
            onClick={() => {
              if (isAnalyzing) return;
              setActiveTab('pdf');
              setLocalError(null);
            }}
            className={`flex items-center space-x-2 border-b-2 px-4 py-3 text-sm font-semibold transition-all duration-300 cursor-pointer ${
              activeTab === 'pdf'
                ? 'border-accent-primary text-accent-primary'
                : 'border-transparent text-text-secondary hover:text-zinc-300'
            } ${isAnalyzing ? 'opacity-50 cursor-not-allowed' : ''}`}
            disabled={isAnalyzing}
          >
            <Upload className="h-4 w-4" />
            <span>PDF Ingestion</span>
          </button>
        </div>

        {/* Tab Body */}
        <AnimatePresence mode="wait">
          {activeTab === 'url' ? (
            <motion.form
              key="url-form"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              onSubmit={handleUrlSubmit}
              className="space-y-4"
            >
              <div className="space-y-2">
                <label htmlFor="job-url" className="text-xs font-semibold uppercase tracking-wider text-text-secondary">
                  Job Description URL
                </label>
                <div className="relative">
                  <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                    <Link2 className="h-5 w-5 text-zinc-500" />
                  </div>
                  <input
                    type="text"
                    id="job-url"
                    className="block w-full rounded-lg border border-border-dark bg-background py-3.5 pl-10 pr-4 text-sm text-white placeholder-zinc-500 focus:border-accent-primary focus:outline-none focus:ring-1 focus:ring-accent-primary transition-all duration-200"
                    placeholder="https://careers.google.com/jobs/results/..."
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    disabled={isAnalyzing}
                  />
                </div>
              </div>

              {localError && (
                <div className="flex items-center space-x-2 rounded-lg border border-error-bg/25 bg-error-bg/5 p-3 text-xs text-error-bg">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  <span>{localError}</span>
                </div>
              )}

              <button
                type="submit"
                className={`flex w-full items-center justify-center space-x-2 rounded-lg bg-gradient-to-r from-accent-primary to-accent-secondary py-3.5 px-4 text-sm font-bold text-black shadow-lg shadow-accent-primary/20 hover:opacity-90 transition-all duration-300 cursor-pointer ${
                  isAnalyzing ? 'opacity-60 cursor-not-allowed' : ''
                }`}
                disabled={isAnalyzing}
              >
                {isAnalyzing ? (
                  <>
                    <RefreshCw className="h-4 w-4 animate-spin text-black" />
                    <span>Analyzing Job Description Pipeline...</span>
                  </>
                ) : (
                  <span>Analyze Job URL</span>
                )}
              </button>
            </motion.form>
          ) : (
            <motion.div
              key="pdf-form"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-4"
            >
              {/* Drag and drop zone */}
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={triggerFileSelect}
                className={`flex flex-col items-center justify-center rounded-xl border-2 border-dashed py-8 px-6 text-center cursor-pointer transition-all duration-300 ${
                  isDragOver
                    ? 'border-accent-primary bg-accent-primary/5'
                    : file
                    ? 'border-success-bg/40 bg-success-bg/2'
                    : 'border-border-dark bg-background/50 hover:border-zinc-700 hover:bg-[#151518]'
                } ${isAnalyzing ? 'opacity-60 cursor-not-allowed pointer-events-none' : ''}`}
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  className="hidden"
                  accept=".pdf"
                  disabled={isAnalyzing}
                />

                {file ? (
                  <div className="flex flex-col items-center space-y-3">
                    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-success-bg/10 text-success-bg">
                      <FileText className="h-6 w-6" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-white">{file.name}</p>
                      <p className="text-xs text-text-secondary">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                    <div className="flex items-center space-x-1.5 text-xs text-success-bg font-medium">
                      <CheckCircle className="h-3.5 w-3.5" />
                      <span>Ready for Analysis</span>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center space-y-3">
                    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-border-dark text-text-secondary">
                      <Upload className="h-6 w-6" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-white">Drag & drop your PDF here, or browse</p>
                      <p className="text-xs text-text-secondary">Supports only PDF formats up to 10MB</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Progress Indicator */}
              {isUploading && (
                <div className="space-y-1.5">
                  <div className="flex justify-between text-2xs font-mono text-text-secondary">
                    <span>Uploading local file...</span>
                    <span>{uploadProgress}%</span>
                  </div>
                  <div className="h-1.5 w-full rounded-full bg-border-dark overflow-hidden">
                    <div
                      className="h-full bg-accent-secondary transition-all duration-150"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                </div>
              )}

              {localError && (
                <div className="flex items-center space-x-2 rounded-lg border border-error-bg/25 bg-error-bg/5 p-3 text-xs text-error-bg">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  <span>{localError}</span>
                </div>
              )}

              <button
                type="button"
                onClick={handleFileSubmit}
                className={`flex w-full items-center justify-center space-x-2 rounded-lg bg-gradient-to-r from-accent-primary to-accent-secondary py-3.5 px-4 text-sm font-bold text-black shadow-lg shadow-accent-primary/20 hover:opacity-90 transition-all duration-300 cursor-pointer ${
                  isAnalyzing || isUploading || !file ? 'opacity-60 cursor-not-allowed' : ''
                }`}
                disabled={isAnalyzing || isUploading || !file}
              >
                {isAnalyzing ? (
                  <>
                    <RefreshCw className="h-4 w-4 animate-spin text-black" />
                    <span>Analyzing Job Description Pipeline...</span>
                  </>
                ) : (
                  <span>Analyze PDF Description</span>
                )}
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
