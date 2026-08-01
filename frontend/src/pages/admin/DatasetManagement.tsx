import React, { useEffect, useRef, useState } from 'react';
import { adminApi } from '../../api';
import { Database, Upload, CheckCircle2, RefreshCw, AlertCircle } from 'lucide-react';

export const DatasetManagement: React.FC = () => {
  const [info, setInfo] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchInfo = () => {
    setLoading(true);
    adminApi.getDatasetInfo()
      .then(res => setInfo(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchInfo();
  }, []);

  const handleUpload = () => {
    const file = fileInputRef.current?.files?.[0];
    if (!file) {
      setMessage({ type: 'error', text: 'Choose a CSV file first.' });
      return;
    }
    setUploading(true);
    setMessage(null);
    adminApi.uploadDataset(file)
      .then(res => {
        setMessage({ type: 'success', text: res.message || 'Dataset uploaded successfully.' });
        fetchInfo();
      })
      .catch(err => {
        setMessage({ type: 'error', text: err.response?.data?.detail || 'Upload failed.' });
      })
      .finally(() => setUploading(false));
  };

  return (
    <div className="space-y-8">
      <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-linkedin-blue/10 text-linkedin-blue rounded-xl">
            <Database size={24} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">Placement Dataset Management</h2>
            <p className="text-xs text-slate-500">Manage the labeled dataset used to train the placement prediction model</p>
          </div>
        </div>
      </div>

      {/* Current Dataset Info */}
      <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <h3 className="font-bold text-slate-900 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
          Active Training Dataset
        </h3>
        {loading ? (
          <p className="text-sm text-slate-500">Loading dataset info...</p>
        ) : info ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-xs text-slate-400 block">Source</span>
              <span className={`font-bold ${info.source === 'uploaded' ? 'text-emerald-600' : 'text-amber-600'}`}>
                {info.source === 'uploaded' ? 'Real (uploaded)' : 'Synthetic (placeholder)'}
              </span>
            </div>
            <div>
              <span className="text-xs text-slate-400 block">Rows</span>
              <span className="font-bold text-slate-800 dark:text-slate-200">{info.row_count}</span>
            </div>
            <div>
              <span className="text-xs text-slate-400 block">Placed ratio</span>
              <span className="font-bold text-slate-800 dark:text-slate-200">
                {info.positive_class_ratio != null ? `${(info.positive_class_ratio * 100).toFixed(1)}%` : '—'}
              </span>
            </div>
            <div>
              <span className="text-xs text-slate-400 block">Columns</span>
              <span className="font-bold text-slate-800 dark:text-slate-200">{info.columns?.length}</span>
            </div>
          </div>
        ) : null}
        {info?.source === 'synthetic' && (
          <p className="text-xs text-amber-600 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 rounded-lg p-3">
            No real placement records have been uploaded yet. The model is currently trained on a synthetic dataset for demonstration purposes.
          </p>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h3 className="font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Upload size={18} className="text-linkedin-blue" /> Import Real Placement Dataset (CSV)
          </h3>
          <p className="text-xs text-slate-500">
            Required columns: cgpa, ats_score, github_score, project_quality_score, resume_credibility_score,
            verified_skills_count, hidden_skills_count, unsupported_claims_count, projects_count,
            certifications_count, internships_count, programming_languages_count, total_commits, placed (0/1).
          </p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            className="block w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-blue-50 file:text-linkedin-blue"
          />
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="w-full py-2 bg-linkedin-blue hover:bg-linkedin-hover text-white text-xs font-semibold rounded-lg shadow-sm flex items-center justify-center gap-2 disabled:opacity-60"
          >
            <RefreshCw size={14} className={uploading ? 'animate-spin' : ''} />
            {uploading ? 'Validating & Uploading...' : 'Upload & Validate Dataset'}
          </button>
          {message && (
            <p className={`text-xs flex items-center gap-1.5 ${message.type === 'success' ? 'text-emerald-600' : 'text-red-500'}`}>
              {message.type === 'success' ? <CheckCircle2 size={14} /> : <AlertCircle size={14} />}
              {message.text}
            </p>
          )}
        </div>

        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h3 className="font-bold text-slate-900 dark:text-white flex items-center gap-2">
            Next Step
          </h3>
          <p className="text-xs text-slate-500">
            After uploading a new dataset, go to <strong>Model Retraining</strong> and trigger a retrain —
            it will pick up whichever dataset is active here (uploaded, or synthetic if none was uploaded).
          </p>
        </div>
      </div>
    </div>
  );
};