import React from 'react';
import { RecommendationItem } from '../types';
import { ProductCard } from './ProductCard';
import { PackageOpen } from 'lucide-react';

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
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 animate-pulse">
        {[...Array(8)].map((_, i) => (
          <div key={i} className="h-64 bg-slate-200 rounded-xl"></div>
        ))}
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="text-center py-16 bg-white rounded-xl border border-slate-200 p-8">
        <PackageOpen className="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <h4 className="text-base font-semibold text-slate-700">No Recommendations Available</h4>
        <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
          Select a shopper profile or switch modes to generate personalized candidate recommendations.
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
