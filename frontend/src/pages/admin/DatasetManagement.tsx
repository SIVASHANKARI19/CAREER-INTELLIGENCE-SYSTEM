import React from 'react';
import { Database, Upload, Download, CheckCircle2 } from 'lucide-react';

export const DatasetManagement: React.FC = () => {
  return (
    <div className="space-y-8">
      <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-linkedin-blue/10 text-linkedin-blue rounded-xl">
            <Database size={24} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">ML Dataset & Vector Store Management</h2>
            <p className="text-xs text-slate-500">Manage placement training corpus and historical batch datasets</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h3 className="font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Upload size={18} className="text-linkedin-blue" /> Import Placement Dataset (CSV / JSON)
          </h3>
          <p className="text-xs text-slate-500">Upload historical student placement data with features (CGPA, ATS score, GitHub commits, placement outcome).</p>
          <input type="file" accept=".csv,.json" className="block w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-blue-50 file:text-linkedin-blue" />
          <button className="w-full py-2 bg-linkedin-blue text-white text-xs font-semibold rounded-lg shadow-sm">
            Upload & Validate Dataset
          </button>
        </div>

        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h3 className="font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Download size={18} className="text-linkedin-blue" /> Export Synthesized Features
          </h3>
          <p className="text-xs text-slate-500">Export normalized feature matrix used by XGBoost and DeBERTa NER models.</p>
          <button className="w-full py-2 bg-slate-800 dark:bg-slate-700 text-white text-xs font-semibold rounded-lg shadow-sm">
            Download Clean Feature Matrix (.csv)
          </button>
        </div>
      </div>
    </div>
  );
};
