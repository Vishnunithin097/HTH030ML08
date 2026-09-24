"""
Hybrid Recommendation Engine.
Combines Collaborative Filtering and Content-Based models with weighted fusion
and seamless cold-start routing.
"""
from typing import List, Dict, Optional, Any
import numpy as np

from app.core.catalog import catalog, CatalogItem
from app.recommenders.collaborative import collaborative_recommender
from app.recommenders.content_based import content_recommender
from app.recommenders.cold_start import cold_start_engine


class HybridRecommender:
    """
    Blends Collaborative Filtering latent factors and Content-Based TF-IDF representations.
    Maintains clean separation between ML relevance fusion and business guardrails.
    """

    def __init__(
        self,
        cf_weight: float = 0.60,
        content_weight: float = 0.40,
        cold_threshold: int = 3,
    ):
        self.cf_weight = cf_weight
        self.content_weight = content_weight
        self.cold_threshold = cold_threshold

    def recommend(
        self,
        user_id: int,
        interaction_count: int = 0,
        interacted_item_ids: List[int] = None,
        selected_categories: List[str] = None,
        candidate_items: List[CatalogItem] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Generates ML candidate recommendations with relevance scores.
        """
        if not candidate_items:
            # Fallback to catalog slice if not explicitly passed
            catalog.initialize_from_metadata()
            candidate_items = list(catalog._items_cache.values())[:200]

        # 1. Cold-Start User Detection
        if cold_start_engine.is_cold_user(interaction_count, threshold=self.cold_threshold):
            return cold_start_engine.recommend_for_cold_user(
                user_id=user_id,
                selected_categories=selected_categories or ["General"],
                candidate_items=candidate_items,
                limit=limit,
            )

        # 2. Build User Content Profile for warm user
        user_profile_vec = content_recommender.build_user_profile_vector(
            interacted_product_ids=interacted_item_ids or [],
            category_preferences=selected_categories or [],
        )

        scored_candidates: List[Dict[str, Any]] = []

        for item in candidate_items:
            # Check for cold-start item
            if item.is_cold_demo:
                cold_scored = cold_start_engine.score_cold_item(
                    cold_item=item,
                    user_category_preferences=selected_categories,
                    user_profile_vec=user_profile_vec,
                )
                scored_candidates.append(cold_scored)
                continue

            # Compute Collaborative Score
            cf_score = collaborative_recommender.predict_score(user_id, item.item_id)

            # Compute Content Score
            content_score = None
            if user_profile_vec is not None:
                content_score = content_recommender.predict_score(user_profile_vec, item.item_id)

            # Determine fusion mode & calculate relevance
            if cf_score is not None and content_score is not None:
                relevance = self.cf_weight * cf_score + self.content_weight * content_score
                source = "hybrid_cf_content"
            elif cf_score is not None:
                relevance = cf_score
                source = "collaborative_only"
            elif content_score is not None:
                relevance = content_score
                source = "content_only"
            else:
                # Baseline category / rating heuristic for unmapped items
                relevance = (item.quality_score or 0.5) * 0.4
                source = "catalog_baseline"

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
                "collaborative_score": round(cf_score, 5) if cf_score is not None else None,
                "content_score": round(content_score, 5) if content_score is not None else None,
                "relevance_score": round(float(np.clip(relevance, 0.0, 1.0)), 5),
                "is_cold_start": False,
                "recommendation_source": source,
            })

        # Sort candidate pool by ML relevance descending
        scored_candidates.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_candidates[:limit]


hybrid_recommender = HybridRecommender()
