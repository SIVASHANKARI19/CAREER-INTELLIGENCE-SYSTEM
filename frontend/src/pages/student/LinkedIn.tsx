import React, { useEffect, useState } from 'react';
import { linkedinApi, profileApi } from '../../api';
import { LinkedinAnalysis, StudentProfile } from '../../types';
import { Linkedin as LinkedinIcon, Briefcase, GraduationCap, Award, Sparkles, RefreshCw } from 'lucide-react';

export const LinkedInPage: React.FC = () => {
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [data, setData] = useState<LinkedinAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    profileApi.getProfile()
      .then(p => {
        setProfile(p);
        return linkedinApi.getAnalysis(p.id);
      })
      .then(res => setData(res))
      .catch(() => {
        // No analysis yet is expected on first visit — not a real error.
        setData(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleRunAnalyze = () => {
    if (!profile?.linkedin_pdf_path) {
      setError('Upload your LinkedIn PDF export in your profile before running analysis.');
      return;
    }
    setError(null);
    setAnalyzing(true);
    linkedinApi.analyze(profile.id)
      .then(res => setData(res))
      .catch(err => setError(err.response?.data?.detail || 'LinkedIn analysis failed. Please try again.'))
      .finally(() => setAnalyzing(false));
  };

  if (loading) return <div className="p-8 text-center text-slate-500">Parsing LinkedIn PDF export...</div>;

  if (!data) {
    return (
      <div className="bg-white dark:bg-[#242B31] p-10 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm text-center space-y-4">
        <LinkedinIcon className="mx-auto text-linkedin-blue" size={32} />
        <h2 className="text-lg font-bold text-slate-900 dark:text-white">No LinkedIn analysis yet</h2>
        <p className="text-sm text-slate-500">Run analysis to extract your headline, experience, education, and skills from your uploaded PDF.</p>
        {error && <p className="text-sm text-red-500">{error}</p>}
        <button
          onClick={handleRunAnalyze}
          disabled={analyzing}
          className="px-4 py-2 bg-linkedin-blue hover:bg-linkedin-hover text-white text-sm font-semibold rounded-lg shadow-sm inline-flex items-center gap-2 disabled:opacity-60"
        >
          <RefreshCw size={16} className={analyzing ? 'animate-spin' : ''} />
          {analyzing ? 'Analyzing...' : 'Run LinkedIn Analysis'}
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-blue-100 dark:bg-blue-950/60 text-linkedin-blue rounded-xl">
            <LinkedinIcon size={24} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">LinkedIn Profile Intelligence</h2>
            <p className="text-xs text-slate-500">Parsed from exported LinkedIn PDF summary</p>
          </div>
        </div>
        <button
          onClick={handleRunAnalyze}
          disabled={analyzing}
          className="px-3 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold rounded-lg flex items-center gap-2 disabled:opacity-60"
        >
          <RefreshCw size={14} className={analyzing ? 'animate-spin' : ''} />
          {analyzing ? 'Re-analyzing...' : 'Re-analyze'}
        </button>
      </div>
      {error && <p className="text-sm text-red-500">{error}</p>}

      {/* Headline & Summary */}
      <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <h3 className="text-sm font-bold text-slate-900 dark:text-white border-b border-slate-100 dark:border-slate-800 pb-3">
          Professional Headline & Summary
        </h3>
        <div className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl space-y-2">
          <p className="text-sm font-bold text-linkedin-blue">{data?.headline}</p>
          <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">{data?.summary}</p>
        </div>
      </div>

      {/* Grid for Skills & Experience */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Extracted Skills */}
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
            <Sparkles size={16} className="text-linkedin-blue" /> Endorsed Skills ({data?.extracted_skills.length})
          </h3>
          <div className="flex flex-wrap gap-2">
            {data?.extracted_skills.map((skill, i) => (
              <span key={i} className="px-3 py-1 bg-blue-50 dark:bg-blue-950/50 text-linkedin-blue dark:text-linkedin-accent border border-blue-200 dark:border-blue-800 rounded-full text-xs font-semibold">
                {skill}
              </span>
            ))}
          </div>
        </div>

        {/* Extracted Experience */}
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
            <Briefcase size={16} className="text-linkedin-blue" /> Work Experience
          </h3>
          <div className="space-y-3">
            {data?.extracted_experience.map((exp: any, i: number) => (
              <div key={i} className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700 text-xs space-y-1">
                <p className="font-bold text-slate-900 dark:text-white">{exp.title} - {exp.company}</p>
                <p className="text-slate-400">{exp.duration} ({exp.location})</p>
                <p className="text-slate-600 dark:text-slate-300 mt-1">{exp.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Extracted Posts */}
      {data?.extracted_posts && data.extracted_posts.length > 0 && (
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
            <Sparkles size={16} className="text-linkedin-blue" /> Recent Posts ({data.extracted_posts.length})
          </h3>
          <div className="space-y-3">
            {data.extracted_posts.map((post: any, i: number) => (
              <div key={i} className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700 text-xs space-y-2">
                <p className="text-slate-700 dark:text-slate-200 leading-relaxed">{post.content}</p>
                <div className="flex items-center justify-between text-slate-400">
                  <span>{post.posted}</span>
                  <span>
                    {post.reactions_count != null ? `${post.reactions_count} reactions` : ''}
                    {post.comments_count != null ? ` · ${post.comments_count} comments` : ''}
                  </span>
                </div>
                {post.mentioned_skills?.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {post.mentioned_skills.map((s: string, j: number) => (
                      <span key={j} className="px-2 py-0.5 bg-blue-50 dark:bg-blue-950/50 text-linkedin-blue dark:text-linkedin-accent border border-blue-200 dark:border-blue-800 rounded-full text-[10px] font-semibold">
                        {s}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};