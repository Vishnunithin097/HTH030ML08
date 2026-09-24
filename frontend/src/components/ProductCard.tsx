import React from 'react';
import { RecommendationItem } from '../types';
import { Info, Sparkles, AlertTriangle, CheckCircle2, TrendingUp, ShieldAlert, Package, Star } from 'lucide-react';

interface ProductCardProps {
  item: RecommendationItem;
  onExplainClick: (item: RecommendationItem) => void;
}

export const ProductCard: React.FC<ProductCardProps> = ({ item, onExplainClick }) => {
  const margin = item.margin_pct ?? 25;
  const inventory = item.inventory_count ?? 50;
  const isLowStock = inventory < 20;
  const isLowMargin = margin < 15;

  // Margin color styling
  const marginColor = margin >= 30 
    ? 'text-emerald-700 bg-emerald-50 border-emerald-200' 
    : margin >= 18 
    ? 'text-blue-700 bg-blue-50 border-blue-200' 
    : 'text-amber-700 bg-amber-50 border-amber-200';

  // Stock badge styling
  const stockColor = inventory >= 50
    ? 'text-slate-700 bg-slate-50 border-slate-200'
    : inventory >= 20
    ? 'text-amber-700 bg-amber-50 border-amber-200'
    : 'text-rose-700 bg-rose-50 border-rose-200';

  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm hover:shadow transition-all flex flex-col justify-between group">
      {/* Top Header & Badges */}
      <div className="p-4 flex-1 flex flex-col">
        <div className="flex items-center justify-between gap-2 mb-2.5">
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold bg-slate-900 text-white tracking-wide">
            RANK #{item.rank}
          </span>
          
          <div className="flex items-center gap-1">
            {item.is_cold_start ? (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-50 text-amber-800 border border-amber-200">
                <Sparkles className="w-3 h-3 text-amber-600" />
                Cold-Start
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-600">
                {item.recommendation_source === 'hybrid' ? 'Hybrid ML' : item.recommendation_source}
              </span>
            )}
          </div>
        </div>

        {/* Product Visual Placeholder or Image */}
        <div className="w-full h-32 bg-slate-50 rounded-lg border border-slate-100 mb-3 flex flex-col items-center justify-center p-3 relative overflow-hidden group-hover:bg-slate-100/70 transition-colors">
          <div className="w-10 h-10 rounded-full bg-slate-200/80 flex items-center justify-center text-slate-500 font-bold text-sm mb-1">
            {item.name ? item.name.charAt(0).toUpperCase() : 'P'}
          </div>
          <span className="text-[11px] font-medium text-slate-400 text-center line-clamp-1 px-2">
            {item.category_name || 'Catalog Item'}
          </span>
          {item.quality_score !== undefined && item.quality_score !== null && (
            <div className="absolute top-2 right-2 flex items-center gap-0.5 bg-white/90 px-1.5 py-0.5 rounded text-[10px] font-semibold text-slate-700 shadow-xs border border-slate-200/60">
              <Star className="w-3 h-3 text-amber-500 fill-amber-500" />
              <span>{item.quality_score.toFixed(1)}</span>
            </div>
          )}
        </div>

        {/* Category & Brand Metadata */}
        <div className="text-[11px] font-medium text-slate-500 mb-1 flex items-center gap-1.5 truncate">
          <span className="text-slate-700 font-semibold truncate">{item.category_name}</span>
          {item.brand && (
            <>
              <span className="text-slate-300">•</span>
              <span className="text-slate-500 truncate">{item.brand}</span>
            </>
          )}
        </div>

        {/* Product Title */}
        <h3 className="text-sm font-semibold text-slate-900 line-clamp-2 mb-2 leading-snug" title={item.name}>
          {item.name || `Catalog Item #${item.item_id}`}
        </h3>

        {/* Score Breakdown Indicator */}
        <div className="mt-auto pt-2 border-t border-slate-100">
          <div className="grid grid-cols-3 gap-1 text-[10px] text-center mb-2 bg-slate-50/80 p-1.5 rounded-lg border border-slate-100">
            <div>
              <span className="text-slate-400 block font-medium">Relevance</span>
              <span className="font-bold text-blue-600">{(item.relevance_score * 100).toFixed(0)}%</span>
            </div>
            <div>
              <span className="text-slate-400 block font-medium">Business</span>
              <span className="font-bold text-emerald-600">{((item.business_score ?? 0.5) * 100).toFixed(0)}%</span>
            </div>
            <div>
              <span className="text-slate-400 block font-medium">Final</span>
              <span className="font-bold text-slate-900">{(item.final_score * 100).toFixed(0)}%</span>
            </div>
          </div>

          {/* Business Attributes: Margin & Inventory */}
          <div className="flex items-center gap-2 text-[11px]">
            <span className={`px-2 py-0.5 rounded border font-medium flex-1 text-center ${marginColor}`}>
              Margin: {margin.toFixed(1)}%
            </span>
            <span className={`px-2 py-0.5 rounded border font-medium flex-1 text-center ${stockColor}`}>
              Stock: {inventory}u
            </span>
          </div>

          {/* Soft Penalties Indicator if present */}
          {item.penalty_reasons && item.penalty_reasons.length > 0 && (
            <div className="mt-1.5 text-[10px] text-amber-700 bg-amber-50/80 px-2 py-0.5 rounded border border-amber-200/60 flex items-center gap-1 truncate">
              <AlertTriangle className="w-2.5 h-2.5 shrink-0 text-amber-600" />
              <span className="truncate">{item.penalty_reasons[0]}</span>
            </div>
          )}
        </div>
      </div>

      {/* Card Footer */}
      <div className="p-3 bg-slate-50/70 border-t border-slate-100 flex items-center justify-between">
        <div className="text-sm font-bold text-slate-900">
          ₹{item.price ? item.price.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '299.00'}
        </div>

        <button
          onClick={() => onExplainClick(item)}
          className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-slate-700 bg-white hover:bg-slate-100 hover:text-slate-900 rounded-md border border-slate-200 shadow-sm transition-colors"
        >
          <Info className="w-3 h-3 text-emerald-600" />
          <span>Why This?</span>
        </button>
      </div>
    </div>
  );
};
