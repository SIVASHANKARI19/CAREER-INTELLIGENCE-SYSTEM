import React, { useEffect, useState } from 'react';
import { dashboardApi } from '../../api';
import { CircularScore } from '../../components/charts/CircularScore';
import { ProgressBar } from '../../components/charts/ProgressBar';
import { Award, FileText, Github, Target, Activity, ArrowUpRight, CheckCircle2 } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Dashboard: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardApi.getSummary()
      .then(res => setData(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-500">
        Loading intelligence metrics...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
            Welcome back, {data?.full_name || 'Student'}! 👋
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Target Career Goal: <span className="font-semibold text-linkedin-blue">{data?.career_goal}</span>
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/simulator"
            className="px-4 py-2 bg-linkedin-blue hover:bg-linkedin-hover text-white text-sm font-semibold rounded-lg shadow-sm flex items-center gap-2 transition-colors"
          >
            <span>Run Career Simulator</span>
            <ArrowUpRight size={16} />
          </Link>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Overall Readiness */}
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 flex flex-col items-center justify-center">
          <CircularScore score={data?.overall_readiness || 84} label="Readiness" sublabel="Placement Index" color="#0A66C2" />
        </div>

        {/* ATS Score Card */}
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase text-slate-400">ATS Resume</span>
            <div className="p-2 bg-blue-50 dark:bg-blue-950/40 text-linkedin-blue rounded-lg">
              <FileText size={20} />
            </div>
          </div>
          <div className="my-3">
            <span className="text-3xl font-bold text-slate-900 dark:text-white">{data?.ats_score}%</span>
            <p className="text-xs text-emerald-600 font-semibold mt-0.5">High Compatibility</p>
          </div>
          <ProgressBar value={data?.ats_score || 85} color="bg-blue-600" />
        </div>

        {/* GitHub Audit Card */}
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase text-slate-400">GitHub Code Audit</span>
            <div className="p-2 bg-purple-50 dark:bg-purple-950/40 text-purple-600 rounded-lg">
              <Github size={20} />
            </div>
          </div>
          <div className="my-3">
            <span className="text-3xl font-bold text-slate-900 dark:text-white">{data?.github_score}%</span>
            <p className="text-xs text-purple-600 font-semibold mt-0.5">Strong Activity</p>
          </div>
          <ProgressBar value={data?.github_score || 82} color="bg-purple-600" />
        </div>

        {/* Skill Gap Count */}
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase text-slate-400">Skill Gaps Identified</span>
            <div className="p-2 bg-amber-50 dark:bg-amber-950/40 text-amber-600 rounded-lg">
              <Target size={20} />
            </div>
          </div>
          <div className="my-3">
            <span className="text-3xl font-bold text-slate-900 dark:text-white">{data?.skill_gap_count}</span>
            <p className="text-xs text-amber-600 font-semibold mt-0.5">Actionable Targets</p>
          </div>
          <Link to="/skill-gap" className="text-xs font-semibold text-linkedin-blue hover:underline">
            View Skill Gap Matrix →
          </Link>
        </div>
      </div>

      {/* Two Column Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Completion & Quick Actions */}
        <div className="lg:col-span-2 bg-white dark:bg-[#242B31] p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 space-y-6">
          <div className="flex justify-between items-center border-b border-slate-100 dark:border-slate-800 pb-4">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <CheckCircle2 className="text-linkedin-blue" size={20} />
              Profile Completion Status
            </h3>
            <span className="text-sm font-bold text-linkedin-blue">{data?.profile_completion}%</span>
          </div>

          <ProgressBar value={data?.profile_completion || 65} heightClass="h-3" />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
            <Link
              to="/resume"
              className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-linkedin-blue transition-colors flex items-center gap-3"
            >
              <div className="p-2.5 bg-blue-100 dark:bg-blue-900/50 text-linkedin-blue rounded-lg">
                <FileText size={20} />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">Upload New Resume</p>
                <p className="text-xs text-slate-500">PDF parse & ATS check</p>
              </div>
            </Link>

            <Link
              to="/fusion"
              className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-linkedin-blue transition-colors flex items-center gap-3"
            >
              <div className="p-2.5 bg-emerald-100 dark:bg-emerald-900/50 text-emerald-600 rounded-lg">
                <Award size={20} />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">Run Skill Fusion</p>
                <p className="text-xs text-slate-500">Triangulate resume vs GitHub</p>
              </div>
            </Link>
          </div>
        </div>

        {/* Recent Activity Log */}
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 space-y-4">
          <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-4">
            <Activity className="text-linkedin-blue" size={20} />
            Recent Activity
          </h3>
          <div className="space-y-3">
            {data?.recent_activity?.map((act: any) => (
              <div key={act.id} className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl text-xs space-y-1">
                <p className="font-semibold text-slate-800 dark:text-slate-200">{act.description}</p>
                <span className="text-slate-400">{act.time}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
