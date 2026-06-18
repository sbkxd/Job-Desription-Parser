'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
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
  Cpu,
  GraduationCap,
  Sparkles,
  CheckCircle2,
  FolderKanban,
  Target,
  FileText,
  Activity,
  History,
  TrendingUp
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
  Radar,
  AreaChart,
  Area
} from 'recharts';
import { useStore } from '../store/useStore';

export default function ResultsDashboard() {
  const {
    report: jobReport,
    resumeReport,
    compatibilityReport,
    recommendationReport,
    activeTab,
    setActiveTab
  } = useStore();

  const [copied, setCopied] = useState(false);
  const [responsibilitiesExpanded, setResponsibilitiesExpanded] = useState(false);
  const [qualificationsExpanded, setQualificationsExpanded] = useState(false);
  const [localHistory, setLocalHistory] = useState<any[]>([]);

  // Local storage support for history tracking
  useEffect(() => {
    if (recommendationReport && jobReport && resumeReport) {
      const historyItem = {
        id: Date.now(),
        date: new Date().toLocaleDateString(),
        jobTitle: jobReport.job_information.job_title,
        company: jobReport.job_information.company,
        candidateName: resumeReport.candidate_profile.candidate_name || 'Candidate',
        score: recommendationReport.compatibility_score,
        readiness: recommendationReport.application_readiness_score
      };

      const stored = localStorage.getItem('jd_parser_history');
      let historyList = stored ? JSON.parse(stored) : [];
      // Prevent duplicate saving of the exact same report run
      if (!historyList.some((h: any) => h.jobTitle === historyItem.jobTitle && h.score === historyItem.score)) {
        historyList = [historyItem, ...historyList].slice(0, 10);
        localStorage.setItem('jd_parser_history', JSON.stringify(historyList));
        setLocalHistory(historyList);
      }
    }
  }, [recommendationReport, jobReport, resumeReport]);

  useEffect(() => {
    const stored = localStorage.getItem('jd_parser_history');
    if (stored) {
      setLocalHistory(JSON.parse(stored));
    }
  }, []);

  if (!recommendationReport || !jobReport || !resumeReport) return null;

  // Clipboard copy action
  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify({
      job_description: jobReport,
      resume_profile: resumeReport,
      compatibility: compatibilityReport,
      recommendations: recommendationReport
    }, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Export JSON file download
  const handleExportJson = () => {
    const reportData = {
      job_description: jobReport,
      resume_profile: resumeReport,
      compatibility: compatibilityReport,
      recommendations: recommendationReport
    };
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(reportData, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `career_intelligence_${jobReport.job_information.job_title.toLowerCase().replace(/\s+/g, '_')}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  // Export CSV file download
  const handleExportCsv = () => {
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "Category,Values\n";
    csvContent += `Job Title,"${jobReport.job_information.job_title}"\n`;
    csvContent += `Company,"${jobReport.job_information.company}"\n`;
    csvContent += `Compatibility Score,"${recommendationReport.compatibility_score}%"\n`;
    csvContent += `Readiness Score,"${recommendationReport.application_readiness_score}%"\n`;
    csvContent += `Matched Skills,"${recommendationReport.matched_skills.join(', ')}"\n`;
    csvContent += `Missing Skills,"${recommendationReport.missing_skills.join(', ')}"\n`;
    csvContent += `Tailored Summary,"${recommendationReport.tailored_summary.replace(/"/g, '""')}"\n`;

    const encodedUri = encodeURI(csvContent);
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", encodedUri);
    downloadAnchor.setAttribute("download", `compatibility_report_${jobReport.job_information.job_title.toLowerCase().replace(/\s+/g, '_')}.csv`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  // Score styling color resolver
  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-[#10B981] border-[#10B981]/30'; // Excellent
    if (score >= 75) return 'text-[#00E5FF] border-[#00E5FF]/30'; // Strong
    if (score >= 60) return 'text-[#F59E0B] border-[#F59E0B]/30'; // Moderate
    return 'text-[#EF4444] border-[#EF4444]/30'; // Weak
  };

  // Prepare chart data for Recharts
  const skillSplitData = [
    { name: 'Matched', count: recommendationReport.matched_skills.length, fill: '#10B981' },
    { name: 'Missing', count: recommendationReport.missing_skills.length, fill: '#EF4444' },
    { name: 'Job Skills', count: jobReport.skills.required.length + jobReport.skills.preferred.length, fill: '#8B5CF6' }
  ];

  const radarData = [
    { subject: 'Skills', A: recommendationReport.matched_skills.length, fullMark: 12 },
    { subject: 'Exp Match', A: resumeReport.candidate_profile.years_experience >= (jobReport.role_profile.minimum_experience_years || 0) ? 10 : 4, fullMark: 10 },
    { subject: 'Education', A: resumeReport.candidate_profile.education.length > 0 ? 8 : 2, fullMark: 10 },
    { subject: 'ATS Keywords', A: recommendationReport.ats_recommendations.filter(r => r.coverage_status !== 'MISSING').length, fullMark: 10 },
    { subject: 'Projects', A: resumeReport.projects.length, fullMark: 10 }
  ];

  const atsTimelineData = [
    { keyword: 'Overall', score: recommendationReport.compatibility_score },
    { keyword: 'Keywords', score: recommendationReport.ats_recommendations.length > 0 ? Math.min(100, Math.round((recommendationReport.ats_recommendations.filter(k => k.coverage_status !== 'MISSING').length / recommendationReport.ats_recommendations.length) * 100)) : 100 },
    { keyword: 'Readiness', score: recommendationReport.application_readiness_score }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="mx-auto max-w-7xl px-4 py-8 space-y-8"
    >
      {/* Top Header & Export Actions Panel */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-border-dark pb-6">
        <div>
          <span className="text-xs font-mono text-accent-primary font-semibold tracking-widest uppercase">Career Intelligence Engine</span>
          <h2 className="text-2xl font-bold text-white tracking-tight">Structured Job & Resume Match Report</h2>
          <p className="text-xs text-text-secondary mt-1">Comparing {resumeReport.candidate_profile.candidate_name || 'Candidate'} against {jobReport.job_information.job_title} at {jobReport.job_information.company}</p>
        </div>

        <div className="flex flex-wrap gap-2.5">
          <button
            onClick={handleCopy}
            className="flex items-center space-x-1.5 rounded-lg border border-border-dark bg-[#111113] hover:border-accent-primary/40 px-3.5 py-2 text-xs font-semibold text-zinc-300 hover:text-white transition-all duration-200 cursor-pointer"
          >
            {copied ? <Check className="h-4 w-4 text-[#10B981]" /> : <Copy className="h-4 w-4" />}
            <span>{copied ? 'Copied!' : 'Copy JSON'}</span>
          </button>

          <button
            onClick={handleExportJson}
            className="flex items-center space-x-1.5 rounded-lg border border-border-dark bg-[#111113] hover:border-accent-primary/40 px-3.5 py-2 text-xs font-semibold text-zinc-300 hover:text-white transition-all duration-200 cursor-pointer"
          >
            <FileJson className="h-4 w-4 text-accent-secondary" />
            <span>Export JSON</span>
          </button>

          <button
            onClick={handleExportCsv}
            className="flex items-center space-x-1.5 rounded-lg border border-border-dark bg-[#111113] hover:border-accent-primary/40 px-3.5 py-2 text-xs font-semibold text-zinc-300 hover:text-white transition-all duration-200 cursor-pointer"
          >
            <FileSpreadsheet className="h-4 w-4 text-[#10B981]" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Interactive Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-border-dark pb-3 text-xs sm:text-sm">
        {(['compatibility', 'recommendations', 'job', 'resume', 'analytics'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg font-semibold capitalize transition-all cursor-pointer ${
              activeTab === tab
                ? 'bg-gradient-to-r from-accent-primary/10 to-accent-secondary/10 border border-accent-primary/20 text-accent-primary'
                : 'text-text-secondary hover:text-white border border-transparent'
            }`}
          >
            {tab === 'compatibility' ? 'Compatibility Analysis' : tab === 'recommendations' ? 'ATS & Improvement advice' : `${tab} Intelligence`}
          </button>
        ))}
      </div>

      {/* Tab Panels */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.3 }}
          className="space-y-6"
        >
          {activeTab === 'compatibility' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Score card & summary info */}
              <div className="space-y-6 lg:col-span-1">
                <div className="rounded-2xl border border-border-dark bg-[#111113]/60 glass-panel p-6 flex flex-col items-center justify-center text-center space-y-4 shadow-xl">
                  <span className="text-xs font-mono text-zinc-500 uppercase tracking-widest">Compatibility Rating</span>
                  <div className={`h-36 w-36 rounded-full border-4 flex flex-col items-center justify-center ${getScoreColor(recommendationReport.compatibility_score)}`}>
                    <span className="text-4xl font-extrabold font-mono">{recommendationReport.compatibility_score}%</span>
                    <span className="text-xs uppercase tracking-wider font-semibold opacity-75">Compatible</span>
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-base">
                      {recommendationReport.compatibility_score >= 90 ? 'Excellent Match' :
                       recommendationReport.compatibility_score >= 75 ? 'Strong Match' :
                       recommendationReport.compatibility_score >= 60 ? 'Moderate Match' : 'Weak Match'}
                    </h3>
                    <p className="text-xs text-text-secondary mt-1">Weighted profile score evaluated across skills, years, and credentials.</p>
                  </div>
                </div>

                <div className="rounded-2xl border border-border-dark bg-[#111113]/60 glass-panel p-6 space-y-4 shadow-xl">
                  <div className="flex items-center space-x-2 text-accent-secondary">
                    <Sparkles className="h-5 w-5" />
                    <h3 className="font-bold text-white">Tailored Professional Summary</h3>
                  </div>
                  <p className="text-xs text-zinc-300 leading-relaxed font-sans">{recommendationReport.tailored_summary}</p>
                </div>
              </div>

              {/* Matched, missing, strengths and gaps list */}
              <div className="lg:col-span-2 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Matched skills */}
                  <div className="rounded-xl border border-border-dark bg-[#111113]/40 p-5 space-y-4">
                    <div className="flex items-center space-x-2 text-[#10B981]">
                      <CheckCircle2 className="h-5 w-5" />
                      <h4 className="font-bold text-white text-sm">Matched Skills</h4>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {recommendationReport.matched_skills.map((s, idx) => (
                        <span key={idx} className="rounded bg-[#10B981]/10 border border-[#10B981]/25 px-2 py-0.5 text-xs text-[#10B981] font-medium">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Missing skills */}
                  <div className="rounded-xl border border-border-dark bg-[#111113]/40 p-5 space-y-4">
                    <div className="flex items-center space-x-2 text-[#F59E0B]">
                      <AlertTriangle className="h-5 w-5" />
                      <h4 className="font-bold text-white text-sm">Missing Target Skills</h4>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {recommendationReport.missing_skills.map((s, idx) => (
                        <span key={idx} className="rounded bg-[#F59E0B]/10 border border-[#F59E0B]/25 px-2 py-0.5 text-xs text-[#F59E0B] font-medium">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Strength Analysis */}
                <div className="rounded-xl border border-border-dark bg-[#111113]/40 p-5 space-y-4">
                  <div className="flex items-center space-x-2 text-accent-primary">
                    <Target className="h-5 w-5" />
                    <h4 className="font-bold text-white text-sm">Key Alignment Strengths</h4>
                  </div>
                  <ul className="grid grid-cols-1 md:grid-cols-2 gap-3 pl-1">
                    {recommendationReport.strengths.map((str, idx) => (
                      <li key={idx} className="flex items-start space-x-2 text-xs text-zinc-300">
                        <Check className="h-4 w-4 shrink-0 text-[#10B981] mt-0.5" />
                        <span>{str}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Gap Analysis */}
                {recommendationReport.critical_gaps.length > 0 && (
                  <div className="rounded-xl border border-border-dark bg-[#111113]/40 p-5 space-y-3.5">
                    <div className="flex items-center space-x-2 text-[#EF4444]">
                      <AlertTriangle className="h-5 w-5" />
                      <h4 className="font-bold text-white text-sm">Critical Missing Gaps</h4>
                    </div>
                    <ul className="space-y-2.5">
                      {recommendationReport.critical_gaps.map((g, idx) => (
                        <li key={idx} className="flex items-start space-x-2 text-xs text-zinc-300">
                          <span className="h-1.5 w-1.5 rounded-full bg-[#EF4444] mt-2 shrink-0" />
                          <span>{g}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'recommendations' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* ATS optimization gauge and improvements */}
              <div className="lg:col-span-1 space-y-6">
                <div className="rounded-2xl border border-border-dark bg-[#111113]/60 glass-panel p-6 flex flex-col items-center justify-center text-center space-y-4 shadow-xl">
                  <span className="text-xs font-mono text-zinc-500 uppercase tracking-widest">Application Readiness</span>
                  <div className={`h-32 w-32 rounded-full border-4 flex flex-col items-center justify-center ${getScoreColor(recommendationReport.application_readiness_score)}`}>
                    <span className="text-3xl font-extrabold font-mono">{recommendationReport.application_readiness_score}%</span>
                    <span className="text-3xs uppercase tracking-wider font-semibold opacity-75">Ready to Apply</span>
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-sm">ATS Readiness Status</h3>
                    <p className="text-3xs text-text-secondary mt-1 leading-relaxed">{recommendationReport.application_readiness_recommendation}</p>
                  </div>
                </div>

                {/* ATS Keyword Recommendations */}
                <div className="rounded-2xl border border-border-dark bg-[#111113]/60 glass-panel p-5 space-y-4 shadow-xl">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-text-secondary">ATS Keyword Gap Analysis</h4>
                  <div className="space-y-4.5">
                    {recommendationReport.ats_recommendations.map((rec, idx) => (
                      <div key={idx} className="space-y-1.5 text-2xs border-b border-border-dark pb-3.5 last:border-b-0 last:pb-0">
                        <div className="flex justify-between items-center">
                          <span className="font-mono font-bold text-white">{rec.keyword}</span>
                          <span className={`px-2 py-0.5 rounded text-3xs font-mono font-semibold uppercase ${
                            rec.coverage_status === 'MISSING' ? 'bg-[#EF4444]/10 text-[#EF4444]' : 'bg-[#F59E0B]/10 text-[#F59E0B]'
                          }`}>{rec.coverage_status}</span>
                        </div>
                        <p className="text-zinc-400 leading-relaxed">{rec.recommendation}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Section-by-section improvements */}
              <div className="lg:col-span-2 space-y-6">
                <div className="flex items-center space-x-2 text-accent-primary border-b border-border-dark pb-3">
                  <Cpu className="h-5 w-5" />
                  <h3 className="font-bold text-white">Section-Level Resume Improvements</h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {recommendationReport.resume_improvements.map((imp, idx) => (
                    <div key={idx} className="rounded-xl border border-border-dark bg-[#111113]/40 p-5 space-y-3 shadow-md hover:border-accent-primary/20 transition-all">
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-bold text-white uppercase font-mono tracking-wider">{imp.section}</span>
                        <span className="rounded bg-accent-secondary/15 border border-accent-secondary/25 px-2 py-0.5 text-3xs text-accent-secondary font-semibold">
                          {imp.type}
                        </span>
                      </div>
                      <p className="text-xs text-zinc-300 leading-relaxed font-sans">{imp.message}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'job' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Job Info Panel */}
              <div className="space-y-6 lg:col-span-1">
                <div className="rounded-xl border border-border-dark bg-[#111113]/60 glass-panel p-5.5 space-y-4">
                  <div className="flex items-center space-x-2.5 text-accent-primary">
                    <Briefcase className="h-5 w-5" />
                    <h3 className="font-semibold text-white">Job Information</h3>
                  </div>
                  <div className="space-y-3.5 text-sm">
                    <div>
                      <p className="text-2xs font-mono text-zinc-500 uppercase tracking-wider">Job Title</p>
                      <p className="font-semibold text-white">{jobReport.job_information.job_title || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-2xs font-mono text-zinc-500 uppercase tracking-wider">Company</p>
                      <p className="text-zinc-200">{jobReport.job_information.company || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-2xs font-mono text-zinc-500 uppercase tracking-wider">Location</p>
                      <div className="flex items-center space-x-1 text-zinc-300">
                        <MapPin className="h-3.5 w-3.5 text-zinc-500" />
                        <span>{jobReport.job_information.location || 'N/A'}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="rounded-xl border border-border-dark bg-[#111113]/60 glass-panel p-5.5 space-y-4">
                  <div className="flex items-center space-x-2.5 text-accent-secondary">
                    <User className="h-5 w-5" />
                    <h3 className="font-semibold text-white">Role Profile</h3>
                  </div>
                  <div className="space-y-3.5">
                    <div>
                      <p className="text-2xs font-mono text-zinc-500 uppercase tracking-wider">Seniority</p>
                      <span className="inline-flex rounded bg-[#1f1635] border border-accent-secondary/20 px-2 py-0.5 text-xs font-semibold text-accent-secondary">
                        {jobReport.role_profile.seniority || 'Not specified'}
                      </span>
                    </div>
                    <div>
                      <p className="text-2xs font-mono text-zinc-500 uppercase tracking-wider">Experience Requirement</p>
                      <div className="flex items-center space-x-1.5 text-sm text-zinc-200">
                        <Calendar className="h-4 w-4 text-zinc-500" />
                        <span>
                          {jobReport.role_profile.minimum_experience_years !== null
                            ? `${jobReport.role_profile.minimum_experience_years} to ${jobReport.role_profile.maximum_experience_years || '5+'} Years`
                            : 'Not specified'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Responsibilities & Qualifications */}
              <div className="lg:col-span-2 space-y-6">
                <div className="rounded-xl border border-border-dark bg-[#111113]/60 glass-panel p-6 space-y-5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2 text-zinc-200">
                      <FileCheck className="h-5 w-5 text-zinc-400" />
                      <h3 className="font-semibold text-white">Target Job Specifications</h3>
                    </div>
                  </div>

                  <div className="space-y-4.5 pl-4 border-l border-border-dark relative">
                    <p className="text-xs font-mono text-zinc-500 uppercase tracking-widest">Key Responsibilities</p>
                    {jobReport.responsibilities.map((resp, idx) => (
                      <div key={idx} className="relative text-xs text-zinc-300">
                        <span className="absolute -left-[20.5px] top-1.5 h-2 w-2 rounded-full bg-accent-secondary" />
                        <p>{resp}</p>
                      </div>
                    ))}
                  </div>

                  <div className="space-y-4.5 pl-4 border-l border-border-dark relative pt-4">
                    <p className="text-xs font-mono text-zinc-500 uppercase tracking-widest">Job Qualifications</p>
                    {jobReport.qualifications.map((qual, idx) => (
                      <div key={idx} className="relative text-xs text-zinc-300">
                        <span className="absolute -left-[20.5px] top-1.5 h-2 w-2 rounded-full bg-accent-primary" />
                        <p>{qual}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'resume' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Profile Overview Card */}
              <div className="space-y-6 lg:col-span-1">
                <div className="rounded-xl border border-border-dark bg-[#111113]/60 glass-panel p-5.5 space-y-4">
                  <div className="flex items-center space-x-2.5 text-accent-primary">
                    <User className="h-5 w-5" />
                    <h3 className="font-semibold text-white">Candidate Details</h3>
                  </div>
                  <div className="space-y-3.5 text-sm">
                    <div>
                      <p className="text-2xs font-mono text-zinc-500 uppercase tracking-wider">Candidate Name</p>
                      <p className="font-semibold text-white">{resumeReport.candidate_profile.candidate_name || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-2xs font-mono text-zinc-500 uppercase tracking-wider">Experience Years</p>
                      <p className="text-zinc-200">{resumeReport.candidate_profile.years_experience} Years</p>
                    </div>
                    {resumeReport.candidate_profile.certifications.length > 0 && (
                      <div>
                        <p className="text-2xs font-mono text-zinc-500 uppercase tracking-wider mb-1">Certifications</p>
                        <div className="flex flex-wrap gap-1">
                          {resumeReport.candidate_profile.certifications.map((c, idx) => (
                            <span key={idx} className="rounded bg-accent-secondary/10 border border-accent-secondary/20 px-2 py-0.5 text-3xs text-accent-secondary">
                              {c}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Education Panel */}
                <div className="rounded-xl border border-border-dark bg-[#111113]/60 glass-panel p-5.5 space-y-4">
                  <div className="flex items-center space-x-2.5 text-accent-secondary">
                    <GraduationCap className="h-5 w-5" />
                    <h3 className="font-semibold text-white">Education History</h3>
                  </div>
                  <div className="space-y-4 text-xs">
                    {resumeReport.candidate_profile.education.map((edu, idx) => (
                      <div key={idx} className="border-b border-border-dark pb-3.5 last:border-b-0 last:pb-0 space-y-1">
                        <p className="font-bold text-white">{edu.degree} in {edu.field_of_study}</p>
                        <p className="text-zinc-400">{edu.school} {edu.graduation_year && `(${edu.graduation_year})`}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Professional Work Experience Timeline */}
              <div className="lg:col-span-2 space-y-6">
                <div className="rounded-xl border border-border-dark bg-[#111113]/60 glass-panel p-6 space-y-6">
                  <div className="flex items-center space-x-2 text-zinc-200">
                    <Briefcase className="h-5 w-5 text-zinc-400" />
                    <h3 className="font-semibold text-white">Work Experience History</h3>
                  </div>

                  <div className="space-y-6 pl-4 border-l border-border-dark relative">
                    {resumeReport.experience.map((exp, idx) => (
                      <div key={idx} className="relative text-xs space-y-1.5">
                        <span className="absolute -left-[20.5px] top-1.5 h-2 w-2 rounded-full bg-accent-secondary" />
                        <div className="flex justify-between items-center">
                          <p className="font-bold text-white">{exp.job_title} at {exp.company}</p>
                          <span className="text-3xs font-mono text-zinc-500">{exp.start_date} - {exp.end_date}</span>
                        </div>
                        <p className="text-zinc-400 leading-relaxed font-sans">{exp.description}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Project History */}
                {resumeReport.projects.length > 0 && (
                  <div className="rounded-xl border border-border-dark bg-[#111113]/60 glass-panel p-6 space-y-4">
                    <div className="flex items-center space-x-2 text-zinc-200">
                      <FolderKanban className="h-5 w-5 text-zinc-400" />
                      <h3 className="font-semibold text-white">Notable Projects</h3>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {resumeReport.projects.map((proj, idx) => (
                        <div key={idx} className="rounded-xl border border-border-dark bg-background/50 p-4 space-y-2">
                          <h4 className="font-bold text-white text-xs">{proj.project_title}</h4>
                          <p className="text-2xs text-zinc-400 leading-relaxed">{proj.description}</p>
                          <div className="flex flex-wrap gap-1 pt-1.5">
                            {proj.technologies.map((t, idx) => (
                              <span key={idx} className="rounded bg-accent-primary/10 border border-accent-primary/20 px-1.5 py-0.5 text-3xs text-accent-primary font-mono">
                                {t}
                              </span>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="rounded-xl border border-border-dark bg-[#111113]/60 glass-panel p-6 space-y-6 shadow-xl">
              <div className="flex items-center space-x-2 text-accent-primary">
                <Activity className="h-5 w-5" />
                <h3 className="font-bold text-white">Analytics Panel</h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-[260px]">
                {/* Split matches counts */}
                <div className="flex flex-col space-y-2">
                  <span className="text-xs font-mono text-zinc-500 uppercase text-center">Skill Matches Breakdown</span>
                  <div className="flex-1 w-full text-3xs">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={skillSplitData} margin={{ top: 15, right: 10, left: -25, bottom: 0 }}>
                        <XAxis dataKey="name" stroke="#52525B" tickLine={false} />
                        <YAxis stroke="#52525B" tickLine={false} />
                        <Tooltip contentStyle={{ backgroundColor: '#111113', borderColor: '#27272A' }} />
                        <Bar dataKey="count" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Attribute density */}
                <div className="flex flex-col space-y-2">
                  <span className="text-xs font-mono text-zinc-500 uppercase text-center">Skill Category Coverage</span>
                  <div className="flex-1 w-full text-3xs">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                        <PolarGrid stroke="#27272A" />
                        <PolarAngleAxis dataKey="subject" stroke="#71717A" />
                        <Radar name="Attributes" dataKey="A" stroke="#8B5CF6" fill="#8B5CF6" fillOpacity={0.3} />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* ATS Timeline coverage */}
                <div className="flex flex-col space-y-2">
                  <span className="text-xs font-mono text-zinc-500 uppercase text-center">ATS Keyword Coverage</span>
                  <div className="flex-1 w-full text-3xs">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={atsTimelineData} margin={{ top: 15, right: 10, left: -25, bottom: 0 }}>
                        <XAxis dataKey="keyword" stroke="#52525B" tickLine={false} />
                        <YAxis domain={[0, 100]} stroke="#52525B" tickLine={false} />
                        <Tooltip contentStyle={{ backgroundColor: '#111113', borderColor: '#27272A' }} />
                        <Area type="monotone" dataKey="score" stroke="#00E5FF" fill="rgba(0, 229, 255, 0.1)" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </AnimatePresence>

      {/* History tracker panel */}
      {localHistory.length > 0 && (
        <div className="rounded-2xl border border-border-dark bg-[#111113]/60 glass-panel p-6 space-y-4 shadow-xl">
          <div className="flex items-center space-x-2 text-zinc-400 border-b border-border-dark pb-3">
            <History className="h-5 w-5" />
            <h3 className="font-bold text-white text-sm">Recent Analyses History</h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {localHistory.map((h) => (
              <div key={h.id} className="rounded-xl border border-border-dark bg-background/40 p-4 space-y-2.5 hover:border-zinc-700 transition">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-bold text-white text-xs truncate max-w-[170px]">{h.jobTitle}</h4>
                    <p className="text-3xs text-text-secondary">{h.company}</p>
                  </div>
                  <span className="rounded bg-accent-primary/10 border border-accent-primary/25 px-1.5 py-0.5 text-3xs font-mono font-bold text-accent-primary">
                    {h.score}% Match
                  </span>
                </div>
                <div className="flex justify-between items-center text-3xs text-zinc-500 font-mono pt-1">
                  <span>{h.candidateName}</span>
                  <span>{h.date}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}
