import React from 'react';
import { RecommendationItem } from '../types';
import { ProductCard } from './ProductCard';
import { PackageOpen, Sparkles } from 'lucide-react';

interface RecommendationListProps {
  items: RecommendationItem[];
  loading: boolean;
  onExplainClick: (item: RecommendationItem) => void;
}

export const RecommendationList: React.FC<RecommendationListProps> = ({
  items,
  loading,
  onExplainClick,
}) => {
  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {[...Array(8)].map((_, i) => (
          <div key={i} className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm animate-pulse flex flex-col justify-between h-[360px]">
            <div>
              <div className="flex justify-between items-center mb-3">
                <div className="w-16 h-5 bg-slate-200 rounded"></div>
                <div className="w-14 h-4 bg-slate-200 rounded"></div>
              </div>
              <div className="w-full h-28 bg-slate-100 rounded-lg mb-3"></div>
              <div className="w-24 h-3 bg-slate-200 rounded mb-2"></div>
              <div className="w-full h-4 bg-slate-200 rounded mb-1"></div>
              <div className="w-3/4 h-4 bg-slate-200 rounded mb-4"></div>
            </div>
            <div>
              <div className="w-full h-10 bg-slate-100 rounded-lg mb-3"></div>
              <div className="flex justify-between items-center pt-2 border-t border-slate-100">
                <div className="w-16 h-5 bg-slate-200 rounded"></div>
                <div className="w-20 h-6 bg-slate-200 rounded"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="text-center py-16 bg-white rounded-xl border border-slate-200 p-8 shadow-xs">
        <div className="w-12 h-12 bg-slate-100 text-slate-400 rounded-xl flex items-center justify-center mx-auto mb-3">
          <PackageOpen className="w-6 h-6" />
        </div>
        <h4 className="text-base font-semibold text-slate-800">No Candidate Recommendations Available</h4>
        <p className="text-xs text-slate-500 max-w-md mx-auto mt-1">
          No products matched the current filtering constraints or shopper profile. Try adjusting guardrail configurations or selecting another shopper.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {items.map((item) => (
        <ProductCard key={item.item_id} item={item} onExplainClick={onExplainClick} />
      ))}
    </div>
  );
};
