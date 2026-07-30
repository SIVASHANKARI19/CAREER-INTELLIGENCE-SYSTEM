import React, { useEffect, useState } from 'react';
import { adminApi } from '../../api';
import { AdminAnalytics } from '../../types';
import { ShieldCheck, Users, BarChart3, Cpu, Building2, Award } from 'lucide-react';
import { CircularScore } from '../../components/charts/CircularScore';
import { ProgressBar } from '../../components/charts/ProgressBar';

export const AdminDashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<AdminAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminApi.getAnalytics()
      .then(res => setAnalytics(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading || !analytics) return <div className="p-8 text-center text-slate-500">Loading admin cohort statistics...</div>;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-linkedin-blue/10 text-linkedin-blue rounded-xl">
            <ShieldCheck size={24} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">Admin Control & Placement Overview</h2>
            <p className="text-xs text-slate-500">Institutional analytics, student tracking, and model monitoring</p>
          </div>
        </div>
      </div>

      {/* Aggregate Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
          <span className="text-xs font-semibold uppercase text-slate-400">Total Enrolled Students</span>
          <div className="my-2">
            <span className="text-3xl font-bold text-slate-900 dark:text-white">{analytics.total_students}</span>
          </div>
          <p className="text-xs text-linkedin-blue font-semibold">Active Cohort Batch 2025</p>
        </div>

        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
          <span className="text-xs font-semibold uppercase text-slate-400">Avg Placement Probability</span>
          <div className="my-2">
            <span className="text-3xl font-bold text-emerald-600">{(analytics.avg_placement_probability * 100).toFixed(1)}%</span>
          </div>
          <ProgressBar value={analytics.avg_placement_probability * 100} color="bg-emerald-600" />
        </div>

        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
          <span className="text-xs font-semibold uppercase text-slate-400">Avg Resume ATS Score</span>
          <div className="my-2">
            <span className="text-3xl font-bold text-blue-600">{analytics.avg_ats_score}%</span>
          </div>
          <ProgressBar value={analytics.avg_ats_score} color="bg-blue-600" />
        </div>

        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
          <span className="text-xs font-semibold uppercase text-slate-400">Industry Ready Students</span>
          <div className="my-2">
            <span className="text-3xl font-bold text-purple-600">{analytics.industry_ready_count}</span>
          </div>
          <p className="text-xs text-purple-600 font-semibold">{(analytics.industry_ready_count / analytics.total_students * 100).toFixed(0)}% of cohort ready</p>
        </div>
      </div>

      {/* Department Breakdown */}
      <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <h3 className="text-base font-bold text-slate-900 dark:text-white border-b border-slate-100 dark:border-slate-800 pb-3">
          Department Performance Matrix
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {analytics.department_stats.map((dept, idx) => (
            <div key={idx} className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700 space-y-2">
              <h4 className="font-bold text-sm text-slate-900 dark:text-white">{dept.department}</h4>
              <div className="flex justify-between text-xs text-slate-500">
                <span>Students: {dept.students}</span>
                <span className="font-bold text-linkedin-blue">Avg Readiness: {dept.avg_readiness}%</span>
              </div>
              <ProgressBar value={dept.avg_readiness} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
