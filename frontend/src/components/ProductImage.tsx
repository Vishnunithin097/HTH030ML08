import React, { useState } from 'react';

export interface ProductImageProps {
  productId?: number;
  productName: string;
  brand?: string;
  category?: string;
  subcategory?: string;
  imageUrl?: string | null;
  imageSource?: string;
  imageStatus?: string;
  className?: string;
}

interface CategoryStyle {
  title: string;
  bgTop: string;
  bgBot: string;
  accent: string;
  icon: string;
  shape: React.ReactNode;
}

const CATEGORY_STYLES: Record<string, CategoryStyle> = {
  beauty: {
    title: 'Beauty & Personal Care',
    bgTop: '#fff1f2',
    bgBot: '#ffe4e6',
    accent: '#be123c',
    icon: '✨',
    shape: (
      <>
        <rect x="150" y="110" width="100" height="180" rx="20" fill="#f43f5e" opacity="0.85" />
        <rect x="175" y="70" width="50" height="40" rx="8" fill="#fda4af" />
        <circle cx="200" cy="180" r="28" fill="#ffffff" opacity="0.3" />
        <path d="M185 180 L215 180" stroke="#ffffff" strokeWidth="4" strokeLinecap="round" />
      </>
    ),
  },
  gourmet: {
    title: 'Gourmet & World Food',
    bgTop: '#faf5ff',
    bgBot: '#f3e8ff',
    accent: '#6b21a8',
    icon: '🍷',
    shape: (
      <>
        <path d="M160 120 L240 120 L220 220 L180 220 Z" fill="#9333ea" opacity="0.85" />
        <rect x="192" y="220" width="16" height="50" fill="#c084fc" />
        <ellipse cx="200" cy="275" rx="35" ry="8" fill="#7e22ce" />
        <ellipse cx="200" cy="120" rx="40" ry="10" fill="#d8b4fe" />
      </>
    ),
  },
  kitchen: {
    title: 'Kitchen & Home',
    bgTop: '#f8fafc',
    bgBot: '#f1f5f9',
    accent: '#334155',
    icon: '🍳',
    shape: (
      <>
        <ellipse cx="190" cy="190" rx="75" ry="35" fill="#475569" opacity="0.9" />
        <ellipse cx="190" cy="185" rx="65" ry="28" fill="#64748b" />
        <path d="M260 190 L320 170" stroke="#1e293b" strokeWidth="12" strokeLinecap="round" />
      </>
    ),
  },
  cleaning: {
    title: 'Cleaning & Household',
    bgTop: '#f0fdfa',
    bgBot: '#ccfbf1',
    accent: '#0f766e',
    icon: '🧹',
    shape: (
      <>
        <rect x="160" y="140" width="80" height="150" rx="16" fill="#0d9488" opacity="0.85" />
        <path d="M180 140 L180 90 L160 90 L170 70 L210 70 L200 90 L200 140 Z" fill="#2dd4bf" />
        <circle cx="200" cy="200" r="20" fill="#ffffff" opacity="0.3" />
      </>
    ),
  },
  snack: {
    title: 'Snacks & Packaged Food',
    bgTop: '#fff7ed',
    bgBot: '#ffedd5',
    accent: '#c2410c',
    icon: '🍿',
    shape: (
      <>
        <path d="M150 100 L250 100 L235 280 L165 280 Z" fill="#ea580c" opacity="0.85" />
        <path d="M150 100 Q200 115 250 100 L248 115 Q200 130 152 115 Z" fill="#fed7aa" />
        <circle cx="200" cy="190" r="24" fill="#ffffff" opacity="0.35" />
      </>
    ),
  },
  grain: {
    title: 'Staples, Oil & Spices',
    bgTop: '#fefce8',
    bgBot: '#fef08a',
    accent: '#a16207',
    icon: '🌾',
    shape: (
      <>
        <rect x="165" y="120" width="70" height="160" rx="12" fill="#ca8a04" opacity="0.85" />
        <rect x="185" y="80" width="30" height="40" rx="4" fill="#fde047" />
        <ellipse cx="200" cy="200" rx="20" ry="30" fill="#ffffff" opacity="0.3" />
      </>
    ),
  },
  bakery: {
    title: 'Bakery & Dairy',
    bgTop: '#fffbeb',
    bgBot: '#fef3c7',
    accent: '#b45309',
    icon: '🍞',
    shape: (
      <>
        <path d="M140 180 Q140 120 200 120 Q260 120 260 180 L250 260 L150 260 Z" fill="#d97706" opacity="0.85" />
        <line x1="170" y1="150" x2="185" y2="180" stroke="#fef3c7" strokeWidth="4" strokeLinecap="round" />
        <line x1="200" y1="145" x2="200" y2="180" stroke="#fef3c7" strokeWidth="4" strokeLinecap="round" />
        <line x1="230" y1="150" x2="215" y2="180" stroke="#fef3c7" strokeWidth="4" strokeLinecap="round" />
      </>
    ),
  },
  beverage: {
    title: 'Beverages & Drinks',
    bgTop: '#ecfdf5',
    bgBot: '#d1fae5',
    accent: '#047857',
    icon: '☕',
    shape: (
      <>
        <path d="M170 120 L230 120 L220 270 L180 270 Z" fill="#059669" opacity="0.85" />
        <rect x="188" y="75" width="24" height="45" rx="6" fill="#6ee7b7" />
        <ellipse cx="200" cy="190" rx="16" ry="35" fill="#ffffff" opacity="0.25" />
      </>
    ),
  },
  baby: {
    title: 'Baby Care',
    bgTop: '#fdf2f8',
    bgBot: '#fce7f3',
    accent: '#be185d',
    icon: '🍼',
    shape: (
      <>
        <rect x="165" y="130" width="70" height="150" rx="14" fill="#db2777" opacity="0.85" />
        <path d="M185 130 L185 90 L215 90 L215 130 Z" fill="#f472b6" />
        <path d="M190 90 Q200 65 210 90 Z" fill="#fbcfe8" />
      </>
    ),
  },
  fruit: {
    title: 'Fresh Fruits & Vegetables',
    bgTop: '#f0fdf4',
    bgBot: '#dcfce7',
    accent: '#15803d',
    icon: '🍎',
    shape: (
      <>
        <ellipse cx="200" cy="190" rx="65" ry="60" fill="#16a34a" opacity="0.9" />
        <path d="M200 130 Q215 95 230 100" stroke="#15803d" strokeWidth="6" strokeLinecap="round" fill="none" />
        <ellipse cx="225" cy="105" rx="14" ry="7" fill="#86efac" transform="rotate(-20 225 105)" />
      </>
    ),
  },
  general: {
    title: 'Catalog Product',
    bgTop: '#f8fafc',
    bgBot: '#e2e8f0',
    accent: '#475569',
    icon: '📦',
    shape: (
      <>
        <rect x="150" y="130" width="100" height="130" rx="12" fill="#64748b" opacity="0.85" />
        <path d="M150 160 L250 160" stroke="#e2e8f0" strokeWidth="4" />
      </>
    ),
  },
};

