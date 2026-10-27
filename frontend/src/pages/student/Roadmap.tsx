import React, { useEffect, useState } from 'react';
import { roadmapApi, profileApi } from '../../api';
import { LearningRoadmap } from '../../types';
import { Compass, Calendar, BookOpen, Rocket, ExternalLink, CheckCircle, RefreshCw } from 'lucide-react';

export const RoadmapPage: React.FC = () => {
  const [data, setData] = useState<LearningRoadmap | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    profileApi.getProfile()
      .then(p => roadmapApi.getRoadmap(p.id))
      .then(res => setData(res))
      .catch(() => {
        // No roadmap yet is expected on first visit — not a real error.
        setData(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleGenerate = () => {
    setError(null);
    setGenerating(true);
    roadmapApi.generate()
      .then(res => setData(res))
      .catch(err => setError(err.response?.data?.detail || 'Roadmap generation failed. Please try again.'))
      .finally(() => setGenerating(false));
  };

  if (loading) return <div className="p-8 text-center text-slate-500">Generating personalized AI learning roadmap...</div>;

  if (!data) {
    return (
      <div className="bg-white dark:bg-[#242B31] p-10 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm text-center space-y-4">
        <Compass className="mx-auto text-indigo-600" size={32} />
        <h2 className="text-lg font-bold text-slate-900 dark:text-white">No roadmap yet</h2>
        <p className="text-sm text-slate-500">Generate a personalized weekly/monthly learning roadmap based on your skill gaps and career goal.</p>
        {error && <p className="text-sm text-red-500">{error}</p>}
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="px-4 py-2 bg-linkedin-blue hover:bg-linkedin-hover text-white text-sm font-semibold rounded-lg shadow-sm inline-flex items-center gap-2 disabled:opacity-60"
        >
          <RefreshCw size={16} className={generating ? 'animate-spin' : ''} />
          {generating ? 'Generating...' : 'Generate Roadmap'}
        </button>
      </div>
    );
  }

  // Defensive fallbacks: the API may omit optional arrays, and we never want
  // a missing field to crash the page with a "map of undefined" error.
  const weeklyPlan = data.weekly_plan ?? [];
  const recommendedProjects = data.recommended_projects ?? [];
  const recommendedCourses = data.recommended_courses ?? [];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-indigo-100 dark:bg-indigo-950/60 text-indigo-600 rounded-xl">
            <Compass size={24} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">Personalized AI Learning Roadmap</h2>
            <p className="text-xs text-slate-500">Weekly structured milestone schedule to reach placement readiness</p>
          </div>
        </div>
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="px-3 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold rounded-lg flex items-center gap-2 disabled:opacity-60"
        >
          <RefreshCw size={14} className={generating ? 'animate-spin' : ''} />
          {generating ? 'Regenerating...' : 'Regenerate'}
        </button>
      </div>
      {error && <p className="text-sm text-red-500">{error}</p>}

      {/* Weekly Plan Timeline */}
      <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
        <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
          <Calendar size={18} className="text-linkedin-blue" /> {weeklyPlan.length}-Week Mastery Schedule
        </h3>

        {weeklyPlan.length === 0 ? (
          <p className="text-sm text-slate-500">No weekly plan available yet. Try regenerating the roadmap.</p>
        ) : (
          <div className="space-y-6 border-l-2 border-slate-200 dark:border-slate-700 pl-4 ml-2">
            {weeklyPlan.map((item: any, idx: number) => (
              <div key={idx} className="relative space-y-2">
                <div className="absolute -left-[25px] top-1 w-4 h-4 rounded-full bg-linkedin-blue border-2 border-white dark:border-[#242B31]" />
                <div className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700 space-y-2">
                  <span className="text-xs font-bold text-linkedin-blue uppercase tracking-wider">Week {item.week}</span>
                  <h4 className="font-bold text-sm text-slate-900 dark:text-white">{item.focus}</h4>
                  <ul className="space-y-1 text-xs text-slate-600 dark:text-slate-300">
                    {(item.tasks ?? []).map((t: string, tidx: number) => (
                      <li key={tidx} className="flex items-center gap-2">
                        <CheckCircle size={12} className="text-emerald-500 shrink-0" />
                        <span>{t}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Recommended Projects & Courses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Recommended Capstone Projects */}
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
            <Rocket size={16} className="text-indigo-600" /> Recommended Capstone Projects
          </h3>
          {recommendedProjects.length === 0 ? (
            <p className="text-xs text-slate-500">No project recommendations yet.</p>
          ) : (
            <div className="space-y-3">
              {recommendedProjects.map((p: any, i: number) => (
                <div key={i} className="p-3.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700 text-xs space-y-1.5">
                  <span className="font-bold text-slate-900 dark:text-white">{p.title}</span>
                  <p className="text-slate-500">{p.description}</p>
                  <div className="flex flex-wrap gap-1 pt-1">
                    {(p.skills_practiced ?? []).map((t: string, idx: number) => (
                      <span key={idx} className="px-2 py-0.5 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded text-[10px]">
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recommended Courses */}
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
            <BookOpen size={16} className="text-indigo-600" /> Curated Courses & Guides
          </h3>
          {recommendedCourses.length === 0 ? (
            <p className="text-xs text-slate-500">No course recommendations yet.</p>
          ) : (
            <div className="space-y-3">
              {recommendedCourses.map((c: any, i: number) => {
                // The API doesn't send a direct link for courses, so build a
                // best-effort search URL rather than rendering a dead <a>.
                const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(`${c.title} ${c.platform}`)}`;
                return (
                  <a
                    key={i}
                    href={searchUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="p-3.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700 text-xs space-y-1 block hover:border-linkedin-blue transition-colors"
                  >
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-slate-900 dark:text-white">{c.title}</span>
                      <ExternalLink size={14} className="text-slate-400" />
                    </div>
                    <p className="text-slate-400">Platform: {c.platform}{c.skill ? ` · ${c.skill}` : ''}</p>
                  </a>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};