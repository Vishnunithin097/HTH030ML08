import React from 'react';
import { RecommendationItem } from '../types';
import { ProductImage } from './ProductImage';
import { Star, Info, ShieldCheck, Sparkles, AlertCircle } from 'lucide-react';

interface ProductCardProps {
  item: RecommendationItem;
  mode?: 'pure' | 'business_aware';
  onExplainClick: (item: RecommendationItem) => void;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  item,
  mode = 'business_aware',
  onExplainClick,
}) => {
  const margin = item.margin_pct ?? 20;
  const inventory = item.inventory_count ?? 50;
  const rating = item.rating ?? 4.0;
  const isLowStock = inventory < 15;
  const isCold = item.is_cold_start;

  // Format source label nicely
  const getSourceLabel = () => {
    switch (item.recommendation_source) {
      case 'hybrid_cf_content':
        return 'Hybrid Match';
      case 'collaborative_only':
        return 'Shopper Affinity';
      case 'tfidf_content_only':
        return 'Content Match';
      case 'cold_start_category_content':
        return 'Category Discovery';
      case 'cold_start_item_boost':
        return 'New Arrival';
      case 'catalog_fallback':
        return 'Popular in Catalog';
      default:
        return 'Personalized';
    }
  };

  return (
    <div className="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-xs hover:border-slate-300 hover:shadow-sm transition-all flex flex-col justify-between group">
      <div>
        {/* Top Meta Bar */}
        <div className="px-3 pt-2.5 pb-1.5 flex items-center justify-between gap-1 text-[11px]">
          <span className="font-semibold text-slate-700">
            #{item.rank}
          </span>
          <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium ${
            isCold
              ? 'bg-amber-50 text-amber-800 border border-amber-200/80'
              : 'bg-slate-100 text-slate-600'
          }`}>
            {isCold ? <Sparkles className="w-2.5 h-2.5 text-amber-600" /> : null}
            {getSourceLabel()}
          </span>
        </div>

        {/* Product Image */}
        <ProductImage
          productId={item.item_id}
          productName={item.name || `Product #${item.item_id}`}
          brand={item.brand}
          category={item.category_name}
          subcategory={item.subcategory}
          imageUrl={item.image_url}
          imageStatus={item.image_status}
          imageSource={item.image_source}
          className="w-full h-40 bg-white"
        />

        {/* Card Content */}
        <div className="p-3">
          {/* Brand & Category */}
          <div className="text-[11px] text-slate-500 mb-1 flex items-center gap-1.5 truncate">
            {item.brand && (
              <>
                <span className="font-medium text-slate-700 truncate">{item.brand}</span>
                <span className="text-slate-300">•</span>
              </>
            )}
            <span className="truncate">{item.category_name || 'General'}</span>
          </div>

          {/* Product Title */}
          <h3
            className="text-xs font-medium text-slate-900 line-clamp-2 min-h-[32px] leading-snug mb-2 group-hover:text-emerald-700 transition-colors"
            title={item.name}
          >
            {item.name || `Catalog Product #${item.item_id}`}
          </h3>

          {/* Rating & Commercial signals in business mode */}
          <div className="flex items-center justify-between gap-2 text-xs mb-2">
            <div className="flex items-center gap-1 text-slate-700 font-medium">
              <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
              <span>{rating.toFixed(1)}</span>
            </div>

            {mode === 'business_aware' && (
              <div className="flex items-center gap-1 text-[11px]">
                {isLowStock ? (
                  <span className="text-amber-700 font-medium flex items-center gap-0.5">
                    <AlertCircle className="w-3 h-3 text-amber-500" />
                    Only {inventory} left
                  </span>
                ) : (
                  <span className="text-slate-500">
                    {inventory} in stock
                  </span>
                )}
              </div>
            )}
          </div>

          {/* Business Mode Subtle Margin Tag */}
          {mode === 'business_aware' && margin >= 30 && (
            <div className="inline-flex items-center gap-1 text-[10px] text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200/60 font-medium mb-1">
              <ShieldCheck className="w-3 h-3 text-emerald-600" />
              High Margin SKU ({margin.toFixed(0)}%)
            </div>
          )}
        </div>
      </div>

      {/* Card Footer: Price & Why Recommended */}
      <div className="px-3 py-2.5 bg-slate-50/80 border-t border-slate-100 flex items-center justify-between">
        <div>
          <span className="text-[10px] text-slate-400 block font-normal leading-tight">Price</span>
          <span className="text-sm font-semibold text-slate-900">
            ₹{item.price ? item.price.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '299.00'}
          </span>
        </div>

        <button
          onClick={() => onExplainClick(item)}
          className="inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium text-slate-700 hover:text-emerald-800 bg-white hover:bg-emerald-50/60 rounded border border-slate-200 hover:border-emerald-300 shadow-2xs transition-all"
        >
          <Info className="w-3.5 h-3.5 text-emerald-600" />
          <span>Why this?</span>
        </button>
      </div>
    </div>
  );
};
