"""
Unified Catalog Abstraction Layer.

Decouples the internal database item catalog from:
1. RetailRocket Latent SVD Factor Item Space
2. BigBasket Content TF-IDF Feature Space

IMPORTANT ARCHITECTURAL ENFORCEMENT:
Never assume RetailRocket item_id == BigBasket product_id.
"""
from typing import Dict, Optional, Any, List, Tuple
import pandas as pd
import numpy as np
from app.core.feature_extraction import feature_store


class CatalogItem:
    """Standardized catalog item representation."""

    def __init__(
        self,
        item_id: int,
        name: str,
        category_name: str,
        subcategory: Optional[str] = None,
        brand: Optional[str] = None,
        price: float = 299.0,
        margin_pct: float = 20.0,
        inventory_count: int = 100,
        quality_score: float = 0.5,
        business_priority: float = 0.0,
        source: str = "bigbasket",
        source_id: Optional[int] = None,
        is_cold_demo: bool = False,
    ):
        self.item_id = item_id
        self.name = name
        self.category_name = category_name
        self.subcategory = subcategory
        self.brand = brand
        self.price = price
        self.margin_pct = margin_pct
        self.inventory_count = inventory_count
        self.quality_score = quality_score
        self.business_priority = business_priority
        self.source = source
        self.source_id = source_id if source_id is not None else item_id
        self.is_cold_demo = is_cold_demo

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_id": self.item_id,
            "name": self.name,
            "category_name": self.category_name,
            "subcategory": self.subcategory,
            "brand": self.brand,
            "price": self.price,
            "margin_pct": self.margin_pct,
            "inventory_count": self.inventory_count,
            "quality_score": self.quality_score,
            "business_priority": self.business_priority,
            "source": self.source,
            "is_cold_demo": self.is_cold_demo,
        }


class UnifiedCatalog:
    """Manages catalog item lookup and retrieval across sources."""

    def __init__(self):
        self._items_cache: Dict[int, Dict[str, Any]] = {}
        self._biz_cache: Dict[int, Dict[str, Any]] = {}
        self._users_cache: Dict[int, Dict[str, Any]] = {}
        self._categories_cache: List[str] = []
        self._initialized: bool = False

    def initialize_from_metadata(self):
        """Pre-populates catalog cache from BigBasket parquet metadata."""
        if self._initialized:
            return

        df = feature_store.bigbasket_meta
        if df is not None:
            cat_col = "category" if "category" in df.columns else "category_name"
            if cat_col in df.columns:
                self._categories_cache = sorted(df[cat_col].dropna().unique().tolist())

            for idx, row in df.iterrows():
                pid = int(row.get("index", idx))

                price = float(row.get("sale_price", row.get("market_price", 299.0)))
                # Deterministic synthetic business layer based on pid
                margin = float(15.0 + ((pid * 37) % 35))
                inventory = int(10 + ((pid * 13) % 180))
                quality = float(0.60 + (((pid * 7) % 35) / 100.0))

                item_dict = {
                    "item_id": pid,
                    "name": str(row.get("product", f"Product #{pid}")),
                    "category_name": str(row.get(cat_col, "General")),
                    "subcategory": str(row.get("sub_category", "")),
                    "brand": str(row.get("brand", "")),
                    "price": price,
                    "tags": [str(row.get(cat_col, "General")), str(row.get("brand", ""))],
                    "is_synthetic_cold_demo": False,
                }
                self._items_cache[pid] = item_dict
                self._biz_cache[pid] = {
                    "margin_pct": margin,
                    "inventory_count": inventory,
                    "quality_score": quality,
                    "business_priority": 0.50,
                }

        # Seed Cold Start Demo Entities
        self._items_cache[999999998] = {
            "item_id": 999999998,
            "name": "Demo Organic Herbal Green Tea 100g",
            "category_name": "Beverages",
            "subcategory": "Tea",
            "brand": "Organic Valley",
            "price": 349.00,
            "tags": ["organic", "tea", "herbal", "green tea"],
            "is_synthetic_cold_demo": True,
        }
        self._biz_cache[999999998] = {
            "margin_pct": 35.0,
            "inventory_count": 120,
            "quality_score": 0.90,
            "business_priority": 0.80,
        }

        self._users_cache[999999999] = {
            "user_id": 999999999,
            "selected_categories": ["Beauty & Hygiene", "Beverages"],
            "is_synthetic_cold_demo": True,
        }

        # Seed some warm demo users
        self._users_cache[111016] = {
            "user_id": 111016,
            "selected_categories": ["Beauty & Hygiene", "Gourmet & World Food"],
            "is_synthetic_cold_demo": False,
        }

        self._initialized = True

    def get_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        if not self._initialized:
            self.initialize_from_metadata()
        return self._items_cache.get(item_id)

    def get_business_metadata(self, item_id: int) -> Optional[Dict[str, Any]]:
        if not self._initialized:
            self.initialize_from_metadata()
        return self._biz_cache.get(item_id)

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        if not self._initialized:
            self.initialize_from_metadata()
        return self._users_cache.get(user_id)

    def add_user(self, user_id: int, categories: List[str], is_cold: bool = True):
        if not self._initialized:
            self.initialize_from_metadata()
        self._users_cache[user_id] = {
            "user_id": user_id,
            "selected_categories": categories,
            "is_synthetic_cold_demo": is_cold,
        }

    def add_item(self, item_data: Dict[str, Any]):
        if not self._initialized:
            self.initialize_from_metadata()
        pid = item_data["item_id"]
        self._items_cache[pid] = item_data
        self._biz_cache[pid] = {
            "margin_pct": item_data.get("margin_pct", 25.0),
            "inventory_count": item_data.get("inventory_count", 100),
            "quality_score": item_data.get("quality_score", 0.80),
            "business_priority": item_data.get("business_priority", 0.50),
        }

    def get_all_items(self) -> List[Dict[str, Any]]:
        if not self._initialized:
            self.initialize_from_metadata()
        return list(self._items_cache.values())

    def get_items_by_category(self, category: str, limit: int = 50) -> List[Any]:
        if not self._initialized:
            self.initialize_from_metadata()
        cat_lower = category.lower().strip()
        matched = []
        for item in self._items_cache.values():
            if isinstance(item, dict):
                item_cat = str(item.get("category_name") or "").lower()
                item_sub = str(item.get("subcategory") or "").lower()
            else:
                item_cat = str(getattr(item, "category_name", "") or "").lower()
                item_sub = str(getattr(item, "subcategory", "") or "").lower()
            if cat_lower in item_cat or cat_lower in item_sub:
                matched.append(item)
                if len(matched) >= limit:
                    break
        return matched

    def get_all_users(self) -> List[Dict[str, Any]]:
        if not self._initialized:
            self.initialize_from_metadata()
        return list(self._users_cache.values())

    def get_all_categories(self) -> List[str]:
        if not self._initialized:
            self.initialize_from_metadata()
        return self._categories_cache


catalog_service = UnifiedCatalog()
catalog = catalog_service
