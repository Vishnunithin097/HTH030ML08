import React, { useState, useEffect } from 'react';

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

/* ──────────────────────────────────────────────────────────────────────────
   Inline SVG fallback renderer — used ONLY when the network image fails.
   Uses pure SVG paths (no emoji) so it renders identically in all browsers.
   ────────────────────────────────────────────────────────────────────────── */

interface FallbackStyle {
  bgTop: string; bgBot: string; accent: string; label: string;
  body: React.ReactNode;
}

const FALLBACK_STYLES: Record<string, FallbackStyle> = {
  beauty: {
    bgTop: '#fff1f2', bgBot: '#ffe4e6', accent: '#be123c', label: 'Beauty & Hygiene',
    body: (<>
      <rect x="172" y="105" width="56" height="168" rx="20" fill="#f43f5e" opacity="0.88"/>
      <rect x="184" y="68"  width="32" height="40"  rx="7"  fill="#fda4af"/>
      <rect x="190" y="56"  width="20" height="14"  rx="5"  fill="#be123c"/>
      <ellipse cx="200" cy="188" rx="18" ry="36" fill="#ffffff" opacity="0.18"/>
      <rect x="178" y="148" width="44" height="3" rx="1.5" fill="#ffffff" opacity="0.45"/>
    </>),
  },
  gourmet: {
    bgTop: '#faf5ff', bgBot: '#f3e8ff', accent: '#6b21a8', label: 'Gourmet & World Food',
    body: (<>
      <rect x="152" y="148" width="96" height="110" rx="14" fill="#9333ea" opacity="0.88"/>
      <rect x="158" y="126" width="84" height="26" rx="6" fill="#d8b4fe"/>
      <ellipse cx="200" cy="148" rx="42" ry="10" fill="#6b21a8" opacity="0.55"/>
      <ellipse cx="200" cy="200" rx="30" ry="40" fill="#ffffff" opacity="0.16"/>
    </>),
  },
  kitchen: {
    bgTop: '#f8fafc', bgBot: '#f1f5f9', accent: '#334155', label: 'Kitchen & Home',
    body: (<>
      <rect x="158" y="112" width="84" height="148" rx="10" fill="#64748b" opacity="0.88"/>
      <rect x="158" y="112" width="84" height="28"  rx="10" fill="#94a3b8"/>
      <rect x="168" y="160" width="64" height="4" rx="2" fill="#ffffff" opacity="0.40"/>
      <rect x="172" y="176" width="56" height="4" rx="2" fill="#ffffff" opacity="0.28"/>
    </>),
  },
  cleaning: {
    bgTop: '#f0fdfa', bgBot: '#ccfbf1', accent: '#0f766e', label: 'Cleaning & Household',
    body: (<>
      <rect x="170" y="148" width="60" height="128" rx="14" fill="#0d9488" opacity="0.88"/>
      <path d="M182 148 L182 96 L162 96 L170 72 L214 72 L202 96 L202 148 Z" fill="#2dd4bf"/>
      <ellipse cx="200" cy="210" rx="18" ry="30" fill="#ffffff" opacity="0.18"/>
    </>),
  },
  snack: {
    bgTop: '#fff7ed', bgBot: '#ffedd5', accent: '#c2410c', label: 'Snacks & Branded Foods',
    body: (<>
      <path d="M154 100 L246 100 L230 280 L170 280 Z" fill="#ea580c" opacity="0.88"/>
      <path d="M154 100 Q200 116 246 100 L244 116 Q200 132 156 116 Z" fill="#fed7aa"/>
      <rect x="168" y="158" width="64" height="3" rx="1.5" fill="#ffffff" opacity="0.45"/>
      <circle cx="200" cy="198" r="20" fill="#ffffff" opacity="0.18"/>
    </>),
  },
  grain: {
    bgTop: '#fefce8', bgBot: '#fef9c3', accent: '#a16207', label: 'Foodgrains & Staples',
    body: (<>
      <rect x="166" y="118" width="68" height="158" rx="14" fill="#ca8a04" opacity="0.88"/>
      <rect x="184" y="76"  width="32" height="44"  rx="5"  fill="#fde047"/>
      <rect x="190" y="68"  width="20" height="12"  rx="4"  fill="#a16207"/>
      <ellipse cx="200" cy="195" rx="18" ry="30" fill="#ffffff" opacity="0.22"/>
    </>),
  },
  bakery: {
    bgTop: '#fffbeb', bgBot: '#fef3c7', accent: '#b45309', label: 'Bakery & Dairy',
    body: (<>
      <rect x="130" y="148" width="140" height="110" rx="12" fill="#d97706" opacity="0.88"/>
      <rect x="130" y="148" width="140" height="30"  rx="12" fill="#fcd34d"/>
      <rect x="148" y="192" width="104" height="4" rx="2" fill="#ffffff" opacity="0.40"/>
      <rect x="155" y="210" width="90"  height="4" rx="2" fill="#ffffff" opacity="0.28"/>
    </>),
  },
  beverage: {
    bgTop: '#ecfdf5', bgBot: '#d1fae5', accent: '#047857', label: 'Beverages',
    body: (<>
      <path d="M174 120 L226 120 L218 272 L182 272 Z" fill="#059669" opacity="0.88"/>
      <rect x="186" y="72" width="28" height="52" rx="8" fill="#6ee7b7"/>
      <rect x="190" y="60" width="20" height="16" rx="5" fill="#047857"/>
      <ellipse cx="200" cy="196" rx="16" ry="36" fill="#ffffff" opacity="0.20"/>
    </>),
  },
  baby: {
    bgTop: '#fdf2f8', bgBot: '#fce7f3', accent: '#be185d', label: 'Baby Care',
    body: (<>
      <rect x="164" y="128" width="72" height="148" rx="16" fill="#db2777" opacity="0.88"/>
      <path d="M182 128 L182 86 L218 86 L218 128 Z" fill="#f472b6"/>
      <path d="M188 86 Q200 62 212 86 Z" fill="#fbcfe8"/>
      <ellipse cx="200" cy="200" rx="22" ry="34" fill="#ffffff" opacity="0.20"/>
    </>),
  },
  fruit: {
    bgTop: '#f0fdf4', bgBot: '#dcfce7', accent: '#15803d', label: 'Fresh Produce',
    body: (<>
      <circle cx="200" cy="200" r="74" fill="#16a34a" opacity="0.90"/>
      <ellipse cx="200" cy="190" rx="44" ry="55" fill="#86efac" opacity="0.30"/>
      <path d="M200 130 Q220 90 238 98" stroke="#15803d" strokeWidth="7" strokeLinecap="round" fill="none"/>
    </>),
  },
  general: {
    bgTop: '#f8fafc', bgBot: '#e2e8f0', accent: '#475569', label: 'Catalog Product',
    body: (<>
      <rect x="152" y="128" width="96" height="130" rx="14" fill="#64748b" opacity="0.88"/>
      <path d="M152 160 L248 160" stroke="#e2e8f0" strokeWidth="3" strokeLinecap="round"/>
      <rect x="168" y="172" width="64" height="4" rx="2" fill="#ffffff" opacity="0.40"/>
      <rect x="172" y="188" width="56" height="4" rx="2" fill="#ffffff" opacity="0.28"/>
    </>),
  },
};

