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
        self._items_cache: Dict[int, CatalogItem] = {}
        self._categories_cache: List[str] = []
        self._initialized: bool = False

    def initialize_from_metadata(self):
        """Pre-populates catalog cache from BigBasket parquet metadata."""
        if self._initialized:
            return

        df = feature_store.product_metadata
        if df is not None:
            self._categories_cache = sorted(df["category"].dropna().unique().tolist())
            for _, row in df.iterrows():
                pid = int(row["product_id"])
                # Extract margin reference if available, else standard 20%
                margin_ref = float(row.get("margin_reference", 0.0))
                margin_pct = round(margin_ref * 100.0, 2) if margin_ref > 0 else 20.00
                price = float(row.get("sale_price", 299.0))
                
                item = CatalogItem(
                    item_id=pid,
                    name=str(row.get("product", f"Product #{pid}")),
                    category_name=str(row.get("category", "General")),
                    subcategory=str(row.get("sub_category", "")),
                    brand=str(row.get("brand", "")),
                    price=price,
                    margin_pct=margin_pct,
                    inventory_count=100,
                    quality_score=0.75,
                    business_priority=0.0,
                    source="bigbasket",
                    source_id=pid,
                )
                self._items_cache[pid] = item

            # Add seeded cold-start demo item
            cold_item = CatalogItem(
                item_id=999999998,
                name="Demo Running Shoe",
                category_name="Sports",
                subcategory="Running",
                brand="DemoBrand",
                price=4999.00,
                margin_pct=35.00,
                inventory_count=100,
                quality_score=0.90,
                business_priority=0.80,
                source="synthetic_cold",
                source_id=999999998,
                is_cold_demo=True,
            )
            self._items_cache[999999998] = cold_item

        self._initialized = True

    def get_item(self, item_id: int) -> Optional[CatalogItem]:
        if not self._initialized:
            self.initialize_from_metadata()
        return self._items_cache.get(item_id)

    def get_all_categories(self) -> List[str]:
        if not self._initialized:
            self.initialize_from_metadata()
        return self._categories_cache

    def get_items_by_category(self, category_name: str, limit: int = 50) -> List[CatalogItem]:
        if not self._initialized:
            self.initialize_from_metadata()
        matches = [
            item for item in self._items_cache.values()
            if item.category_name.lower() == category_name.lower()
        ]
        return matches[:limit]


catalog = UnifiedCatalog()