function getCategoryStyle(categoryName?: string, subcategoryName?: string, productName?: string): CategoryStyle {
  const combined = `${categoryName || ''} ${subcategoryName || ''} ${productName || ''}`.toLowerCase();
  if (combined.includes('beauty') || combined.includes('skin') || combined.includes('hair') || combined.includes('groom') || combined.includes('fragrance') || combined.includes('soap')) return CATEGORY_STYLES.beauty;
  if (combined.includes('gourmet') || combined.includes('chocolate') || combined.includes('sauce') || combined.includes('spread') || combined.includes('syrup')) return CATEGORY_STYLES.gourmet;
  if (combined.includes('kitchen') || combined.includes('pet') || combined.includes('cookware') || combined.includes('container') || combined.includes('storage') || combined.includes('bottle')) return CATEGORY_STYLES.kitchen;
  if (combined.includes('clean') || combined.includes('detergent') || combined.includes('scrub') || combined.includes('wipe')) return CATEGORY_STYLES.cleaning;
  if (combined.includes('snack') || combined.includes('biscuit') || combined.includes('namkeen') || combined.includes('candy') || combined.includes('chips') || combined.includes('halwa') || combined.includes('sweet')) return CATEGORY_STYLES.snack;
  if (combined.includes('grain') || combined.includes('oil') || combined.includes('masala') || combined.includes('spice') || combined.includes('rice') || combined.includes('atta') || combined.includes('dal')) return CATEGORY_STYLES.grain;
  if (combined.includes('bakery') || combined.includes('dairy') || combined.includes('bread') || combined.includes('milk') || combined.includes('butter') || combined.includes('cheese')) return CATEGORY_STYLES.bakery;
  if (combined.includes('beverage') || combined.includes('tea') || combined.includes('coffee') || combined.includes('drink') || combined.includes('juice')) return CATEGORY_STYLES.beverage;
  if (combined.includes('baby') || combined.includes('diaper')) return CATEGORY_STYLES.baby;
  if (combined.includes('fruit') || combined.includes('veg') || combined.includes('apple') || combined.includes('onion') || combined.includes('potato')) return CATEGORY_STYLES.fruit;
  return CATEGORY_STYLES.general;
}

