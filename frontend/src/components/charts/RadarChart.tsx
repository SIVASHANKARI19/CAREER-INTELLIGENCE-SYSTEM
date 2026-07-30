import React from 'react';
import {
  Radar, RadarChart as RechartsRadarChart, PolarGrid, PolarAngleAxis,
  PolarRadiusAxis, ResponsiveContainer, Tooltip
} from 'recharts';

interface ReadinessRadarProps {
  data: {
    technical_readiness: number;
    communication_readiness: number;
    resume_readiness: number;
    project_readiness: number;
    github_readiness: number;
    interview_readiness: number;
    overall_readiness: number;
  };
}

export const ReadinessRadarChart: React.FC<ReadinessRadarProps> = ({ data }) => {
  const chartData = [
    { subject: 'Technical', A: data.technical_readiness, fullMark: 100 },
    { subject: 'Communication', A: data.communication_readiness, fullMark: 100 },
    { subject: 'Resume', A: data.resume_readiness, fullMark: 100 },
    { subject: 'Projects', A: data.project_readiness, fullMark: 100 },
    { subject: 'GitHub', A: data.github_readiness, fullMark: 100 },
    { subject: 'Interview', A: data.interview_readiness, fullMark: 100 },
  ];

  return (
    <div className="w-full h-72">
      <ResponsiveContainer width="100%" height="100%">
        <RechartsRadarChart cx="50%" cy="50%" outerRadius="75%" data={chartData}>
          <PolarGrid stroke="#e2e8f0" />
          <PolarAngleAxis dataKey="subject" stroke="#64748b" tick={{ fontSize: 12, fontWeight: 500 }} />
          <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#cbd5e1" />
          <Radar
            name="Readiness Score"
            dataKey="A"
            stroke="#0A66C2"
            fill="#0A66C2"
            fillOpacity={0.45}
          />
          <Tooltip
            contentStyle={{ backgroundColor: '#1e293b', borderRadius: '8px', color: '#fff', border: 'none' }}
          />
        </RechartsRadarChart>
      </ResponsiveContainer>
    </div>
  );
};
