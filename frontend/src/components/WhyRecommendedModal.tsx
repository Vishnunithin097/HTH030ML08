import React from 'react';
import { RecommendationItem } from '../types';
import { X, CheckCircle2, TrendingUp, ShieldAlert, Cpu } from 'lucide-react';

interface WhyRecommendedModalProps {
  item: RecommendationItem | null;
  onClose: () => void;
}

export const WhyRecommendedModal: React.FC<WhyRecommendedModalProps> = ({ item, onClose }) => {
  if (!item) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div>
            <span className="text-xs font-semibold text-emerald-600 uppercase tracking-wider">
              Explainability Audit
            </span>
            <h3 className="text-base font-bold text-slate-900 mt-0.5">
              Why was this product recommended?
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="py-4 space-y-4">
          <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-100">
            <h4 className="text-sm font-semibold text-slate-900">{item.name}</h4>
            <p className="text-xs text-slate-500 mt-0.5">
              {item.category_name} • Item ID: #{item.item_id}
            </p>
          </div>

          <div className="space-y-2">
            <h5 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Signal Attribution
            </h5>
            <div className="p-3 bg-emerald-50 text-emerald-900 text-xs rounded-xl border border-emerald-200 flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
              <span>{item.explanation}</span>
            </div>
          </div>

          <div className="space-y-2">
            <h5 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Score Decomposition
            </h5>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-3 rounded-xl border border-slate-100 bg-slate-50">
                <div className="flex items-center gap-1.5 text-slate-500 mb-1">
                  <Cpu className="w-3.5 h-3.5" /> ML Relevance
                </div>
                <div className="text-base font-bold text-slate-900">
                  {(item.relevance_score * 100).toFixed(1)}%
                </div>
              </div>
              <div className="p-3 rounded-xl border border-slate-100 bg-slate-50">
                <div className="flex items-center gap-1.5 text-slate-500 mb-1">
                  <TrendingUp className="w-3.5 h-3.5" /> Business Value
                </div>
                <div className="text-base font-bold text-slate-900">
                  {((item.business_score ?? 0.5) * 100).toFixed(1)}%
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="pt-3 border-t border-slate-100 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-900 text-white rounded-xl text-xs font-semibold hover:bg-slate-800 transition-colors"
          >
            Close Audit
          </button>
        </div>
      </div>
    </div>
  );
};
