import React from 'react';
import { RecommendationItem } from '../types';
import { ProductCard } from './ProductCard';
import { SkeletonProductCard } from './SkeletonProductCard';
import { EmptyState } from './EmptyState';

interface RecommendationListProps {
  items: RecommendationItem[];
  loading: boolean;
  mode?: 'pure' | 'business_aware';
  onExplainClick: (item: RecommendationItem) => void;
  onReset?: () => void;
}

export const RecommendationList: React.FC<RecommendationListProps> = ({
  items,
  loading,
  mode = 'business_aware',
  onExplainClick,
  onReset,
}) => {
  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {[...Array(8)].map((_, i) => (
          <SkeletonProductCard key={i} />
        ))}
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <EmptyState
        title="No recommendation candidates"
        description="No products matched the current filtering constraints or shopper profile. Try adjusting guardrails or selecting another shopper identity."
        onReset={onReset}
      />
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {items.map((item) => (
        <ProductCard
          key={`${item.item_id}-${item.rank}`}
          item={item}
          mode={mode}
          onExplainClick={onExplainClick}
        />
      ))}
    </div>
  );
};
