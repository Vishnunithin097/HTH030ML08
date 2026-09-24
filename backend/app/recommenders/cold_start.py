"""
Explicit Cold-Start Handling Engine.
Resolves zero-interaction and low-interaction shoppers and items using content,
declared category affinities, and popularity signals without falsifying collaborative scores.
"""
from typing import List, Dict, Optional, Any, Tuple
import numpy as np
from app.core.catalog import catalog, CatalogItem
from app.recommenders.content_based import content_recommender
from app.core.preprocessing import clean_text


class ColdStartEngine:
    """
    Identifies cold-start states and generates signal-backed candidate recommendations
    for new shoppers and catalog items.
    """

    def __init__(self, default_threshold: int = 3):
        self.default_threshold = default_threshold

    def is_cold_user(self, interaction_count: int, threshold: Optional[int] = None) -> bool:
        """Determines if a user falls below the interaction volume threshold."""
        th = threshold if threshold is not None else self.default_threshold
        return interaction_count < th

    def is_cold_item(self, interaction_count: int) -> bool:
        """Determines if an item has zero historical interactions."""
        return interaction_count == 0

    def recommend_for_cold_user(
        self,
        user_id: int,
        selected_categories: List[str],
        candidate_items: List[CatalogItem],
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Generates recommendations for a new/cold user based strictly on declared category
        preferences, TF-IDF semantic alignment, and item quality ratings.
        """
        if not candidate_items:
            return []

        # 1. Build query vector from user's selected category preferences
        query_vec = content_recommender.build_user_profile_vector(
            category_preferences=selected_categories
        )

        scored_candidates = []
        normalized_cats = [c.lower().strip() for c in selected_categories if c]

        for item in candidate_items:
            # Check direct category match
            item_cat = (item.category_name or "").lower().strip()
            item_sub = (item.subcategory or "").lower().strip()
            has_cat_match = any(cat in item_cat or cat in item_sub for cat in normalized_cats)

            # Compute content semantic score
            content_score = 0.0
            if query_vec is not None:
                sim = content_recommender.predict_score(query_vec, item.item_id)
                content_score = sim if sim is not None else 0.0

            # Direct category alignment boost
            category_boost = 0.35 if has_cat_match else 0.0
            # Quality & baseline rating score (0.0 to 0.15)
            quality_factor = (item.quality_score or 0.5) * 0.15

            # Total relevance in [0, 1]
            relevance_score = float(np.clip(content_score * 0.5 + category_boost + quality_factor, 0.0, 1.0))

            scored_candidates.append({
                "item_id": item.item_id,
                "name": item.name,
                "category_name": item.category_name,
                "subcategory": item.subcategory,
                "brand": item.brand,
                "price": item.price,
                "margin_pct": item.margin_pct,
                "inventory_count": item.inventory_count,
                "quality_score": item.quality_score,
                "business_priority": item.business_priority,
                "collaborative_score": None,  # Explicitly None (NOT fake 0.0)
                "content_score": round(content_score, 5),
                "relevance_score": round(relevance_score, 5),
                "is_cold_start": True,
                "recommendation_source": "cold_start_category_content",
            })

        # Sort by relevance score descending
        scored_candidates.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_candidates[:limit]

    def score_cold_item(
        self,
        cold_item: CatalogItem,
        user_category_preferences: List[str] = None,
        user_profile_vec = None
    ) -> Dict[str, Any]:
        """
        Evaluates relevance for a cold-start item without collaborative factors.
        """
        content_score = 0.0
        if user_profile_vec is not None:
            sim = content_recommender.predict_score(user_profile_vec, cold_item.item_id)
            content_score = sim if sim is not None else 0.0

        # Business priority auxiliary boost for strategic new item placement
        prio_boost = (cold_item.business_priority or 0.0) * 0.20
        relevance_score = float(np.clip(content_score * 0.8 + prio_boost, 0.0, 1.0))

        return {
            "item_id": cold_item.item_id,
            "name": cold_item.name,
            "category_name": cold_item.category_name,
            "subcategory": cold_item.subcategory,
            "brand": cold_item.brand,
            "price": cold_item.price,
            "margin_pct": cold_item.margin_pct,
            "inventory_count": cold_item.inventory_count,
            "quality_score": cold_item.quality_score,
            "business_priority": cold_item.business_priority,
            "collaborative_score": None,
            "content_score": round(content_score, 5),
            "relevance_score": round(relevance_score, 5),
            "is_cold_start": True,
            "recommendation_source": "cold_start_item_boost",
        }


cold_start_engine = ColdStartEngine()
