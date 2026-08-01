import React, { useEffect, useState } from 'react';
import { fusionApi, profileApi } from '../../api';
import { FusionResult } from '../../types';
import { Network, CheckCircle2, Eye, AlertOctagon, Sparkles, ShieldCheck, RefreshCw } from 'lucide-react';
import { CircularScore } from '../../components/charts/CircularScore';

export const FusionPage: React.FC = () => {
  const [profileId, setProfileId] = useState<number | null>(null);
  const [data, setData] = useState<FusionResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    profileApi.getProfile()
      .then(p => {
        setProfileId(p.id);
        return fusionApi.getFusion(p.id);
      })
      .then(res => setData(res))
      .catch(() => {
        // No fusion result yet is expected on first visit — not a real error.
        setData(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleRunFusion = () => {
    setError(null);
    setRunning(true);
    fusionApi.runFusion()
      .then(res => setData(res))
      .catch(err => setError(err.response?.data?.detail || 'Fusion failed. Run Resume, GitHub, or LinkedIn analysis first.'))
      .finally(() => setRunning(false));
  };

  if (loading) return <div className="p-8 text-center text-slate-500">Triangulating data from Resume, GitHub, and LinkedIn...</div>;

  if (!data) {
    return (
      <div className="bg-white dark:bg-[#242B31] p-10 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm text-center space-y-4">
        <Network className="mx-auto text-emerald-600" size={32} />
        <h2 className="text-lg font-bold text-slate-900 dark:text-white">No fusion result yet</h2>
        <p className="text-sm text-slate-500">Run fusion to cross-check your Resume, GitHub, and LinkedIn data for verified and hidden skills.</p>
        {error && <p className="text-sm text-red-500">{error}</p>}
        <button
          onClick={handleRunFusion}
          disabled={running}
          className="px-4 py-2 bg-linkedin-blue hover:bg-linkedin-hover text-white text-sm font-semibold rounded-lg shadow-sm inline-flex items-center gap-2 disabled:opacity-60"
        >
          <RefreshCw size={16} className={running ? 'animate-spin' : ''} />
          {running ? 'Fusing...' : 'Run Fusion'}
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 rounded-xl">
            <Network size={24} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">Multi-Source Triangulation & Fusion Engine</h2>
            <p className="text-xs text-slate-500">Cross-analyzes claims across Resume, GitHub code, and LinkedIn profile</p>
          </div>
        </div>
        <button
          onClick={handleRunFusion}
          disabled={running}
          className="px-3 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold rounded-lg flex items-center gap-2 disabled:opacity-60"
        >
          <RefreshCw size={14} className={running ? 'animate-spin' : ''} />
          {running ? 'Re-fusing...' : 'Re-run Fusion'}
        </button>
      </div>
      {error && <p className="text-sm text-red-500">{error}</p>}

      {/* Main Credibility Score */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col items-center justify-center">
          <CircularScore score={data?.resume_credibility_score || 88} label="Credibility" sublabel="Cross-Source Authenticity" color="#059669" />
        </div>

        <div className="md:col-span-2 bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
            <Sparkles className="text-emerald-500" size={16} /> Triangulation Recommendations
          </h3>
          <ul className="space-y-2.5">
            {data?.suggestions.map((sug, i) => (
              <li key={i} className="flex items-start gap-2 text-xs text-slate-700 dark:text-slate-300 bg-emerald-50/50 dark:bg-emerald-950/20 p-3 rounded-xl border border-emerald-200/50 dark:border-emerald-900/40">
                <CheckCircle2 size={15} className="text-emerald-500 shrink-0 mt-0.5" />
                <span>{sug}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* 3 Categories: Verified, Hidden, Unsupported */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Verified Skills */}
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-emerald-600 dark:text-emerald-400 flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
            <CheckCircle2 size={16} /> Verified Skills (≥2 Sources)
          </h3>
          <div className="flex flex-wrap gap-2">
            {data?.verified_skills.map((s, i) => (
              <span key={i} className="px-3 py-1 bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 rounded-full text-xs font-semibold">
                ✓ {s}
              </span>
            ))}
          </div>
        </div>

        {/* Hidden Skills */}
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-blue-600 dark:text-blue-400 flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
            <Eye size={16} /> Hidden Skills (Not on Resume)
          </h3>
          <div className="flex flex-wrap gap-2">
            {data?.hidden_skills.map((s, i) => (
              <span key={i} className="px-3 py-1 bg-blue-50 dark:bg-blue-950/50 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800 rounded-full text-xs font-semibold">
                + Add {s}
              </span>
            ))}
          </div>
        </div>

        {/* Unsupported Claims */}
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-rose-600 dark:text-rose-400 flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
            <AlertOctagon size={16} /> Unsupported Resume Claims
          </h3>
          <div className="flex flex-wrap gap-2">
            {data?.unsupported_claims.map((s, i) => (
              <span key={i} className="px-3 py-1 bg-rose-50 dark:bg-rose-950/50 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800 rounded-full text-xs font-semibold">
                ⚠️ {s}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};