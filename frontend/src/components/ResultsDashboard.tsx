'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Briefcase,
  MapPin,
  User,
  Calendar,
  Award,
  Terminal,
  FileCheck,
  AlertTriangle,
  Download,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  FileJson,
  FileSpreadsheet,
  HelpCircle,
  Tag
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  AreaChart,
  Area
} from 'recharts';
import { useStore } from '../store/useStore';

export default function ResultsDashboard() {
  const { report } = useStore();
  const [copied, setCopied] = useState(false);
  const [responsibilitiesExpanded, setResponsibilitiesExpanded] = useState(false);
  const [qualificationsExpanded, setQualificationsExpanded] = useState(false);

  if (!report) return null;

  const {
    job_information,
    role_profile,
    skills,
    education_requirements,
    responsibilities,
    qualifications,
    technology_stack,
    review_summary
  } = report;

  // Clipboard copy action
  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(report, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Export JSON file download
  const handleExportJson = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(report, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `jd_intelligence_${job_information.job_title.toLowerCase().replace(/\s+/g, '_')}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  // Export CSV file download
  const handleExportCsv = () => {
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "Category,Values\n";
    csvContent += `Job Title,"${job_information.job_title}"\n`;
    csvContent += `Company,"${job_information.company}"\n`;
    csvContent += `Location,"${job_information.location}"\n`;
    csvContent += `Seniority,"${role_profile.seniority}"\n`;
    csvContent += `Required Skills,"${skills.required.join(', ')}"\n`;
    csvContent += `Preferred Skills,"${skills.preferred.join(', ')}"\n`;
    csvContent += `Technology Stack,"${technology_stack.join(', ')}"\n`;

    const encodedUri = encodeURI(csvContent);
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", encodedUri);
    downloadAnchor.setAttribute("download", `jd_intelligence_${job_information.job_title.toLowerCase().replace(/\s+/g, '_')}.csv`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  // Prepare chart data for Recharts
  const skillDistributionData = [
    { name: 'Required', count: skills.required.length, fill: '#00E5FF' },
    { name: 'Preferred', count: skills.preferred.length, fill: '#8B5CF6' },
    { name: 'Normalized', count: skills.normalized.length, fill: '#10B981' }
  ];

  const categoryBreakdownData = [
    { subject: 'Required Skills', A: skills.required.length, fullMark: 15 },
    { subject: 'Preferred Skills', A: skills.preferred.length, fullMark: 15 },
    { subject: 'Tech Stack', A: technology_stack.length, fullMark: 15 },
    { subject: 'Qualifications', A: qualifications.length, fullMark: 15 },
    { subject: 'Education', A: education_requirements.length, fullMark: 15 }
  ];

  // Simulated confidence mapping
  const confidenceData = [
    { stage: 'Ingestion', confidence: 99 },
    { stage: 'Segmentation', confidence: 95 },
    { stage: 'Extraction', confidence: 88 },
    { stage: 'Normalization', confidence: 82 },
    { stage: 'Review Eval', confidence: 90 },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
      className="mx-auto max-w-7xl px-4 py-8 space-y-8"
    >
      {/* Top Banner with Action Buttons */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border-dark pb-6">
        <div>
          <span className="text-xs font-mono text-accent-primary font-semibold tracking-widest uppercase">Analysis Finalized</span>
          <h2 className="text-2xl font-bold text-white tracking-tight">Structured Job Intelligence Report</h2>
        </div>

        {/* Export Actions Panel */}
        <div className="flex flex-wrap gap-2.5">
          <button
            onClick={handleCopy}
            className="flex items-center space-x-1.5 rounded-lg border border-border-dark bg-[#111113] hover:border-accent-primary/40 px-3.5 py-2 text-xs font-semibold text-zinc-300 hover:text-white transition-all duration-300 cursor-pointer"
          >
            {copied ? <Check className="h-4 w-4 text-success-bg" /> : <Copy className="h-4 w-4" />}
            <span>{copied ? 'Copied!' : 'Copy JSON'}</span>
          </button>

          <button
            onClick={handleExportJson}
            className="flex items-center space-x-1.5 rounded-lg border border-border-dark bg-[#111113] hover:border-accent-primary/40 px-3.5 py-2 text-xs font-semibold text-zinc-300 hover:text-white transition-all duration-300 cursor-pointer"
          >
            <FileJson className="h-4 w-4 text-accent-secondary" />
            <span>Export JSON</span>
          </button>

          <button
            onClick={handleExportCsv}
            className="flex items-center space-x-1.5 rounded-lg border border-border-dark bg-[#111113] hover:border-accent-primary/40 px-3.5 py-2 text-xs font-semibold text-zinc-300 hover:text-white transition-all duration-300 cursor-pointer"
          >
            <FileSpreadsheet className="h-4 w-4 text-success-bg" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Grid: Main Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Column 1: Info & Profile Card */}
        <div className="space-y-6 lg:col-span-1">
          {/* Job Information Card */}
          <div className="rounded-xl border border-border-dark bg-[#111113]/60 glass-panel p-5.5 space-y-4">
            <div className="flex items-center space-x-2.5 text-accent-primary">
              <Briefcase className="h-5 w-5" />
              <h3 className="font-semibold text-white">Job Information</h3>
            </div>

            <div className="space-y-3 text-sm">
              <div>
                <p className="text-2xs font-mono text-zinc-500 uppercase tracking-wider">Job Title</p>
                <p className="font-semibold text-white">{job_information.job_title || 'N/A'}</p>
              </div>
              <div>
                <p className="text-2xs font-mono text-zinc-500 uppercase tracking-wider">Company</p>
                <p className="text-zinc-200">{job_information.company || 'N/A'}</p>
              </div>
              <div>
                <p className="text-2xs font-mono text-zinc-500 uppercase tracking-wider">Location</p>
                <div className="flex items-center space-x-1 text-zinc-300">
                  <MapPin className="h-3.5 w-3.5 text-zinc-500" />
                  <span>{job_information.location || 'N/A'}</span>
                </div>
              </div>
              <div>
                <p className="text-2xs font-mono text-zinc-500 uppercase tracking-wider">Source Type</p>
                <span className="inline-flex rounded-full bg-accent-primary/10 border border-accent-primary/20 px-2.5 py-0.5 text-xs text-accent-primary font-medium capitalize">
                  {job_information.source_type || 'URL'}
                </span>
              </div>
            </div>
          </div>

          {/* Role Profile Card */}
          <div className="rounded-xl border border-border-dark bg-[#111113]/60 glass-panel p-5.5 space-y-4">
            <div className="flex items-center space-x-2.5 text-accent-secondary">
              <User className="h-5 w-5" />
              <h3 className="font-semibold text-white">Role Profile</h3>
            </div>

            <div className="space-y-3.5">
              <div>
                <p className="text-2xs font-mono text-zinc-500 uppercase tracking-wider">Seniority</p>
                <span className="inline-flex rounded bg-[#1f1635] border border-accent-secondary/20 px-2 py-0.5 text-xs font-semibold text-accent-secondary">
                  {role_profile.seniority || 'Not specified'}
                </span>
              </div>

              <div>
                <p className="text-2xs font-mono text-zinc-500 uppercase tracking-wider">Experience Requirement</p>
                <div className="flex items-center space-x-1.5 text-sm text-zinc-200">
                  <Calendar className="h-4 w-4 text-zinc-500" />
                  <span>
                    {role_profile.minimum_experience_years !== null
                      ? `${role_profile.minimum_experience_years} to ${role_profile.maximum_experience_years || '5+'} Years`
                      : 'Not specified'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Review Summary Card */}
          <div className="rounded-xl border border-border-dark bg-[#111113]/60 glass-panel p-5.5 space-y-4">
            <div className="flex items-center space-x-2.5 text-warning-bg">
              <AlertTriangle className="h-5 w-5" />
              <h3 className="font-semibold text-white">Audit Summary</h3>
            </div>

            <div className="space-y-4 text-xs">
              <div className="flex items-center justify-between border-b border-border-dark pb-2">
                <span className="text-text-secondary">Needs Review?</span>
                <span className={`font-mono font-bold ${review_summary.review_required ? 'text-error-bg' : 'text-success-bg'}`}>
                  {review_summary.review_required ? 'YES (FLAGGED)' : 'NO (PASSED)'}
                </span>
              </div>

              {review_summary.flagged_skills.length > 0 && (
                <div>
                  <p className="text-2xs font-mono text-zinc-500 uppercase tracking-wider mb-1">Flagged Out-of-Taxonomy Skills</p>
                  <div className="flex flex-wrap gap-1">
                    {review_summary.flagged_skills.map((skill, idx) => (
                      <span key={idx} className="rounded bg-error-bg/10 border border-error-bg/20 px-1.5 py-0.5 text-3xs text-error-bg font-mono">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {review_summary.low_confidence_items.length > 0 && (
                <div>
                  <p className="text-2xs font-mono text-zinc-500 uppercase tracking-wider mb-1">Low Confidence Items</p>
                  <ul className="list-disc pl-4 space-y-1 text-zinc-400 text-3xs">
                    {review_summary.low_confidence_items.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Column 2 & 3: Skills, Responsibilities, Qualifications & Charts */}
        <div className="lg:col-span-2 space-y-6">

          {/* Skills Card */}
          <div className="rounded-xl border border-border-dark bg-[#111113]/60 glass-panel p-6 space-y-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-success-bg">
                <Award className="h-5 w-5" />
                <h3 className="font-semibold text-white">Extracted Skills</h3>
              </div>
              <span className="text-3xs font-mono text-zinc-500">Source taxonomy: ESCO v1.1</span>
            </div>

            <div className="space-y-4">
              {/* Required Skills */}
              <div>
                <p className="text-2xs font-mono text-zinc-500 uppercase tracking-wider mb-2">Required Skills</p>
                <div className="flex flex-wrap gap-1.5">
                  {skills.required.length > 0 ? (
                    skills.required.map((skill, idx) => (
                      <span key={idx} className="rounded-md bg-accent-primary/10 border border-accent-primary/20 px-2.5 py-1 text-xs text-accent-primary font-medium hover:bg-accent-primary/20 transition-colors duration-150">
                        {skill}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-zinc-500">None extracted</span>
                  )}
                </div>
              </div>

              {/* Preferred Skills */}
              <div>
                <p className="text-2xs font-mono text-zinc-500 uppercase tracking-wider mb-2">Preferred / Nice-to-Have</p>
                <div className="flex flex-wrap gap-1.5">
                  {skills.preferred.length > 0 ? (
                    skills.preferred.map((skill, idx) => (
                      <span key={idx} className="rounded-md bg-accent-secondary/10 border border-accent-secondary/20 px-2.5 py-1 text-xs text-accent-secondary font-medium hover:bg-accent-secondary/20 transition-colors duration-150">
                        {skill}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-zinc-500">None extracted</span>
                  )}
                </div>
              </div>

              {/* Normalized ESCO Mapping */}
              {skills.normalized.length > 0 && (
                <div className="pt-2 border-t border-border-dark">
                  <p className="text-2xs font-mono text-zinc-500 uppercase tracking-wider mb-2">ESCO Taxonomy Normalized Matches</p>
                  <div className="flex flex-wrap gap-1.5">
                    {skills.normalized.map((skill, idx) => (
                      <span key={idx} className="rounded-md bg-success-bg/10 border border-success-bg/20 px-2.5 py-1 text-xs text-success-bg font-medium">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Technology Stack Card (Tag cloud) */}
          <div className="rounded-xl border border-border-dark bg-[#111113]/60 glass-panel p-6 space-y-4">
            <div className="flex items-center space-x-2 text-[#00E5FF]">
              <Terminal className="h-5 w-5" />
              <h3 className="font-semibold text-white">Technology Stack Cloud</h3>
            </div>

            <div className="flex flex-wrap gap-2">
              {technology_stack.length > 0 ? (
                technology_stack.map((tech, idx) => {
                  // Interactive coloring categories
                  const colors = [
                    'bg-zinc-800 border-zinc-700 hover:border-accent-primary/40 text-zinc-300',
                    'bg-zinc-800 border-zinc-700 hover:border-accent-secondary/40 text-zinc-300'
                  ];
                  return (
                    <span
                      key={idx}
                      className={`inline-flex items-center space-x-1.5 rounded-full border px-3 py-1 text-xs font-mono transition-all duration-300 cursor-pointer ${colors[idx % colors.length]}`}
                    >
                      <Tag className="h-3 w-3 text-accent-primary" />
                      <span>{tech}</span>
                    </span>
                  );
                })
              ) : (
                <span className="text-xs text-zinc-500">None detected</span>
              )}
            </div>
          </div>

          {/* Collapsible: Responsibilities & Qualifications */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

            {/* Responsibilities Timeline Card */}
            <div className="rounded-xl border border-border-dark bg-[#111113]/60 glass-panel p-5.5 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2 text-zinc-200">
                  <Briefcase className="h-5 w-5 text-zinc-400" />
                  <h3 className="font-semibold text-white">Responsibilities</h3>
                </div>
                <button
                  onClick={() => setResponsibilitiesExpanded(!responsibilitiesExpanded)}
                  className="text-text-secondary hover:text-white cursor-pointer"
                >
                  {responsibilitiesExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                </button>
              </div>

              <div className={`space-y-4 relative pl-4 border-l border-border-dark ${responsibilitiesExpanded ? '' : 'max-h-[160px] overflow-hidden'}`}>
                {responsibilities.length > 0 ? (
                  responsibilities.map((resp, idx) => (
                    <div key={idx} className="relative text-xs text-zinc-300">
                      <span className="absolute -left-[20.5px] top-1.5 h-2 w-2 rounded-full bg-accent-secondary" />
                      <p>{resp}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-zinc-500">None parsed</p>
                )}
              </div>
            </div>

            {/* Qualifications Checklist Card */}
            <div className="rounded-xl border border-border-dark bg-[#111113]/60 glass-panel p-5.5 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2 text-zinc-200">
                  <FileCheck className="h-5 w-5 text-zinc-400" />
                  <h3 className="font-semibold text-white">Qualifications</h3>
                </div>
                <button
                  onClick={() => setQualificationsExpanded(!qualificationsExpanded)}
                  className="text-text-secondary hover:text-white cursor-pointer"
                >
                  {qualificationsExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                </button>
              </div>

              <div className={`space-y-3 ${qualificationsExpanded ? '' : 'max-h-[160px] overflow-hidden'}`}>
                {qualifications.length > 0 ? (
                  qualifications.map((qual, idx) => (
                    <div key={idx} className="flex items-start space-x-2 text-xs text-zinc-300">
                      <Check className="h-4 w-4 shrink-0 text-success-bg mt-0.5" />
                      <p>{qual}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-zinc-500">None parsed</p>
                )}
              </div>
            </div>

          </div>

          {/* Visualizations Section */}
          <div className="rounded-xl border border-border-dark bg-[#111113]/60 glass-panel p-6 space-y-6">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-text-secondary">Advanced Visualizations</h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-[220px]">

              {/* Chart 1: Skill Distribution */}
              <div className="flex flex-col space-y-2">
                <span className="text-2xs font-mono text-zinc-500 uppercase text-center">Skill Type Split</span>
                <div className="flex-1 w-full text-3xs">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={skillDistributionData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                      <XAxis dataKey="name" stroke="#52525B" tickLine={false} />
                      <YAxis stroke="#52525B" tickLine={false} />
                      <Tooltip contentStyle={{ backgroundColor: '#111113', borderColor: '#27272A' }} />
                      <Bar dataKey="count" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Chart 2: Category Breakdown */}
              <div className="flex flex-col space-y-2">
                <span className="text-2xs font-mono text-zinc-500 uppercase text-center">Attribute Density</span>
                <div className="flex-1 w-full text-3xs">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart cx="50%" cy="50%" outerRadius="70%" data={categoryBreakdownData}>
                      <PolarGrid stroke="#27272A" />
                      <PolarAngleAxis dataKey="subject" stroke="#71717A" />
                      <Radar name="Count" dataKey="A" stroke="#8B5CF6" fill="#8B5CF6" fillOpacity={0.3} />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Chart 3: Pipeline Confidence */}
              <div className="flex flex-col space-y-2">
                <span className="text-2xs font-mono text-zinc-500 uppercase text-center">Extraction Confidence %</span>
                <div className="flex-1 w-full text-3xs">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={confidenceData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                      <XAxis dataKey="stage" stroke="#52525B" tickLine={false} />
                      <YAxis domain={[0, 100]} stroke="#52525B" tickLine={false} />
                      <Tooltip contentStyle={{ backgroundColor: '#111113', borderColor: '#27272A' }} />
                      <Area type="monotone" dataKey="confidence" stroke="#00E5FF" fill="rgba(0, 229, 255, 0.1)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

            </div>
          </div>

        </div>

      </div>
    </motion.div>
  );
}
