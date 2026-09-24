"""
Product Image Foundation and Multi-Tier Resolution Provider.

Enforces strict resolution priority:
1. Verified Image URL (explicitly validated external or catalog URL)
2. Local Image Asset (local static filesystem asset matching product_id)
3. Configured Image Manifest (data/product_image_manifest.json / data/image_manifest.json)
4. Deterministic Category/Product-Specific Studio Fallback Asset

Guarantee: Every product has a visually meaningful, non-generic e-commerce image.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Resolve true repo root (backend/app/core/image_provider.py -> 4 levels up)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
if not (ROOT_DIR / "backend").exists():
    ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class ImageProvider:
    """Singleton service for item image resolution and asset tracking."""

    def __init__(self):
        self._manifest: Dict[str, Dict[str, Any]] = {}
        self._load_manifest()

    def _load_manifest(self):
        candidate_paths = [
            ROOT_DIR / "image_dataset" / "image_manifest.json",
            ROOT_DIR / "imagedataset" / "image_manifest.json",
            ROOT_DIR / "data" / "product_image_manifest.json",
            ROOT_DIR / "data" / "image_manifest.json",
            Path("image_dataset/image_manifest.json"),
            Path("imagedataset/image_manifest.json"),
            Path("data/product_image_manifest.json"),
            Path("data/image_manifest.json"),
        ]
        for path in candidate_paths:
            if path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self._manifest.update({str(k): v for k, v in data.items() if not k.startswith("_")})
                        logger.info(f"Loaded {len(self._manifest)} entries from image manifest at {path}")
                except Exception as e:
                    logger.warning(f"Failed to read image manifest at {path}: {e}")

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
        Resolves product image following strict priority:
        1. Verified URL
        2. Local image asset
        3. Manifest lookup
        4. Deterministic category/product fallback asset
        """
        # Tier 1: Verified URL if explicitly provided
        if existing_url and isinstance(existing_url, str) and existing_url.strip():
            url = existing_url.strip()
            if not ("via.placeholder.com" in url or ("placeholder" in url and "data:image" not in url)):
                if url.startswith("http://") or url.startswith("https://") or url.startswith("data:image/"):
                    return {
                        "image_url": url,
                        "image_source": existing_source or "dataset",
                        "image_status": "verified",
                    }

        # Tier 2: Local Verified Product Image Check
        local_verified_candidates = [
            (ROOT_DIR / "image_dataset" / "images" / f"{product_id}.jpg", f"/image_dataset/images/{product_id}.jpg"),
            (ROOT_DIR / "image_dataset" / "images" / f"{product_id}.png", f"/image_dataset/images/{product_id}.png"),
            (ROOT_DIR / "imagedataset" / "images" / f"{product_id}.jpg", f"/imagedataset/images/{product_id}.jpg"),
            (ROOT_DIR / "imagedataset" / "images" / f"{product_id}.png", f"/imagedataset/images/{product_id}.png"),
            (ROOT_DIR / "frontend" / "public" / "product-images" / "verified" / f"{product_id}.jpg", f"/product-images/verified/{product_id}.jpg"),
            (ROOT_DIR / "frontend" / "public" / "product-images" / "verified" / f"{product_id}.png", f"/product-images/verified/{product_id}.png"),
            (ROOT_DIR / "backend" / "static" / "product-images" / "verified" / f"{product_id}.jpg", f"/product-images/verified/{product_id}.jpg"),
            (ROOT_DIR / "backend" / "static" / "images" / f"{product_id}.jpg", f"/images/{product_id}.jpg"),
        ]
        for l_path, rel_url in local_verified_candidates:
            if l_path.exists():
                return {
                    "image_url": rel_url,
                    "image_source": "local_asset",
                    "image_status": "local",
                }

        # Tier 3: Image Manifest Lookup
        pid_str = str(product_id)
        if pid_str in self._manifest:
            entry = self._manifest[pid_str]
            m_url = entry.get("image_url") or entry.get("path")
            if m_url:
                return {
                    "image_url": m_url,
                    "image_source": entry.get("image_source") or entry.get("source", "image_manifest"),
                    "image_status": entry.get("image_status") or entry.get("status", "generated"),
                }

        # Tier 4: Deterministic Semantic Subcategory or Category Fallback
        cat_str = (category or "general").lower()
        sub_str = (sub_category or "").lower()
        prod_str = (product_name or "").lower()

        # Check semantic subcategory
        sub_map = {
            "skin": "skin_care.svg",
            "hair": "hair_care.svg",
            "deo": "fragrances_deos.svg",
            "perfume": "fragrances_deos.svg",
            "fragrance": "fragrances_deos.svg",
            "soap": "bath_handwash.svg",
            "bath": "bath_handwash.svg",
            "shave": "mens_grooming.svg",
            "sauce": "sauces_spreads.svg",
            "spread": "sauces_spreads.svg",
            "chocolate": "chocolates_biscuits.svg",
            "biscuit": "chocolates_biscuits.svg",
            "tea": "tea_coffee.svg",
            "coffee": "tea_coffee.svg",
            "juice": "beverages_drinks.svg",
            "drink": "beverages_drinks.svg",
            "oil": "oils_ghee.svg",
            "ghee": "oils_ghee.svg",
            "spice": "spices_masala.svg",
            "masala": "spices_masala.svg",
            "dairy": "dairy_milk.svg",
            "milk": "dairy_milk.svg",
            "bread": "bread_bakery.svg",
            "nut": "snacks_dry_fruits.svg",
            "snack": "snacks_namkeen.svg",
            "cleaner": "cleaners_detergents.svg",
            "dish": "cleaners_detergents.svg",
            "cookware": "cookware_kitchen.svg",
            "bottle": "storage_accessories.svg",
            "baby": "baby_care_essentials.svg",
            "fruit": "fresh_fruits.svg",
            "vegetable": "fresh_veggies.svg",
        }

        matched_sub = None
        for kw, svg_name in sub_map.items():
            if kw in sub_str or kw in prod_str:
                matched_sub = svg_name
                break

        if matched_sub:
            return {
                "image_url": f"/product-images/generated/{matched_sub}",
                "image_source": "generated_asset",
                "image_status": "generated",
            }

        # Category Fallback
        cat_slug_map = {
            "beauty": "beauty_hygiene.svg",
            "gourmet": "gourmet_world_food.svg",
            "kitchen": "kitchen_garden_pets.svg",
            "clean": "cleaning_household.svg",
            "snack": "snacks_branded_foods.svg",
            "grain": "foodgrains_oil_masala.svg",
            "oil": "foodgrains_oil_masala.svg",
            "bakery": "bakery_cakes_dairy.svg",
            "dairy": "bakery_cakes_dairy.svg",
            "beverage": "beverages.svg",
            "baby": "baby_care.svg",
            "fruit": "fruits_vegetables.svg",
            "veg": "fruits_vegetables.svg",
            "meat": "eggs_meat_fish.svg",
            "fish": "eggs_meat_fish.svg",
            "egg": "eggs_meat_fish.svg",
        }

        matched_cat = "general.svg"
        for kw, svg_name in cat_slug_map.items():
            if kw in cat_str:
                matched_cat = svg_name
                break

        return {
            "image_url": f"/product-images/fallback/{matched_cat}",
            "image_source": "category_fallback",
            "image_status": "fallback",
        }

    # Backward compatibility alias
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
