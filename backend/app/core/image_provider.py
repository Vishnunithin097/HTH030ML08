"""
Product Image Foundation and Resolution Provider.
Provides deterministic, multi-tiered image resolution without fabricating unverified URLs:
1. Verified Image URL (explicitly validated external or catalog URL)
2. Local Image Asset (local static filesystem asset)
3. Configured Image Manifest (data/image_manifest.json)
4. Deterministic Professional Fallback Placeholder
"""
import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

CATEGORY_FALLBACK_ICONS = {
    "beverages": "☕",
    "beauty & hygiene": "✨",
    "snacks & branded foods": "🍿",
    "foodgrains, oil & masala": "🌾",
    "bakery, cakes & dairy": "🍞",
    "dairy": "🥛",
    "fruits & vegetables": "🍎",
    "gourmet & world food": "🍷",
    "cleaning & household": "🧹",
    "kitchen, garden & pets": "🍳",
    "baby care": "🍼",
    "general": "📦",
}

CATEGORY_FALLBACK_COLORS = {
    "beverages": ("#065f46", "#047857"),
    "beauty & hygiene": ("#831843", "#be185d"),
    "snacks & branded foods": ("#9a3412", "#c2410c"),
    "foodgrains, oil & masala": ("#854d0e", "#a16207"),
    "bakery, cakes & dairy": ("#78350f", "#b45309"),
    "dairy": ("#1e40af", "#2563eb"),
    "fruits & vegetables": ("#14532d", "#16a34a"),
    "gourmet & world food": ("#4c1d95", "#6d28d9"),
    "cleaning & household": ("#0e7490", "#0891b2"),
    "kitchen, garden & pets": ("#374151", "#4b5563"),
    "baby care": ("#9d174d", "#db2777"),
    "general": ("#1f2937", "#374151"),
}


class ImageProvider:
    """Singleton service for item image resolution and asset tracking."""

    def __init__(self):
        self._manifest: Dict[str, Dict[str, Any]] = {}
        self._load_manifest()

    def _load_manifest(self):
        candidate_paths = [
            os.path.join("data", "image_manifest.json"),
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "image_manifest.json"),
            os.path.join(os.path.dirname(__file__), "..", "..", "data", "image_manifest.json"),
        ]
        for path in candidate_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self._manifest = {str(k): v for k, v in data.items() if not k.startswith("_")}
                        logger.info(f"Loaded {len(self._manifest)} entries from image manifest at {path}")
                        return
                except Exception as e:
                    logger.warning(f"Failed to read image manifest at {path}: {e}")

    def generate_fallback_svg(self, item_name: str, category_name: str) -> str:
        """Generates an inline SVG data URI with category-tailored aesthetic."""
        cat_key = (category_name or "general").lower().strip()
        matched_cat = "general"
        for k in CATEGORY_FALLBACK_ICONS:
            if k in cat_key:
                matched_cat = k
                break

        icon = CATEGORY_FALLBACK_ICONS.get(matched_cat, "📦")
        c1, c2 = CATEGORY_FALLBACK_COLORS.get(matched_cat, ("#1f2937", "#374151"))
        
        # Clean item title for display in SVG
        clean_title = (item_name or "Product")[:28].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        cat_title = (category_name or "Catalog Item")[:24].replace("&", "&amp;")

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c2}"/>
    </linearGradient>
  </defs>
  <rect width="400" height="400" rx="16" fill="url(#g)"/>
  <rect x="20" y="20" width="360" height="360" rx="12" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="1.5"/>
  <text x="200" y="170" font-size="64" text-anchor="middle" dominant-baseline="central">{icon}</text>
  <text x="200" y="250" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif" font-size="16" font-weight="600" fill="#ffffff" text-anchor="middle">{clean_title}</text>
  <text x="200" y="280" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif" font-size="12" font-weight="400" fill="rgba(255,255,255,0.7)" text-anchor="middle">{cat_title}</text>
</svg>"""
        import urllib.parse
        encoded = urllib.parse.quote(svg)
        return f"data:image/svg+xml;utf8,{encoded}"

    def resolve_image(
        self,
        item_id: int,
        item_name: Optional[str] = None,
        category_name: Optional[str] = None,
        existing_url: Optional[str] = None,
        existing_source: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Resolves the image following strict waterfall:
        1. Verified existing URL (non-placeholder)
        2. Manifest lookup
        3. Local static asset
        4. Category-tailored SVG fallback
        """
        # Tier 1: Existing URL if explicitly marked verified or real external URL
        if existing_url and isinstance(existing_url, str) and existing_url.strip():
            url = existing_url.strip()
            if not ("via.placeholder.com" in url or "placeholder" in url and "data:image" not in url):
                if url.startswith("http://") or url.startswith("https://") or url.startswith("data:image/"):
                    return {
                        "image_url": url,
                        "image_source": existing_source or "catalog_verified",
                        "image_status": "verified",
                    }

        # Tier 2: Image Manifest
        item_key = str(item_id)
        if item_key in self._manifest:
            entry = self._manifest[item_key]
            m_url = entry.get("image_url")
            if m_url:
                return {
                    "image_url": m_url,
                    "image_source": entry.get("source", "manifest"),
                    "image_status": entry.get("status", "verified"),
                }

        # Tier 3: Local Static Asset Check
        local_asset_path = os.path.join("backend", "static", "images", f"{item_id}.jpg")
        if os.path.exists(local_asset_path):
            return {
                "image_url": f"/static/images/{item_id}.jpg",
                "image_source": "local",
                "image_status": "local",
            }

        # Tier 4: Deterministic Fallback Placeholder
        fallback_svg = self.generate_fallback_svg(
            item_name=item_name or f"Item #{item_id}",
            category_name=category_name or "General",
        )
        return {
            "image_url": fallback_svg,
            "image_source": "fallback_generator",
            "image_status": "fallback",
        }


image_provider = ImageProvider()
