import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';

interface ScoreBreakdownProps {
  data?: Array<{ name: string; relevance: number; business: number; final: number }>;
}

export const ScoreBreakdownChart: React.FC<ScoreBreakdownProps> = ({ data }) => {
  const chartData = data || [
    { name: 'Item #1', relevance: 85, business: 90, final: 87 },
    { name: 'Item #2', relevance: 82, business: 75, final: 80 },
    { name: 'Item #3', relevance: 78, business: 95, final: 83 },
    { name: 'Item #4', relevance: 74, business: 60, final: 70 },
    { name: 'Item #5', relevance: 70, business: 88, final: 75 },
  ];

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
      <h4 className="text-sm font-bold text-slate-900 mb-4">Relevance vs Business Score Decomposition</h4>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <XAxis dataKey="name" fontSize={11} stroke="#94a3b8" />
            <YAxis fontSize={11} stroke="#94a3b8" />
            <Tooltip
              contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e2e8f0' }}
            />
            <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
            <Bar dataKey="relevance" name="ML Relevance" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            <Bar dataKey="business" name="Business Score" fill="#10b981" radius={[4, 4, 0, 0]} />
            <Bar dataKey="final" name="Final Score" fill="#0f172a" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
