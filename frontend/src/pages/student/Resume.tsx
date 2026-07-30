import React, { useEffect, useState } from 'react';
import { resumeApi } from '../../api';
import { ResumeAnalysis } from '../../types';
import { CircularScore } from '../../components/charts/CircularScore';
import { FileText, CheckCircle, AlertTriangle, Sparkles, RefreshCw } from 'lucide-react';

export const Resume: React.FC = () => {
  const [data, setData] = useState<ResumeAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);

  const fetchAnalysis = () => {
    setLoading(true);
    resumeApi.getAnalysis(1)
      .then(res => setData(res))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchAnalysis();
  }, []);

  const handleRunAnalyze = () => {
    setAnalyzing(true);
    resumeApi.analyze()
      .then(res => setData(res))
      .catch(err => console.error(err))
      .finally(() => setAnalyzing(false));
  };

  if (loading) return <div className="p-8 text-center text-slate-500">Parsing resume PDF & computing ATS score...</div>;

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <FileText className="text-linkedin-blue" size={24} /> ATS Resume Intelligence Analyzer
          </h2>
          <p className="text-xs text-slate-500 mt-1">Deep NLP skill extraction & Applicant Tracking System scoring</p>
        </div>
        <button
          onClick={handleRunAnalyze}
          disabled={analyzing}
          className="px-4 py-2 bg-linkedin-blue hover:bg-linkedin-hover text-white text-xs font-semibold rounded-lg shadow-sm flex items-center gap-2 transition-colors disabled:opacity-50"
        >
          <RefreshCw size={14} className={analyzing ? 'animate-spin' : ''} />
          <span>{analyzing ? 'Analyzing...' : 'Re-run ATS Audit'}</span>
        </button>
      </div>

      {/* Main Score & Suggestions Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col items-center justify-center">
          <CircularScore score={data?.ats_score || 85} label="ATS Score" sublabel="Keyword Match Index" color="#0A66C2" />
        </div>

        <div className="lg:col-span-2 bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
            <Sparkles className="text-amber-500" size={16} /> AI Optimization Suggestions
          </h3>
          <ul className="space-y-2.5">
            {data?.suggestions.map((sug, i) => (
              <li key={i} className="flex items-start gap-2.5 text-xs text-slate-700 dark:text-slate-300 bg-amber-50/50 dark:bg-amber-950/20 p-3 rounded-xl border border-amber-200/50 dark:border-amber-900/40">
                <AlertTriangle size={15} className="text-amber-500 shrink-0 mt-0.5" />
                <span>{sug}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Extracted Entities Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Extracted Skills */}
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white border-b border-slate-100 dark:border-slate-800 pb-3">
            Extracted Technical Competencies ({data?.extracted_skills.length})
          </h3>
          <div className="flex flex-wrap gap-2">
            {data?.extracted_skills.map((skill, i) => (
              <span key={i} className="px-3 py-1 bg-blue-50 dark:bg-blue-950/50 text-linkedin-blue dark:text-linkedin-accent border border-blue-200 dark:border-blue-800 rounded-full text-xs font-semibold">
                {skill}
              </span>
            ))}
          </div>
        </div>

        {/* Extracted Projects */}
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white border-b border-slate-100 dark:border-slate-800 pb-3">
            Extracted Projects ({data?.extracted_projects.length})
          </h3>
          <div className="space-y-3">
            {data?.extracted_projects.map((proj: any, i: number) => (
              <div key={i} className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700 text-xs space-y-1">
                <p className="font-bold text-slate-900 dark:text-white">{proj.title}</p>
                <p className="text-slate-500">{proj.description}</p>
                <div className="flex flex-wrap gap-1 pt-1">
                  {proj.tech_stack?.map((t: string, idx: number) => (
                    <span key={idx} className="px-2 py-0.5 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded text-[10px]">
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
