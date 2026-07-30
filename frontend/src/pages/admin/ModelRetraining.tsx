import React, { useEffect, useState } from 'react';
import { adminApi } from '../../api';
import { ModelRegistry } from '../../types';
import { Cpu, Play, CheckCircle2, Sparkles, RefreshCw } from 'lucide-react';

export const ModelRetraining: React.FC = () => {
  const [models, setModels] = useState<ModelRegistry[]>([]);
  const [loading, setLoading] = useState(true);
  const [retraining, setRetraining] = useState(false);
  const [retrainMsg, setRetrainMsg] = useState<string | null>(null);

  useEffect(() => {
    adminApi.getModelRegistry()
      .then(res => setModels(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleRetrain = () => {
    setRetraining(true);
    setRetrainMsg(null);
    adminApi.retrainModel()
      .then(res => {
        setRetrainMsg(`${res.message} Target model: ${res.new_version}`);
      })
      .catch(err => console.error(err))
      .finally(() => setRetraining(false));
  };

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-purple-100 dark:bg-purple-950/60 text-purple-600 rounded-xl">
            <Cpu size={24} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">ML Model Registry & Retraining Engine</h2>
            <p className="text-xs text-slate-500">Monitor XGBoost Classifier, DeBERTa NLP, and SHAP explainability models</p>
          </div>
        </div>

        <button
          onClick={handleRetrain}
          disabled={retraining}
          className="px-4 py-2.5 bg-linkedin-blue hover:bg-linkedin-hover text-white text-sm font-semibold rounded-lg shadow-sm flex items-center gap-2 transition-colors disabled:opacity-50"
        >
          <RefreshCw size={16} className={retraining ? 'animate-spin' : ''} />
          <span>{retraining ? 'Triggering...' : 'Trigger Model Retraining'}</span>
        </button>
      </div>

      {retrainMsg && (
        <div className="p-4 bg-purple-50 dark:bg-purple-950/40 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800 rounded-xl text-sm flex items-center gap-2">
          <Sparkles size={18} />
          <span>{retrainMsg}</span>
        </div>
      )}

      {/* Models Registry Table */}
      <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <h3 className="text-base font-bold text-slate-900 dark:text-white border-b border-slate-100 dark:border-slate-800 pb-3">
          Active Registered Models
        </h3>

        {loading ? (
          <div className="p-8 text-center text-slate-500">Loading model registry...</div>
        ) : (
          <div className="space-y-4">
            {models.map((m) => (
              <div key={m.id} className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div>
                    <h4 className="font-bold text-sm text-slate-900 dark:text-white">{m.model_name}</h4>
                    <p className="text-xs text-slate-400">Version: {m.version}</p>
                  </div>
                  <span className={`self-start sm:self-auto px-3 py-1 rounded-full text-xs font-bold ${
                    m.status === 'active' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300' : 'bg-amber-100 text-amber-700'
                  }`}>
                    ● {m.status.toUpperCase()}
                  </span>
                </div>

                {/* Metrics */}
                <div className="flex flex-wrap gap-4 pt-2 border-t border-slate-200/60 dark:border-slate-700/60 text-xs">
                  {Object.entries(m.metrics || {}).map(([key, val]) => (
                    <div key={key} className="bg-white dark:bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700">
                      <span className="text-slate-400 capitalize">{key.replace('_', ' ')}: </span>
                      <span className="font-bold text-slate-800 dark:text-slate-200">{String(val)}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
