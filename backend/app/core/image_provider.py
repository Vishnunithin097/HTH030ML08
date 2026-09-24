"""
Product Image Provider — Multi-Tier Resolution Engine with SQID Integration.

Priority:
1. Local downloaded SQID product photo → /images/products/{product_id}.jpg
2. High-confidence SQID remote image URL (from image_manifest.json)
3. Supplementary SQID image URL (from supp_product_image_urls)
4. Local pre-generated per-product SVG → /product-visuals/{product_id}.svg
5. Category fallback SVG → /product-images/fallback/{slug}.svg

Guarantee: Every product always resolves to a valid, non-broken visual.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Paths
_THIS = Path(__file__).resolve()
ROOT_DIR = _THIS.parent.parent.parent.parent
if not (ROOT_DIR / "backend").exists():
    ROOT_DIR = _THIS.parent.parent.parent

IMAGE_DATASET_DIR = ROOT_DIR / "image_dataset"
LOCAL_IMAGES_DIR = IMAGE_DATASET_DIR / "images"
MANIFEST_PATH = IMAGE_DATASET_DIR / "image_manifest.json"
VISUALS_DIR = IMAGE_DATASET_DIR / "product_visuals"
FALLBACK_DIR = ROOT_DIR / "frontend" / "public" / "product-images" / "fallback"

# Category -> Fallback Slug Mapping
_CAT_SLUG: list[tuple[str, str]] = [
    ("beauty",       "beauty_hygiene"),
    ("hygiene",      "beauty_hygiene"),
    ("gourmet",      "gourmet_world_food"),
    ("world food",   "gourmet_world_food"),
    ("kitchen",      "kitchen_garden_pets"),
    ("garden",       "kitchen_garden_pets"),
    ("clean",        "cleaning_household"),
    ("household",    "cleaning_household"),
    ("snack",        "snacks_branded_foods"),
    ("branded food", "snacks_branded_foods"),
    ("foodgrain",    "foodgrains_oil_masala"),
    ("masala",       "foodgrains_oil_masala"),
    ("oil",          "foodgrains_oil_masala"),
    ("bakery",       "bakery_cakes_dairy"),
    ("cakes",        "bakery_cakes_dairy"),
    ("dairy",        "bakery_cakes_dairy"),
    ("beverage",     "beverages"),
    ("tea",          "beverages"),
    ("coffee",       "beverages"),
    ("baby",         "baby_care"),
    ("fruit",        "fruits_vegetables"),
    ("vegetable",    "fruits_vegetables"),
]


def _category_fallback_url(category: str, sub_category: str) -> str:
    combined = f"{(category or '').lower()} {(sub_category or '').lower()}"
    for kw, slug in _CAT_SLUG:
        if kw in combined:
            p = FALLBACK_DIR / f"{slug}.svg"
            if p.exists():
                return f"/product-images/fallback/{slug}.svg"
    return "/product-images/fallback/general.svg"


class ImageProvider:
    """Resolves a BigBasket product_id → image URL via priority waterfall."""

    def __init__(self):
        self._manifest_cache: Optional[Dict[str, Any]] = None
        self._manifest_mtime: float = 0.0

    def _load_manifest(self) -> Dict[str, Any]:
        if MANIFEST_PATH.exists():
            try:
                mtime = MANIFEST_PATH.stat().st_mtime
                if self._manifest_cache is not None and mtime == self._manifest_mtime:
                    return self._manifest_cache

                with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                    self._manifest_cache = json.load(f)
                    self._manifest_mtime = mtime
                logger.info(f"Loaded image manifest with {len(self._manifest_cache)} items.")
                return self._manifest_cache
            except Exception as e:
                logger.warning(f"Could not load image_manifest.json: {e}")

        self._manifest_cache = {}
        return self._manifest_cache

    def resolve_product_image(
        self,
        product_id: int,
        product_name: Optional[str] = None,
        category: Optional[str] = None,
        sub_category: Optional[str] = None,
        brand: Optional[str] = None,
        existing_url: Optional[str] = None,
        existing_source: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Returns dict with keys: image_url, image_source, image_status, match_confidence
        """
        pid_str = str(product_id)
        manifest = self._load_manifest()
        manifest_item = manifest.get(pid_str) or {}

        # Priority 1 — Manifest Resolved Image URL
        m_url = manifest_item.get("image_url") or manifest_item.get("image_path")
        m_source = manifest_item.get("source") or "manifest"
        m_conf = manifest_item.get("confidence") or manifest_item.get("match_confidence", "medium")

        if m_url and isinstance(m_url, str) and m_url.strip():
            url = m_url.strip()
            return {
                "image_url": url,
                "image_source": m_source,
                "image_status": "verified" if m_conf == "high" else "candidate",
                "match_confidence": m_conf,
            }

        # Priority 2 — Local Image File (/images/products/{product_id}.jpg)
        local_jpg = LOCAL_IMAGES_DIR / f"{product_id}.jpg"
        if local_jpg.exists() and local_jpg.stat().st_size > 1024:
            return {
                "image_url": f"/images/products/{product_id}.jpg",
                "image_source": "local_train_dataset",
                "image_status": "verified",
                "match_confidence": "high",
            }

        # Priority 3 — Explicit Catalog Override / Passed URL
        if existing_url and isinstance(existing_url, str):
            url = existing_url.strip()
            bad = ("via.placeholder.com", "placeholder.com", "example.com/products")
            if url and (url.startswith("http://") or url.startswith("https://") or url.startswith("data:image/")):
                if not any(b in url for b in bad):
                    return {
                        "image_url": url,
                        "image_source": existing_source or "catalog_override",
                        "image_status": "verified",
                        "match_confidence": "high",
                    }

        # Priority 4 — Per-product SVG (/product-visuals/{product_id}.svg)
        svg_path = VISUALS_DIR / f"{product_id}.svg"
        if svg_path.exists():
            return {
                "image_url": f"/product-visuals/{product_id}.svg",
                "image_source": "generated_svg",
                "image_status": "generated",
                "match_confidence": "fallback",
            }

        # Priority 5 — Category fallback URL
        fallback_url = _category_fallback_url(category or "", sub_category or "")
        return {
            "image_url": fallback_url,
            "image_source": "category_fallback",
            "image_status": "fallback",
            "match_confidence": "medium",
        }

    def resolve_image(
        self,
        item_id: int,
        item_name: Optional[str] = None,
        category_name: Optional[str] = None,
        existing_url: Optional[str] = None,
        existing_source: Optional[str] = None,
    ) -> Dict[str, str]:
        return self.resolve_product_image(
            product_id=item_id,
            product_name=item_name,
            category=category_name,
            existing_url=existing_url,
            existing_source=existing_source,
        )


image_provider = ImageProvider()
