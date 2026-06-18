'use client';

import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link2, Upload, FileText, CheckCircle, AlertCircle, RefreshCw, Briefcase, FileUser, Play } from 'lucide-react';
import { ApiService } from '../services/api';
import { useStore } from '../store/useStore';
import { PipelineProgress } from '../types';

export default function InputSection() {
  // Wizard steps: 1 = Job Input, 2 = Resume Input, 3 = Ready to Analyze
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [jobInputType, setJobInputType] = useState<'url' | 'pdf'>('url');

  // Inputs
  const [jobUrl, setJobUrl] = useState('');
  const [jobFile, setJobFile] = useState<File | null>(null);
  const [resumeFile, setResumeFile] = useState<File | null>(null);

  // States
  const [jobUploadProgress, setJobUploadProgress] = useState(0);
  const [resumeUploadProgress, setResumeUploadProgress] = useState(0);
  const [isJobUploading, setIsJobUploading] = useState(false);
  const [isResumeUploading, setIsResumeUploading] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const [isDragOverJob, setIsDragOverJob] = useState(false);
  const [isDragOverResume, setIsDragOverResume] = useState(false);

  // Refs
  const jobFileInputRef = useRef<HTMLInputElement>(null);
  const resumeFileInputRef = useRef<HTMLInputElement>(null);

  const {
    isAnalyzing,
    startAnalysis,
    setReport,
    setResumeReport,
    setCompatibilityReport,
    setRecommendationReport,
    setError,
    updateStage
  } = useStore();

  const handleNextFromJob = () => {
    if (jobInputType === 'url') {
      if (!jobUrl) {
        setLocalError('Please paste a job description URL');
        return;
      }
      if (!jobUrl.startsWith('http://') && !jobUrl.startsWith('https://')) {
        setLocalError('URL must start with http:// or https://');
        return;
      }
    } else {
      if (!jobFile) {
        setLocalError('Please upload a Job Description PDF');
        return;
      }
    }
    setLocalError(null);
    setStep(2);
  };

  const handleNextFromResume = () => {
    if (!resumeFile) {
      setLocalError('Please upload your resume PDF');
      return;
    }
    setLocalError(null);
    setStep(3);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, type: 'job' | 'resume') => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      validateAndSetFile(selectedFile, type);
    }
  };

  const validateAndSetFile = (selectedFile: File, type: 'job' | 'resume') => {
    if (selectedFile.type !== 'application/pdf' && !selectedFile.name.toLowerCase().endsWith('.pdf')) {
      setLocalError('Only PDF files are supported.');
      return;
    }

    setLocalError(null);
    if (type === 'job') {
      setJobFile(selectedFile);
      setIsJobUploading(true);
      setJobUploadProgress(0);
      const interval = setInterval(() => {
        setJobUploadProgress((prev) => {
          if (prev >= 100) {
            clearInterval(interval);
            setIsJobUploading(false);
            return 100;
          }
          return prev + 20;
        });
      }, 100);
    } else {
      setResumeFile(selectedFile);
      setIsResumeUploading(true);
      setResumeUploadProgress(0);
      const interval = setInterval(() => {
        setResumeUploadProgress((prev) => {
          if (prev >= 100) {
            clearInterval(interval);
            setIsResumeUploading(false);
            return 100;
          }
          return prev + 20;
        });
      }, 100);
    }
  };

  const handleRunAnalysis = async () => {
    setLocalError(null);
    startAnalysis();
    simulatePipelineStages();

    try {
      // 1. Analyze Job
      let jobData;
      if (jobInputType === 'url') {
        updateStage('ingestion', 'processing', 'Fetching and parsing Job URL...');
        jobData = await ApiService.analyzeUrl(jobUrl);
      } else {
        updateStage('ingestion', 'processing', 'Uploading and parsing Job PDF...');
        jobData = await ApiService.analyzeFile(jobFile!);
      }
      setReport(jobData);
      updateStage('ingestion', 'success', 'Job Description parsed successfully.');

      // 2. Analyze Resume
      updateStage('segmentation', 'processing', 'Uploading and segmenting candidate Resume PDF...');
      const resumeData = await ApiService.analyzeResume(resumeFile!);
      setResumeReport(resumeData);
      updateStage('segmentation', 'success', 'Resume segmented successfully.');

      // 3. Extract & Normalize
      updateStage('extraction', 'processing', 'Extracting and normalising attributes...');
      // Resume and Job are parsed, now we run compatibility matching
      updateStage('normalization', 'processing', 'Evaluating database ESCO taxonomy mappings...');

      // 4. Compatibility match
      updateStage('compatibility', 'processing', 'Evaluating candidate job compatibility score...');
      const compatibilityData = await ApiService.analyzeCompatibility(resumeData, jobData);
      setCompatibilityReport(compatibilityData);
      updateStage('compatibility', 'success', 'Calculated weighted compatibility metrics.');

      // 5. Recommendations
      updateStage('recommendations', 'processing', 'Generating Mistral AI resume optimization suggestions...');
      const recommendationData = await ApiService.getRecommendations(resumeData, jobData);
      setRecommendationReport(recommendationData);

      updateStage('report', 'success', 'Application readiness report ready!');
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Pipeline analysis execution failed');
    }
  };

  const simulatePipelineStages = () => {
    const stages: { stage: PipelineProgress['stage']; ms: number; msg: string }[] = [
      { stage: 'ingestion', ms: 1000, msg: 'Ingesting Job Description...' },
      { stage: 'segmentation', ms: 2500, msg: 'Segmenting candidate Resume...' },
      { stage: 'extraction', ms: 4500, msg: 'Mining skills and experiences...' },
      { stage: 'normalization', ms: 6000, msg: 'Correlating with ESCO taxonomy...' },
      { stage: 'compatibility', ms: 8000, msg: 'Calculating score profiles...' },
      { stage: 'recommendations', ms: 10000, msg: 'Generating ATS keywords suggestions...' },
    ];

    stages.forEach(({ stage, ms, msg }) => {
      setTimeout(() => {
        const storeState = useStore.getState();
        if (storeState.isAnalyzing && !storeState.error) {
          storeState.updateStage(stage, 'processing', msg);
        }
      }, ms);
    });
  };

  return (
    <div id="analyze-section" className="mx-auto max-w-4xl px-4 py-8 scroll-mt-20">

      {/* Workflow Navigation Tracker */}
      <div className="flex justify-between items-center max-w-xl mx-auto mb-10 text-xs sm:text-sm font-semibold">
        <button
          onClick={() => !isAnalyzing && setStep(1)}
          className={`flex items-center space-x-1.5 cursor-pointer pb-2 border-b-2 transition-all ${
            step === 1 ? 'border-accent-primary text-accent-primary' : 'border-transparent text-zinc-500'
          }`}
          disabled={isAnalyzing}
          aria-label="Step 1: Job Description Input"
        >
          <Briefcase className="h-4 w-4" />
          <span>1. Job Description</span>
        </button>
        <div className="h-[2px] w-8 bg-zinc-800 -mt-2" />
        <button
          onClick={() => !isAnalyzing && jobUrl || jobFile ? setStep(2) : null}
          className={`flex items-center space-x-1.5 pb-2 border-b-2 transition-all ${
            step === 2 ? 'border-accent-primary text-accent-primary' : 'border-transparent text-zinc-500'
          } ${!jobUrl && !jobFile ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          disabled={isAnalyzing || (!jobUrl && !jobFile)}
          aria-label="Step 2: Resume Ingestion"
        >
          <FileUser className="h-4 w-4" />
          <span>2. Resume PDF</span>
        </button>
        <div className="h-[2px] w-8 bg-zinc-800 -mt-2" />
        <button
          onClick={() => !isAnalyzing && resumeFile ? setStep(3) : null}
          className={`flex items-center space-x-1.5 pb-2 border-b-2 transition-all ${
            step === 3 ? 'border-accent-primary text-accent-primary' : 'border-transparent text-zinc-500'
          } ${!resumeFile ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          disabled={isAnalyzing || !resumeFile}
          aria-label="Step 3: Run Analysis"
        >
          <Play className="h-4 w-4" />
          <span>3. Run Matcher</span>
        </button>
      </div>

      {/* Main Workflow Form Card */}
      <div className="rounded-2xl border border-border-dark bg-[#111113]/60 glass-panel p-6 sm:p-8 shadow-2xl relative">
        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.div
              key="step-1"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 10 }}
              className="space-y-6"
            >
              <div className="flex border-b border-border-dark mb-4">
                <button
                  onClick={() => setJobInputType('url')}
                  className={`flex items-center space-x-2 border-b-2 px-4 py-2 text-sm font-semibold transition-all duration-200 cursor-pointer ${
                    jobInputType === 'url' ? 'border-accent-primary text-accent-primary' : 'border-transparent text-zinc-500'
                  }`}
                  disabled={isAnalyzing}
                >
                  <Link2 className="h-4 w-4" />
                  <span>Job URL</span>
                </button>
                <button
                  onClick={() => setJobInputType('pdf')}
                  className={`flex items-center space-x-2 border-b-2 px-4 py-2 text-sm font-semibold transition-all duration-200 cursor-pointer ${
                    jobInputType === 'pdf' ? 'border-accent-primary text-accent-primary' : 'border-transparent text-zinc-500'
                  }`}
                  disabled={isAnalyzing}
                >
                  <Upload className="h-4 w-4" />
                  <span>Job PDF File</span>
                </button>
              </div>

              {jobInputType === 'url' ? (
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
                      value={jobUrl}
                      onChange={(e) => setJobUrl(e.target.value)}
                      disabled={isAnalyzing}
                    />
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div
                    onDragOver={(e) => { e.preventDefault(); setIsDragOverJob(true); }}
                    onDragLeave={() => setIsDragOverJob(false)}
                    onDrop={(e) => {
                      e.preventDefault();
                      setIsDragOverJob(false);
                      const file = e.dataTransfer.files?.[0];
                      if (file) validateAndSetFile(file, 'job');
                    }}
                    onClick={() => jobFileInputRef.current?.click()}
                    className={`flex flex-col items-center justify-center rounded-xl border-2 border-dashed py-8 px-6 text-center cursor-pointer transition-all ${
                      isDragOverJob ? 'border-accent-primary bg-accent-primary/5' : 'border-border-dark bg-background/50 hover:bg-[#151518]'
                    }`}
                  >
                    <input
                      type="file"
                      ref={jobFileInputRef}
                      onChange={(e) => handleFileChange(e, 'job')}
                      className="hidden"
                      accept=".pdf"
                    />
                    {jobFile ? (
                      <div className="flex flex-col items-center space-y-2">
                        <FileText className="h-10 w-10 text-success-bg" />
                        <p className="text-sm font-semibold text-white">{jobFile.name}</p>
                        <p className="text-2xs text-text-secondary">{(jobFile.size / 1024 / 1024).toFixed(2)} MB</p>
                      </div>
                    ) : (
                      <div className="flex flex-col items-center space-y-2">
                        <Upload className="h-10 w-10 text-zinc-500" />
                        <p className="text-sm text-white font-semibold">Drag & Drop Job PDF, or Browse</p>
                        <p className="text-xs text-text-secondary">PDF formats only up to 10MB</p>
                      </div>
                    )}
                  </div>
                  {isJobUploading && (
                    <div className="h-1 w-full bg-border-dark rounded overflow-hidden">
                      <div className="h-full bg-accent-primary transition-all" style={{ width: `${jobUploadProgress}%` }} />
                    </div>
                  )}
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
                onClick={handleNextFromJob}
                className="flex w-full items-center justify-center space-x-2 rounded-lg bg-gradient-to-r from-accent-primary to-accent-secondary py-3.5 px-4 text-sm font-bold text-black shadow-lg shadow-accent-primary/20 hover:opacity-90 transition-all cursor-pointer"
              >
                <span>Continue to Resume Upload</span>
              </button>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div
              key="step-2"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 10 }}
              className="space-y-6"
            >
              <div className="space-y-2">
                <span className="text-xs font-mono text-accent-secondary uppercase font-semibold">Step 2: Resume Ingestion</span>
                <h3 className="text-lg font-bold text-white">Upload Candidate Resume</h3>
                <p className="text-xs text-text-secondary">Provide candidate profile PDF for matching and recommendation intelligence.</p>
              </div>

              <div className="space-y-4">
                <div
                  onDragOver={(e) => { e.preventDefault(); setIsDragOverResume(true); }}
                  onDragLeave={() => setIsDragOverResume(false)}
                  onDrop={(e) => {
                    e.preventDefault();
                    setIsDragOverResume(false);
                    const file = e.dataTransfer.files?.[0];
                    if (file) validateAndSetFile(file, 'resume');
                  }}
                  onClick={() => resumeFileInputRef.current?.click()}
                  className={`flex flex-col items-center justify-center rounded-xl border-2 border-dashed py-8 px-6 text-center cursor-pointer transition-all ${
                    isDragOverResume ? 'border-accent-primary bg-accent-primary/5' : 'border-border-dark bg-background/50 hover:bg-[#151518]'
                  }`}
                >
                  <input
                    type="file"
                    ref={resumeFileInputRef}
                    onChange={(e) => handleFileChange(e, 'resume')}
                    className="hidden"
                    accept=".pdf"
                  />
                  {resumeFile ? (
                    <div className="flex flex-col items-center space-y-2">
                      <FileText className="h-10 w-10 text-success-bg" />
                      <p className="text-sm font-semibold text-white">{resumeFile.name}</p>
                      <p className="text-2xs text-text-secondary">{(resumeFile.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center space-y-2">
                      <Upload className="h-10 w-10 text-zinc-500" />
                      <p className="text-sm text-white font-semibold">Drag & Drop Resume PDF, or Browse</p>
                      <p className="text-xs text-text-secondary">PDF format only up to 10MB</p>
                    </div>
                  )}
                </div>
                {isResumeUploading && (
                  <div className="h-1 w-full bg-border-dark rounded overflow-hidden">
                    <div className="h-full bg-accent-secondary transition-all" style={{ width: `${resumeUploadProgress}%` }} />
                  </div>
                )}
              </div>

              {localError && (
                <div className="flex items-center space-x-2 rounded-lg border border-error-bg/25 bg-error-bg/5 p-3 text-xs text-error-bg">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  <span>{localError}</span>
                </div>
              )}

              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="flex-1 rounded-lg border border-border-dark bg-[#111113] py-3 px-4 text-sm font-semibold text-zinc-300 hover:text-white transition cursor-pointer"
                >
                  Back
                </button>
                <button
                  type="button"
                  onClick={handleNextFromResume}
                  className="flex-1 rounded-lg bg-gradient-to-r from-accent-primary to-accent-secondary py-3 px-4 text-sm font-bold text-black shadow-lg shadow-accent-primary/20 hover:opacity-90 transition cursor-pointer"
                >
                  Continue
                </button>
              </div>
            </motion.div>
          )}

          {step === 3 && (
            <motion.div
              key="step-3"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 10 }}
              className="space-y-6"
            >
              <div className="space-y-2">
                <span className="text-xs font-mono text-success-bg uppercase font-semibold">Step 3: Ready for Analysis</span>
                <h3 className="text-lg font-bold text-white">Run Compatibility Engine</h3>
                <p className="text-xs text-text-secondary">We have locked in the target job and candidate profile. Let's trigger the LangGraph analysis.</p>
              </div>

              <div className="rounded-xl border border-border-dark bg-background/50 p-4 space-y-3.5 text-xs text-zinc-300">
                <div className="flex justify-between items-center border-b border-border-dark pb-2">
                  <span className="text-zinc-500 font-mono">JOB TARGET:</span>
                  <span className="font-semibold text-white truncate max-w-[250px]">{jobInputType === 'url' ? jobUrl : jobFile?.name}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-zinc-500 font-mono">CANDIDATE RESUME:</span>
                  <span className="font-semibold text-white truncate max-w-[250px]">{resumeFile?.name}</span>
                </div>
              </div>

              {localError && (
                <div className="flex items-center space-x-2 rounded-lg border border-error-bg/25 bg-error-bg/5 p-3 text-xs text-error-bg">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  <span>{localError}</span>
                </div>
              )}

              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={() => setStep(2)}
                  className="flex-1 rounded-lg border border-border-dark bg-[#111113] py-3.5 px-4 text-sm font-semibold text-zinc-300 hover:text-white transition cursor-pointer"
                  disabled={isAnalyzing}
                >
                  Back
                </button>
                <button
                  type="button"
                  onClick={handleRunAnalysis}
                  className={`flex-[2] flex items-center justify-center space-x-2 rounded-lg bg-gradient-to-r from-accent-primary to-accent-secondary py-3.5 px-4 text-sm font-bold text-black shadow-lg shadow-accent-primary/20 hover:opacity-90 transition-all cursor-pointer ${
                    isAnalyzing ? 'opacity-60 cursor-not-allowed' : ''
                  }`}
                  disabled={isAnalyzing}
                >
                  {isAnalyzing ? (
                    <>
                      <RefreshCw className="h-4 w-4 animate-spin text-black" />
                      <span>Processing LangGraph Nodes...</span>
                    </>
                  ) : (
                    <span>Analyze & Optimize Resume</span>
                  )}
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
