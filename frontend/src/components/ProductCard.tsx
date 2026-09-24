import React from 'react';
import { RecommendationItem } from '../types';
import { Sparkles, Info, ShieldCheck, Tag } from 'lucide-react';

interface ProductCardProps {
  item: RecommendationItem;
  onExplainClick: (item: RecommendationItem) => void;
}

export const ProductCard: React.FC<ProductCardProps> = ({ item, onExplainClick }) => {
  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between">
      <div className="p-4">
        {/* Top Badges */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
            #{item.rank} Top Pick
          </span>
          {item.is_cold_start && (
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200 flex items-center gap-1">
              <Sparkles className="w-3 h-3" /> Cold-Start
            </span>
          )}
        </div>

        {/* Category & Brand */}
        <div className="text-xs text-slate-500 mb-1 flex items-center gap-1">
          <span>{item.category_name || 'General Category'}</span>
          {item.brand && <span>• {item.brand}</span>}
        </div>

        {/* Name */}
        <h3 className="text-sm font-semibold text-slate-900 line-clamp-2 mb-2">
          {item.name || `Product #${item.item_id}`}
        </h3>

        {/* Explanation snippet */}
        <p className="text-xs text-slate-600 bg-slate-50 p-2 rounded-lg border border-slate-100 line-clamp-2 mb-3">
          💡 {item.explanation}
        </p>

        {/* Business Metrics Pill */}
        <div className="grid grid-cols-2 gap-2 text-xs py-2 border-t border-slate-100">
          <div>
            <span className="text-slate-400 block">Margin</span>
            <span className="font-semibold text-emerald-600">{item.margin_pct ?? 20}%</span>
          </div>
          <div>
            <span className="text-slate-400 block">Stock</span>
            <span className="font-semibold text-slate-700">{item.inventory_count ?? 100} units</span>
          </div>
        </div>
      </div>

      {/* Footer / Actions */}
      <div className="p-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
        <div className="text-sm font-bold text-slate-900">
          ₹{item.price?.toFixed(2) ?? '299.00'}
        </div>
        <button
          onClick={() => onExplainClick(item)}
          className="text-xs font-medium text-emerald-700 hover:text-emerald-800 flex items-center gap-1 bg-white px-2.5 py-1.5 rounded-lg border border-slate-200 shadow-sm hover:border-emerald-300 transition-colors"
        >
          <Info className="w-3.5 h-3.5" />
          Why This?
        </button>
      </div>
    </div>
  );
};
