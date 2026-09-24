import React, { useState } from 'react';
import { Package } from 'lucide-react';

interface ProductImageProps {
  src?: string | null;
  alt: string;
  category?: string;
  imageStatus?: string;
  imageSource?: string;
  className?: string;
}

export const ProductImage: React.FC<ProductImageProps> = ({
  src,
  alt,
  category = 'Catalog Item',
  imageStatus,
  className = 'w-full h-44',
}) => {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);

  // Derive initial character for generic fallback
  const initial = alt ? alt.trim().charAt(0).toUpperCase() : 'P';

  return (
    <div className={`relative overflow-hidden bg-slate-50 border-b border-slate-100 flex items-center justify-center ${className}`}>
      {/* Loading Skeleton */}
      {!loaded && !error && (
        <div className="absolute inset-0 bg-gradient-to-r from-slate-100 via-slate-200/60 to-slate-100 animate-pulse" />
      )}

      {/* Actual Image */}
      {src && !error ? (
        <img
          src={src}
          alt={alt}
          loading="lazy"
          onLoad={() => setLoaded(true)}
          onError={() => {
            setError(true);
            setLoaded(true);
          }}
          className={`w-full h-full object-contain p-2 transition-opacity duration-200 ${
            loaded ? 'opacity-100' : 'opacity-0'
          }`}
        />
      ) : (
        /* Graceful Deterministic Fallback */
        <div className="flex flex-col items-center justify-center p-4 text-center">
          <div className="w-12 h-12 rounded-full bg-emerald-50 border border-emerald-200/70 flex items-center justify-center text-emerald-800 font-bold text-base mb-1.5 shadow-xs">
            {initial}
          </div>
          <span className="text-xs font-medium text-slate-600 line-clamp-1 max-w-[90%]">
            {alt || 'Product'}
          </span>
          <span className="text-[11px] text-slate-400 mt-0.5 line-clamp-1">
            {category}
          </span>
        </div>
      )}

      {/* Subtle image status badge if non-verified fallback */}
      {imageStatus === 'fallback' && (
        <span className="absolute bottom-1.5 right-1.5 px-1.5 py-0.5 rounded text-[9px] font-medium bg-slate-900/60 text-white backdrop-blur-xs">
          Catalog Preview
        </span>
      )}
    </div>
  );
};