function resolveFallbackStyle(
  category?: string, subcategory?: string, productName?: string, imageUrl?: string | null
): FallbackStyle {
  const c = `${category || ''} ${subcategory || ''} ${productName || ''} ${imageUrl || ''}`.toLowerCase();
  if (c.includes('beauty') || c.includes('hygiene') || c.includes('skin') || c.includes('hair') || c.includes('bath') || c.includes('groom') || c.includes('fragrance') || c.includes('soap')) return FALLBACK_STYLES.beauty;
  if (c.includes('gourmet') || c.includes('world food') || c.includes('world_food') || c.includes('sauce') || c.includes('spread') || c.includes('chocolate') || c.includes('pickle') || c.includes('chutney')) return FALLBACK_STYLES.gourmet;
  if (c.includes('kitchen') || c.includes('garden') || c.includes('cookware') || c.includes('storage') || c.includes('pooja')) return FALLBACK_STYLES.kitchen;
  if (c.includes('clean') || c.includes('household') || c.includes('detergent') || c.includes('scrub')) return FALLBACK_STYLES.cleaning;
  if (c.includes('snack') || c.includes('branded food') || c.includes('biscuit') || c.includes('cookie') || c.includes('namkeen') || c.includes('candy') || c.includes('chips') || c.includes('mithai') || c.includes('frozen') || c.includes('ready to cook') || c.includes('ready to eat') || c.includes('instant') || c.includes('colour')) return FALLBACK_STYLES.snack;
  if (c.includes('foodgrain') || c.includes('grain') || c.includes('oil') || c.includes('masala') || c.includes('spice') || c.includes('rice') || c.includes('atta') || c.includes('dal') || c.includes('ghee') || c.includes('flour')) return FALLBACK_STYLES.grain;
  if (c.includes('bakery') || c.includes('cakes') || c.includes('dairy') || c.includes('bread') || c.includes('milk') || c.includes('butter') || c.includes('cheese') || c.includes('egg')) return FALLBACK_STYLES.bakery;
  if (c.includes('beverage') || c.includes('tea') || c.includes('coffee') || c.includes('drink') || c.includes('juice') || c.includes('water') || c.includes('soda')) return FALLBACK_STYLES.beverage;
  if (c.includes('baby') || c.includes('infant') || c.includes('diaper')) return FALLBACK_STYLES.baby;
  if (c.includes('fruit') || c.includes('vegetable') || c.includes('fresh') || c.includes('veg') || c.includes('apple') || c.includes('onion') || c.includes('potato')) return FALLBACK_STYLES.fruit;
  return FALLBACK_STYLES.general;
}

