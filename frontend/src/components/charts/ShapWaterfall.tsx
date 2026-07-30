import React from 'react';
import { ShapExplanation } from '../../types';
import { TrendingUp, TrendingDown, HelpCircle } from 'lucide-react';

interface ShapWaterfallProps {
  shapData: ShapExplanation;
}

export const ShapWaterfall: React.FC<ShapWaterfallProps> = ({ shapData }) => {
  return (
    <div className="space-y-6">
      {/* Base vs Output summary banner */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 bg-slate-50 dark:bg-slate-800/60 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
        <div className="p-3 bg-white dark:bg-slate-800 rounded-lg shadow-sm">
          <p className="text-xs text-slate-500 dark:text-slate-400">Base Expected Value</p>
          <p className="text-xl font-bold text-slate-700 dark:text-slate-200">
            {(shapData.base_value * 100).toFixed(1)}%
          </p>
        </div>
        <div className="p-3 bg-white dark:bg-slate-800 rounded-lg shadow-sm">
          <p className="text-xs text-slate-500 dark:text-slate-400">Model Final Output</p>
          <p className="text-xl font-bold text-linkedin-blue">
            {(shapData.output_value * 100).toFixed(1)}%
          </p>
        </div>
        <div className="p-3 bg-white dark:bg-slate-800 rounded-lg shadow-sm">
          <p className="text-xs text-slate-500 dark:text-slate-400">Net Feature Impact</p>
          <p className={`text-xl font-bold ${shapData.output_value >= shapData.base_value ? 'text-emerald-600' : 'text-rose-600'}`}>
            {shapData.output_value >= shapData.base_value ? '+' : ''}{((shapData.output_value - shapData.base_value) * 100).toFixed(1)}%
          </p>
        </div>
      </div>

      {/* Feature Waterfall Bars */}
      <div className="space-y-4">
        <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-2">
          <span>Feature Impact Breakdown (SHAP Values)</span>
          <span className="text-xs font-normal text-slate-500 dark:text-slate-400">(XAI Transparency)</span>
        </h4>

        {/* Positive Features */}
        <div>
          <h5 className="text-xs font-semibold text-emerald-700 dark:text-emerald-400 mb-2 flex items-center gap-1">
            <TrendingUp size={14} /> Positive Contribution (+ Boost)
          </h5>
          <div className="space-y-2">
            {shapData.positive_features.map((feat, idx) => (
              <div key={idx} className="flex items-center justify-between text-sm bg-emerald-50/50 dark:bg-emerald-950/20 p-2.5 rounded-lg border border-emerald-200/60 dark:border-emerald-800/40">
                <span className="font-medium text-slate-800 dark:text-slate-200">{feat.feature}</span>
                <span className="font-bold text-emerald-600 dark:text-emerald-400">
                  +{(feat.impact * 100).toFixed(1)}%
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Negative Features */}
        <div>
          <h5 className="text-xs font-semibold text-rose-700 dark:text-rose-400 mb-2 flex items-center gap-1">
            <TrendingDown size={14} /> Negative Contribution (- Penalty)
          </h5>
          <div className="space-y-2">
            {shapData.negative_features.map((feat, idx) => (
              <div key={idx} className="flex items-center justify-between text-sm bg-rose-50/50 dark:bg-rose-950/20 p-2.5 rounded-lg border border-rose-200/60 dark:border-rose-800/40">
                <span className="font-medium text-slate-800 dark:text-slate-200">{feat.feature}</span>
                <span className="font-bold text-rose-600 dark:text-rose-400">
                  {(feat.impact * 100).toFixed(1)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
