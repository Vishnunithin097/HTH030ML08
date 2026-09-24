import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts';
import { RecommendationItem } from '../types';

interface ScoreBreakdownChartProps {
  items?: RecommendationItem[];
}

export const ScoreBreakdownChart: React.FC<ScoreBreakdownChartProps> = ({ items }) => {
  const chartData = (items && items.length > 0)
    ? items.slice(0, 8).map((item) => ({
        name: item.name ? (item.name.length > 14 ? item.name.substring(0, 14) + '...' : item.name) : `#${item.item_id}`,
        relevance: Number((item.relevance_score * 100).toFixed(1)),
        business: Number(((item.business_score ?? 0.5) * 100).toFixed(1)),
        final: Number((item.final_score * 100).toFixed(1)),
      }))
    : [
        { name: 'Item #1', relevance: 88, business: 92, final: 89.6 },
        { name: 'Item #2', relevance: 85, business: 74, final: 80.6 },
        { name: 'Item #3', relevance: 81, business: 95, final: 86.6 },
        { name: 'Item #4', relevance: 78, business: 65, final: 72.8 },
        { name: 'Item #5', relevance: 74, business: 88, final: 79.6 },
      ];

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h4 className="text-sm font-bold text-slate-900">Score Decomposition (Top Items in Slate)</h4>
          <p className="text-xs text-slate-500">
            Comparing ML Relevance, Business Value Score, and Final Re-Ranked Score.
          </p>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
            <XAxis dataKey="name" fontSize={11} stroke="#64748b" tickLine={false} />
            <YAxis domain={[0, 100]} fontSize={11} stroke="#64748b" tickLine={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#ffffff',
                borderRadius: '8px',
                border: '1px solid #e2e8f0',
                fontSize: '12px',
                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
              }}
              formatter={(value: any) => [`${value}%`]}
            />
            <Legend
              wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }}
              iconType="circle"
            />
            <Bar dataKey="relevance" name="ML Relevance" fill="#2563eb" radius={[3, 3, 0, 0]} barSize={16} />
            <Bar dataKey="business" name="Business Score" fill="#16a34a" radius={[3, 3, 0, 0]} barSize={16} />
            <Bar dataKey="final" name="Final Score" fill="#0f172a" radius={[3, 3, 0, 0]} barSize={16} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