const InlineSVGFallback: React.FC<{
  productId?: number; productName: string; category?: string;
  subcategory?: string; imageUrl?: string | null;
}> = ({ productId, productName, category, subcategory, imageUrl }) => {
  const style = resolveFallbackStyle(category, subcategory, productName, imageUrl);
  const uid = `f${productId ?? Math.abs(productName.charCodeAt(0) || 0)}`;
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" className="w-full h-full" role="img" aria-label={productName}>
      <defs>
        <linearGradient id={`bg-${uid}`} x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor={style.bgTop}/>
          <stop offset="100%" stopColor={style.bgBot}/>
        </linearGradient>
        <radialGradient id={`sh-${uid}`} cx="50%" cy="92%" r="50%">
          <stop offset="0%" stopColor="rgba(15,23,42,0.16)"/>
          <stop offset="100%" stopColor="rgba(15,23,42,0)"/>
        </radialGradient>
        <filter id={`dr-${uid}`} x="-15%" y="-15%" width="130%" height="130%">
          <feDropShadow dx="0" dy="5" stdDeviation="9" floodColor="rgba(15,23,42,0.13)"/>
        </filter>
      </defs>
      <rect width="400" height="400" fill={`url(#bg-${uid})`} rx="16"/>
      <rect x="1" y="1" width="398" height="398" rx="15" fill="none" stroke="rgba(226,232,240,0.65)" strokeWidth="1.5"/>
      <ellipse cx="200" cy="305" rx="112" ry="18" fill={`url(#sh-${uid})`}/>
      <g filter={`url(#dr-${uid})`}>{style.body}</g>
      <rect x="80" y="328" width="240" height="28" rx="14" fill="#ffffff" fillOpacity="0.92" stroke="rgba(226,232,240,0.8)" strokeWidth="1"/>
      <text x="200" y="346"
        fontFamily="-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif"
        fontSize="11" fontWeight="600" fill={style.accent} textAnchor="middle">
        {subcategory || style.label}
      </text>
    </svg>
  );
};

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
  // Determine primary target image URL
  const primarySrc = imageUrl && imageUrl.trim().length > 0
    ? imageUrl
    : (productId != null ? `/images/products/${productId}.jpg` : null);

  const fallbackSrc = productId != null ? `/product-visuals/${productId}.svg` : null;

  const [src, setSrc] = useState<string | null>(primarySrc);
  const [stage, setStage] = useState<'loading' | 'loaded' | 'fallback'>('loading');

  useEffect(() => {
    setSrc(primarySrc);
    setStage('loading');
  }, [imageUrl, productId]);

  const altText = brand ? `${brand} ${productName}`.trim() : productName;

  const handleLoad = () => setStage('loaded');

  const handleError = () => {
    if (src !== fallbackSrc && fallbackSrc) {
      // Try fallback SVG next
      setSrc(fallbackSrc);
    } else {
      // Render polished inline SVG
      setStage('fallback');
    }
  };

  if (stage === 'fallback' || !src) {
    return (
      <div className={`relative overflow-hidden flex items-center justify-center select-none ${className}`} style={{ aspectRatio: '1/1' }}>
        <InlineSVGFallback
          productId={productId}
          productName={productName}
          category={category}
          subcategory={subcategory}
          imageUrl={imageUrl}
        />
      </div>
    );
  }

  return (
    <div className={`relative overflow-hidden flex items-center justify-center select-none bg-slate-50 ${className}`} style={{ aspectRatio: '1/1' }}>
      {stage === 'loading' && (
        <div className="absolute inset-0 bg-slate-100 animate-pulse"/>
      )}
      <img
        key={src}
        src={src}
        alt={altText}
        loading="lazy"
        decoding="async"
        onLoad={handleLoad}
        onError={handleError}
        className={`w-full h-full object-contain transition-opacity duration-300 ${stage === 'loaded' ? 'opacity-100' : 'opacity-0'}`}
      />
    </div>
  );
};
