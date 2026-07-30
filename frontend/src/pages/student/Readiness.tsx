import React, { useEffect, useState } from 'react';
import { readinessApi } from '../../api';
import { ReadinessScore } from '../../types';
import { ReadinessRadarChart } from '../../components/charts/RadarChart';
import { CircularScore } from '../../components/charts/CircularScore';
import { ProgressBar } from '../../components/charts/ProgressBar';
import { Award, Code, MessageSquare, FileText, FolderGit2, Github, Users } from 'lucide-react';

export const ReadinessPage: React.FC = () => {
  const [data, setData] = useState<ReadinessScore | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    readinessApi.getReadiness(1)
      .then(res => setData(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading || !data) return <div className="p-8 text-center text-slate-500">Computing 7-dimension placement readiness metrics...</div>;

  const dimensions = [
    { label: 'Technical Competency', score: data.technical_readiness, icon: Code, color: 'bg-blue-600' },
    { label: 'Communication & Soft Skills', score: data.communication_readiness, icon: MessageSquare, color: 'bg-emerald-600' },
    { label: 'Resume ATS Quality', score: data.resume_readiness, icon: FileText, color: 'bg-amber-600' },
    { label: 'Project Depth', score: data.project_readiness, icon: FolderGit2, color: 'bg-indigo-600' },
    { label: 'GitHub Activity', score: data.github_readiness, icon: Github, color: 'bg-purple-600' },
    { label: 'Interview Readiness', score: data.interview_readiness, icon: Users, color: 'bg-rose-600' },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-linkedin-blue/10 text-linkedin-blue rounded-xl">
            <Award size={24} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">7-Dimensional Placement Readiness Breakdown</h2>
            <p className="text-xs text-slate-500">Holistic assessment matrix for career positioning</p>
          </div>
        </div>
      </div>

      {/* Radar Chart & Overall Score */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col items-center justify-center">
          <CircularScore score={data.overall_readiness} label="Overall Index" sublabel="Placement Readiness" color="#0A66C2" size={160} />
        </div>

        <div className="lg:col-span-2 bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col items-center justify-center">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white mb-2 self-start">
            Readiness Radar Polygon
          </h3>
          <ReadinessRadarChart data={data} />
        </div>
      </div>

      {/* 6 Dimension Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {dimensions.map((dim, i) => {
          const Icon = dim.icon;
          return (
            <div key={i} className="bg-white dark:bg-[#242B31] p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500 uppercase">{dim.label}</span>
                <Icon size={18} className="text-slate-400" />
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold text-slate-900 dark:text-white">{dim.score}%</span>
              </div>
              <ProgressBar value={dim.score} color={dim.color} />
            </div>
          );
        })}
      </div>
    </div>
  );
};
