import React from 'react';

interface CircularScoreProps {
  score: number;
  size?: number;
  strokeWidth?: number;
  label?: string;
  sublabel?: string;
  color?: string;
}

export const CircularScore: React.FC<CircularScoreProps> = ({
  score,
  size = 140,
  strokeWidth = 10,
  label = 'Overall',
  sublabel,
  color = '#0A66C2'
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const clampedScore = Math.min(100, Math.max(0, score));
  const strokeDashoffset = circumference - (clampedScore / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            fill="transparent"
            className="text-slate-200 dark:text-slate-700"
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className="text-2xl font-bold text-slate-800 dark:text-slate-100">
            {clampedScore}%
          </span>
          {label && <span className="text-xs font-medium text-slate-500 dark:text-slate-400">{label}</span>}
        </div>
      </div>
      {sublabel && <p className="mt-2 text-xs font-medium text-slate-500 dark:text-slate-400">{sublabel}</p>}
    </div>
  );
};
