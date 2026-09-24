import React from 'react';
import { ScoreBreakdownChart } from '../components/ScoreBreakdownChart';
import { BarChart3, TrendingUp, Layers, Cpu } from 'lucide-react';

export const Analytics: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center gap-2 mb-2">
          <BarChart3 className="w-5 h-5 text-emerald-600" />
          <h2 className="text-lg font-bold text-slate-900">Analytics & Performance Diagnostic Hub</h2>
        </div>
        <p className="text-xs text-slate-500">
          Monitor ranking fidelity (NDCG), category intra-list diversity, and business margin lift metrics.
        </p>
      </div>

      {/* KPI Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold">NDCG@10</span>
            <Cpu className="w-4 h-4 text-blue-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900">0.742</div>
          <span className="text-[11px] text-emerald-600 font-medium">High ranking quality</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold">Margin Lift</span>
            <TrendingUp className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-bold text-emerald-600">+14.8%</div>
          <span className="text-[11px] text-slate-400 font-medium">vs pure relevance</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold">Category Diversity</span>
            <Layers className="w-4 h-4 text-purple-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900">0.68</div>
          <span className="text-[11px] text-slate-400 font-medium">Intra-list entropy</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold">Stock Out Avoidance</span>
            <BarChart3 className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900">96.0%</div>
          <span className="text-[11px] text-emerald-600 font-medium">Guarded inventory</span>
        </div>
      </div>

      <ScoreBreakdownChart />
    </div>
  );
};