export const ProductImage: React.FC<ProductImageProps> = ({
  productId,
  productName,
  brand,
  category = 'General',
  subcategory,
  imageUrl,
  imageSource,
  imageStatus,
  className = 'w-full h-40',
}) => {
  const [loaded, setLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);

  // Compute canonical alt text
  const altText = brand ? `${brand} ${productName}`.trim() : productName;
  const style = getCategoryStyle(category, subcategory, productName);

  const hasExternalImage = !hasError && imageUrl && (imageUrl.startsWith('http://') || imageUrl.startsWith('https://') || imageUrl.startsWith('data:image/'));

  return (
    <div
      className={`relative overflow-hidden bg-slate-50/70 border-b border-slate-100 flex items-center justify-center select-none ${className}`}
      style={{ aspectRatio: '1 / 1' }}
    >
      {hasExternalImage ? (
        <>
          {!loaded && (
            <div className="absolute inset-0 bg-slate-100 animate-pulse" />
          )}
          <img
            src={imageUrl!}
            alt={altText}
            loading="lazy"
            onLoad={() => setLoaded(true)}
            onError={() => setHasError(true)}
            className={`w-full h-full object-contain p-2.5 transition-opacity duration-200 ${
              loaded ? 'opacity-100' : 'opacity-0'
            }`}
          />
        </>
      ) : (
        /* High-Fidelity Studio Vector Illustration (Guaranteed 100% Reliable Render) */
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 400 400"
          className="w-full h-full object-contain p-2 transition-transform duration-300 group-hover:scale-105"
          role="img"
          aria-label={altText}
        >
          <defs>
            <linearGradient id={`bgGrad-${productId || 'item'}`} x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor={style.bgTop} />
              <stop offset="100%" stopColor={style.bgBot} />
            </linearGradient>
            <radialGradient id={`shadowGrad-${productId || 'item'}`} cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="rgba(15,23,42,0.15)" />
              <stop offset="100%" stopColor="rgba(15,23,42,0)" />
            </radialGradient>
            <filter id={`softShadow-${productId || 'item'}`} x="-10%" y="-10%" width="120%" height="120%">
              <feDropShadow dx="0" dy="8" stdDeviation="12" floodColor="rgba(15,23,42,0.12)" />
            </filter>
          </defs>

          {/* Clean Canvas Background */}
          <rect width="400" height="400" rx="16" fill={`url(#bgGrad-${productId || 'item'})`} />
          <rect x="1" y="1" width="398" height="398" rx="15" fill="none" stroke="rgba(226,232,240,0.8)" strokeWidth="1.5" />

          {/* Studio Surface Radial Floor Shadow */}
          <ellipse cx="200" cy="300" rx="120" ry="24" fill={`url(#shadowGrad-${productId || 'item'})`} />

          {/* Main Central Product Visual Frame */}
          <g filter={`url(#softShadow-${productId || 'item'})`}>
            {style.shape}
          </g>

          {/* Center Floating Icon Badge */}
          <circle cx="200" cy="180" r="32" fill="#ffffff" stroke="rgba(226,232,240,0.9)" strokeWidth="2" />
          <text x="200" y="188" fontSize="30" textAnchor="middle" dominantBaseline="central">
            {style.icon}
          </text>

          {/* Product Category Label */}
          <rect x="75" y="325" width="250" height="32" rx="16" fill="#ffffff" stroke="rgba(226,232,240,0.9)" strokeWidth="1" />
          <text
            x="200"
            y="345"
            fontFamily="-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif"
            fontSize="12"
            fontWeight="600"
            fill={style.accent}
            textAnchor="middle"
          >
            {category || style.title}
          </text>
        </svg>
      )}
    </div>
  );
};
