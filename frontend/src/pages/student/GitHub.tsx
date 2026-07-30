import React, { useEffect, useState } from 'react';
import { githubApi } from '../../api';
import { GithubAnalysis } from '../../types';
import { Github as GithubIcon, Star, GitFork, GitCommit, ShieldCheck, Code } from 'lucide-react';
import { CircularScore } from '../../components/charts/CircularScore';
import { ProgressBar } from '../../components/charts/ProgressBar';

export const GitHubPage: React.FC = () => {
  const [data, setData] = useState<GithubAnalysis | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    githubApi.getAnalysis(1)
      .then(res => setData(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8 text-center text-slate-500">Auditing GitHub repositories & commit history...</div>;

  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-purple-100 dark:bg-purple-950/60 text-purple-600 rounded-xl">
            <GithubIcon size={24} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">GitHub Engineering Audit</h2>
            <p className="text-xs text-slate-500">Code quality, commit density, & skill confidence validation</p>
          </div>
        </div>
        <div className="text-right">
          <span className="text-xs text-slate-400 font-medium">Total Commits</span>
          <p className="text-2xl font-bold text-purple-600 flex items-center gap-1 justify-end">
            <GitCommit size={20} /> {data?.total_commits}
          </p>
        </div>
      </div>

      {/* Scores Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-around">
          <CircularScore score={data?.github_score || 82} label="GitHub Score" sublabel="Overall Repo Health" color="#9333ea" />
          <CircularScore score={data?.project_quality_score || 85} label="Code Quality" sublabel="Architecture & README" color="#059669" />
        </div>

        {/* Skill Confidence Confidence Map */}
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
            <ShieldCheck className="text-purple-600" size={16} /> Code Confidence Matrix
          </h3>
          <div className="space-y-3">
            {data?.skill_confidence && Object.entries(data.skill_confidence).map(([skill, conf]) => (
              <ProgressBar key={skill} value={Math.round(conf * 100)} label={skill} color="bg-purple-600" />
            ))}
          </div>
        </div>
      </div>

      {/* Repositories List */}
      <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <h3 className="text-base font-bold text-slate-900 dark:text-white border-b border-slate-100 dark:border-slate-800 pb-3">
          Audited Repositories ({data?.repositories.length})
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {data?.repositories.map((repo: any, idx: number) => (
            <div key={idx} className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700 space-y-3 flex flex-col justify-between">
              <div>
                <h4 className="font-bold text-sm text-slate-900 dark:text-white truncate">{repo.name}</h4>
                <p className="text-xs text-slate-500 mt-1 line-clamp-2">{repo.description}</p>
              </div>

              <div className="space-y-2 border-t border-slate-200/60 dark:border-slate-700/60 pt-2 text-xs">
                <div className="flex items-center justify-between text-slate-500">
                  <span className="flex items-center gap-1"><Star size={12} /> {repo.stars} stars</span>
                  <span className="flex items-center gap-1"><GitFork size={12} /> {repo.forks} forks</span>
                  <span className="flex items-center gap-1"><GitCommit size={12} /> {repo.commits}</span>
                </div>
                <p className="text-[11px] text-emerald-600 dark:text-emerald-400 font-medium">{repo.readme_quality}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
