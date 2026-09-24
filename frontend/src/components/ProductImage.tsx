import React, { useState } from 'react';

export interface ProductImageProps {
  productId?: number;
  productName: string;
  brand?: string;
  category?: string;
  imageUrl?: string | null;
  imageSource?: string;
  imageStatus?: string;
  className?: string;
}

export const ProductImage: React.FC<ProductImageProps> = ({
  productId,
  productName,
  brand,
  category = 'General',
  imageUrl,
  imageSource,
  imageStatus,
  className = 'w-full h-44',
}) => {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);

  // Compute canonical alt text
  const altText = brand ? `${brand} ${productName}`.trim() : productName;

  // Resolve initial image source or default category fallback
  const getCategoryFallback = () => {
    const cat = (category || 'general').toLowerCase();
    if (cat.includes('beauty')) return '/product-images/fallback/beauty_hygiene.svg';
    if (cat.includes('gourmet')) return '/product-images/fallback/gourmet_world_food.svg';
    if (cat.includes('kitchen')) return '/product-images/fallback/kitchen_garden_pets.svg';
    if (cat.includes('clean')) return '/product-images/fallback/cleaning_household.svg';
    if (cat.includes('snack')) return '/product-images/fallback/snacks_branded_foods.svg';
    if (cat.includes('grain') || cat.includes('oil')) return '/product-images/fallback/foodgrains_oil_masala.svg';
    if (cat.includes('bakery') || cat.includes('dairy')) return '/product-images/fallback/bakery_cakes_dairy.svg';
    if (cat.includes('beverage')) return '/product-images/fallback/beverages.svg';
    if (cat.includes('baby')) return '/product-images/fallback/baby_care.svg';
    if (cat.includes('fruit') || cat.includes('veg')) return '/product-images/fallback/fruits_vegetables.svg';
    if (cat.includes('meat') || cat.includes('egg') || cat.includes('fish')) return '/product-images/fallback/eggs_meat_fish.svg';
    return '/product-images/fallback/general.svg';
  };

  const activeSrc = !error && imageUrl ? imageUrl : getCategoryFallback();

  return (
    <div className={`relative overflow-hidden bg-slate-50/70 border-b border-slate-100 flex items-center justify-center ${className}`}>
      {/* Soft Image Skeleton */}
      {!loaded && (
        <div className="absolute inset-0 bg-slate-100 animate-pulse" />
      )}

      {/* Product Image Asset */}
      <img
        src={activeSrc}
        alt={altText}
        loading="lazy"
        onLoad={() => setLoaded(true)}
        onError={() => {
          if (!error) {
            setError(true);
          }
          setLoaded(true);
        }}
        className={`w-full h-full object-contain p-2.5 transition-opacity duration-200 ${
          loaded ? 'opacity-100' : 'opacity-0'
        }`}
      />
    </div>
  );
};
