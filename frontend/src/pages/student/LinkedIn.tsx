import React, { useEffect, useState } from 'react';
import { linkedinApi } from '../../api';
import { LinkedinAnalysis } from '../../types';
import { Linkedin as LinkedinIcon, Briefcase, GraduationCap, Award, Sparkles } from 'lucide-react';

export const LinkedInPage: React.FC = () => {
  const [data, setData] = useState<LinkedinAnalysis | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    linkedinApi.getAnalysis(1)
      .then(res => setData(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8 text-center text-slate-500">Parsing LinkedIn PDF export...</div>;

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center gap-4">
        <div className="p-3 bg-blue-100 dark:bg-blue-950/60 text-linkedin-blue rounded-xl">
          <LinkedinIcon size={24} />
        </div>
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">LinkedIn Profile Intelligence</h2>
          <p className="text-xs text-slate-500">Parsed from exported LinkedIn PDF summary</p>
        </div>
      </div>

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
    </div>
  );
};
