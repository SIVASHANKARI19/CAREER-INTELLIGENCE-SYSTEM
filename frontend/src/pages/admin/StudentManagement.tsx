import React, { useEffect, useState } from 'react';
import { adminApi } from '../../api';
import { StudentProfile } from '../../types';
import { Users, Search, ChevronRight } from 'lucide-react';

export const StudentManagement: React.FC = () => {
  const [students, setStudents] = useState<StudentProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    adminApi.getStudents()
      .then(res => setStudents(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const filtered = students.filter(s =>
    (s.full_name || '').toLowerCase().includes(search.toLowerCase()) ||
    (s.department || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-8">
      {/* Header & Search */}
      <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">Student Directory & Profiles</h2>
          <p className="text-xs text-slate-500">Filter, inspect, and monitor student readiness scores</p>
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Filter by name or department..."
            className="w-full pl-9 pr-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm focus:outline-none"
          />
        </div>
      </div>

      {/* Table */}
      <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        {loading ? (
          <div className="p-8 text-center text-slate-500">Loading student directory...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-700 text-xs font-semibold uppercase text-slate-400">
                  <th className="pb-3">Student Name</th>
                  <th className="pb-3">Department</th>
                  <th className="pb-3">CGPA</th>
                  <th className="pb-3">Career Goal</th>
                  <th className="pb-3">Profile %</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {filtered.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40">
                    <td className="py-3 font-semibold text-slate-900 dark:text-white">{s.full_name || `Student #${s.id}`}</td>
                    <td className="py-3 text-slate-500">{s.department || 'CSE'}</td>
                    <td className="py-3 font-semibold text-linkedin-blue">{s.cgpa || 8.5}</td>
                    <td className="py-3 text-slate-500">{s.career_goal || 'SDE'}</td>
                    <td className="py-3">
                      <span className="px-2.5 py-0.5 bg-blue-100 dark:bg-blue-950 text-linkedin-blue rounded-full text-xs font-bold">
                        {s.profile_completion_pct}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
