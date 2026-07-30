import React, { useEffect, useState } from 'react';
import { skillGapApi } from '../../api';
import { SkillGapResult } from '../../types';
import { Target, CheckCircle2, Clock, AlertCircle, Search } from 'lucide-react';

export const SkillGapPage: React.FC = () => {
  const [data, setData] = useState<SkillGapResult | null>(null);
  const [targetRole, setTargetRole] = useState('SDE');
  const [loading, setLoading] = useState(true);

  const fetchSkillGap = (role: string) => {
    setLoading(true);
    skillGapApi.analyze(role)
      .then(res => setData(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchSkillGap(targetRole);
  }, []);

  const handleRoleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchSkillGap(targetRole);
  };

  return (
    <div className="space-y-8">
      {/* Header & Target Role Selector */}
      <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-amber-100 dark:bg-amber-950/60 text-amber-600 rounded-xl">
            <Target size={24} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">Target Role Skill Gap Matrix</h2>
            <p className="text-xs text-slate-500">Benchmark your current skill profile against industry requirements</p>
          </div>
        </div>

        <form onSubmit={handleRoleSubmit} className="flex items-center gap-2 w-full md:w-auto">
          <input
            type="text"
            value={targetRole}
            onChange={e => setTargetRole(e.target.value)}
            placeholder="Target role e.g. SDE, AI Engineer"
            className="px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm focus:ring-2 focus:ring-linkedin-blue focus:outline-none"
          />
          <button
            type="submit"
            className="px-4 py-2 bg-linkedin-blue hover:bg-linkedin-hover text-white text-sm font-semibold rounded-lg shadow-sm flex items-center gap-1 transition-colors"
          >
            <Search size={16} />
            <span>Analyze</span>
          </button>
        </form>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500">Comparing skill graph against target role requirements...</div>
      ) : (
        <div className="space-y-6">
          {/* Matched vs Missing Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Matched Skills */}
            <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
              <h3 className="text-base font-bold text-emerald-600 dark:text-emerald-400 flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
                <CheckCircle2 size={18} /> Matched Competencies ({data?.matched_skills.length})
              </h3>
              <div className="flex flex-wrap gap-2">
                {data?.matched_skills.map((skill, i) => (
                  <span key={i} className="px-3 py-1.5 bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 rounded-lg text-xs font-semibold">
                    ✓ {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* Missing Skills */}
            <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
              <h3 className="text-base font-bold text-rose-600 dark:text-rose-400 flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
                <AlertCircle size={18} /> Missing Target Skills ({data?.missing_skills.length})
              </h3>
              <div className="flex flex-wrap gap-2">
                {data?.missing_skills.map((skill, i) => (
                  <span key={i} className="px-3 py-1.5 bg-rose-50 dark:bg-rose-950/50 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800 rounded-lg text-xs font-semibold">
                    ! {skill}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Priority Map & Estimated Learning Time Table */}
          <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
            <h3 className="text-base font-bold text-slate-900 dark:text-white border-b border-slate-100 dark:border-slate-800 pb-3">
              Action Plan Priority Matrix
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-slate-700 text-xs font-semibold uppercase text-slate-400">
                    <th className="pb-3">Target Skill</th>
                    <th className="pb-3">Priority Level</th>
                    <th className="pb-3">Est. Time to Bridge</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {data?.missing_skills.map((skill, idx) => {
                    const priority = data.priority_map[skill] || 'Medium';
                    const estTime = data.estimated_learning_time[skill] || '2 weeks';
                    return (
                      <tr key={idx} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40">
                        <td className="py-3 font-semibold text-slate-900 dark:text-white">{skill}</td>
                        <td className="py-3">
                          <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                            priority === 'High'
                              ? 'bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-400'
                              : priority === 'Medium'
                              ? 'bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-400'
                              : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300'
                          }`}>
                            {priority}
                          </span>
                        </td>
                        <td className="py-3 text-slate-500 dark:text-slate-400 flex items-center gap-1">
                          <Clock size={14} /> {estTime}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
