import React, { useEffect, useState } from 'react';
import { adminApi } from '../../api';
import { AdminAnalytics } from '../../types';
import { BarChart3, TrendingUp, AlertTriangle } from 'lucide-react';
import { ProgressBar } from '../../components/charts/ProgressBar';

export const Analytics: React.FC = () => {
  const [data, setData] = useState<AdminAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminApi.getAnalytics()
      .then(res => setData(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading || !data) return <div className="p-8 text-center text-slate-500">Generating aggregate placement analytics...</div>;

  return (
    <div className="space-y-8">
      <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-linkedin-blue/10 text-linkedin-blue rounded-xl">
            <BarChart3 size={24} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">Institutional Placement Cohort Analytics</h2>
            <p className="text-xs text-slate-500">Aggregate skill gaps, department trends, and placement readiness forecasting</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Top Missing Skills Across Cohort */}
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
            <AlertTriangle size={18} className="text-amber-500" /> Top Missing Skills Across Students
          </h3>
          <div className="space-y-3">
            {data.top_missing_skills.map((item, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-xs font-semibold text-slate-700 dark:text-slate-300">
                  <span>{item.skill}</span>
                  <span className="text-amber-600 font-bold">{item.count} Students Need This</span>
                </div>
                <ProgressBar value={item.count} max={data.total_students} color="bg-amber-500" />
              </div>
            ))}
          </div>
        </div>

        {/* Department Readiness Summary */}
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
            <TrendingUp size={18} className="text-linkedin-blue" /> Readiness Index by Department
          </h3>
          <div className="space-y-4">
            {data.department_stats.map((dept, idx) => (
              <div key={idx} className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl space-y-2">
                <div className="flex justify-between text-xs font-bold text-slate-900 dark:text-white">
                  <span>{dept.department}</span>
                  <span className="text-linkedin-blue">{dept.avg_readiness}%</span>
                </div>
                <ProgressBar value={dept.avg_readiness} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
