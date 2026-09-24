import React from 'react';

export const SkeletonProductCard: React.FC = () => {
  return (
    <div className="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-xs animate-pulse flex flex-col justify-between">
      <div>
        {/* Image Box Skeleton */}
        <div className="w-full h-44 bg-slate-100 border-b border-slate-100" />

        {/* Details Skeleton */}
        <div className="p-3.5 space-y-2.5">
          <div className="flex items-center justify-between">
            <div className="h-3 w-16 bg-slate-100 rounded" />
            <div className="h-3 w-12 bg-slate-100 rounded" />
          </div>

          <div className="h-4 w-5/6 bg-slate-200 rounded" />
          <div className="h-4 w-3/5 bg-slate-200 rounded" />

          <div className="pt-2 flex items-center gap-1.5">
            <div className="h-3.5 w-10 bg-slate-100 rounded" />
            <div className="h-3.5 w-16 bg-slate-100 rounded" />
          </div>
        </div>
      </div>

      {/* Card Footer Skeleton */}
      <div className="p-3 bg-slate-50/50 border-t border-slate-100 flex items-center justify-between">
        <div className="h-5 w-16 bg-slate-200 rounded" />
        <div className="h-6 w-24 bg-slate-100 rounded" />
      </div>
    </div>
  );
};
