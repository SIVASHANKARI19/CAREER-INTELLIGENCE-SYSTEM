import React, { useEffect, useState } from 'react';
import { simulatorApi, shapApi, profileApi } from '../../api';
import { SimulatorSession, ShapExplanation } from '../../types';
import { PlayCircle, Zap, ArrowRight, ShieldAlert, Sparkles, RefreshCw } from 'lucide-react';
import { CircularScore } from '../../components/charts/CircularScore';
import { ShapWaterfall } from '../../components/charts/ShapWaterfall';

export const SimulatorPage: React.FC = () => {
  const [session, setSession] = useState<SimulatorSession | null>(null);
  const [shap, setShap] = useState<ShapExplanation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const availableActions = [
    { id: 'aws', label: 'AWS Certified Cloud Practitioner', category: 'certification' },
    { id: 'system_design', label: 'Completed End-to-End System Design Capstone', category: 'project' },
    { id: 'docker', label: 'Dockerized Microservices with CI/CD Workflow', category: 'skill' },
    { id: 'internship', label: '3-Month Software Engineering Internship', category: 'internship' },
    { id: 'ats_fix', label: 'Optimized Resume ATS Keywords to 90%', category: 'dsa' },
  ];

  const [selectedActionIds, setSelectedActionIds] = useState<string[]>(['aws', 'system_design']);

  const runSimulation = (actionIds: string[]) => {
    setLoading(true);
    setError(null);
    const applied_changes = availableActions
      .filter(a => actionIds.includes(a.id))
      .map(a => ({ action: a.label, category: a.category }));

    simulatorApi.simulate(applied_changes)
      .then(res => setSession(res))
      .catch(err => setError(err.response?.data?.detail || 'Simulation failed. Please try again.'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    runSimulation(selectedActionIds);
    profileApi.getProfile()
      .then(p => shapApi.getShapForStudent(p.id))
      .then(res => setShap(res))
      .catch(() => {});
  }, []);

  const toggleAction = (id: string) => {
    const updated = selectedActionIds.includes(id)
      ? selectedActionIds.filter(x => x !== id)
      : [...selectedActionIds, id];
    setSelectedActionIds(updated);
    runSimulation(updated);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-linkedin-blue/10 text-linkedin-blue rounded-xl">
            <PlayCircle size={24} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">What-If Career Simulator</h2>
            <p className="text-xs text-slate-500">Test how adding certifications or projects boosts your placement probability</p>
          </div>
        </div>
      </div>

      {/* Simulator Scenario Panel */}
      {error && <p className="text-sm text-red-500">{error}</p>}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Checkbox controls */}
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
            <Zap size={16} className="text-amber-500" /> Select Hypothetical Changes
          </h3>
          <div className="space-y-3">
            {availableActions.map((item) => {
              const checked = selectedActionIds.includes(item.id);
              return (
                <label
                  key={item.id}
                  className={`flex items-start gap-3 p-3 rounded-xl border text-xs font-medium cursor-pointer transition-colors ${
                    checked
                      ? 'bg-linkedin-blue/5 border-linkedin-blue text-slate-900 dark:text-white dark:bg-linkedin-blue/20'
                      : 'bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => toggleAction(item.id)}
                    className="mt-0.5 rounded text-linkedin-blue focus:ring-linkedin-blue"
                  />
                  <span>{item.label}</span>
                </label>
              );
            })}
          </div>
        </div>

        {/* Probability Comparison Output */}
        <div className="lg:col-span-2 bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between space-y-6">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white border-b border-slate-100 dark:border-slate-800 pb-3">
            Simulated Impact Result
          </h3>

          <div className="flex flex-col sm:flex-row items-center justify-around gap-6 my-auto">
            <CircularScore
              score={Math.round((session?.baseline_probability || 0.72) * 100)}
              label="Baseline"
              sublabel="Current Probability"
              color="#64748b"
              size={130}
            />

            <div className="flex flex-col items-center text-linkedin-blue font-bold">
              <ArrowRight size={28} className="rotate-90 sm:rotate-0" />
              <span className="text-xs mt-1 text-emerald-600 font-extrabold">+{((session?.delta || 0) * 100).toFixed(1)}%</span>
            </div>

            <CircularScore
              score={Math.round((session?.simulated_probability || 0.89) * 100)}
              label="Simulated"
              sublabel="Post-Action Probability"
              color="#059669"
              size={130}
            />
          </div>

          <div className="p-4 bg-emerald-50 dark:bg-emerald-950/30 rounded-xl border border-emerald-200 dark:border-emerald-800 text-xs text-emerald-800 dark:text-emerald-300 flex items-center gap-2">
            <Sparkles size={16} className="shrink-0" />
            <span>
              By completing these actions, your predicted placement probability increases from{' '}
              <strong>{Math.round((session?.baseline_probability || 0.72) * 100)}%</strong> to{' '}
              <strong>{Math.round((session?.simulated_probability || 0.89) * 100)}%</strong>!
            </span>
          </div>
        </div>
      </div>

      {/* SHAP Explainable AI Waterfall Component */}
      {shap && (
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-slate-900 dark:text-white border-b border-slate-100 dark:border-slate-800 pb-3">
            Explainable AI Feature Impact (SHAP Waterfall)
          </h3>
          <ShapWaterfall shapData={shap} />
        </div>
      )}
    </div>
  );
};