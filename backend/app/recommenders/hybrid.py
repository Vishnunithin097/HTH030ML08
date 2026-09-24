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


def _get_val(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


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
        candidate_items: List[Any] = None,
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
                interacted_item_ids=interacted_item_ids,
                limit=limit,
            )

        # 2. Build User Content Profile for warm user
        user_profile_vec = content_recommender.build_user_profile_vector(
            interacted_product_ids=interacted_item_ids or [],
            category_preferences=selected_categories or [],
        )

        scored_candidates: List[Dict[str, Any]] = []
        excluded_ids = set(interacted_item_ids or [])

        for item in candidate_items:
            item_id = _get_val(item, "item_id")
            if item_id is None or item_id in excluded_ids:
                continue

            # Check for cold-start item
            is_cold_demo = bool(_get_val(item, "is_cold_demo", False) or _get_val(item, "is_synthetic_cold_demo", False))
            if is_cold_demo:
                cold_scored = cold_start_engine.score_cold_item(
                    cold_item=item,
                    user_category_preferences=selected_categories,
                    user_profile_vec=user_profile_vec,
                )
                scored_candidates.append(cold_scored)
                continue

            # Compute Collaborative Score (only if user & item have verified RetailRocket representations)
            cf_score = None
            rr_id = _get_val(item, "retailrocket_item_id")
            if rr_id is not None:
                cf_score = collaborative_recommender.predict_score(user_id, rr_id)
            elif collaborative_recommender.is_item_available(item_id) and collaborative_recommender.is_user_available(user_id):
                cf_score = collaborative_recommender.predict_score(user_id, item_id)

            # Compute Content Score (BigBasket TF-IDF space)
            content_score = None
            bb_id = _get_val(item, "bigbasket_product_id", item_id)
            if user_profile_vec is not None and bb_id is not None:
                content_score = content_recommender.predict_score(user_profile_vec, bb_id)

            # Determine fusion mode & calculate relevance
            if cf_score is not None and content_score is not None:
                relevance = self.cf_weight * cf_score + self.content_weight * content_score
                source = "hybrid_cf_content"
            elif cf_score is not None:
                relevance = cf_score
                source = "collaborative_only"
            elif content_score is not None:
                relevance = content_score
                source = "tfidf_content_only"
            else:
                # Baseline category / rating heuristic for unmapped items
                relevance = float(_get_val(item, "quality_score") or 0.5) * 0.4
                source = "catalog_fallback"

            scored_candidates.append({
                "item_id": item_id,
                "bigbasket_product_id": bb_id,
                "retailrocket_item_id": rr_id,
                "name": _get_val(item, "name"),
                "category_name": _get_val(item, "category_name"),
                "subcategory": _get_val(item, "subcategory"),
                "brand": _get_val(item, "brand"),
                "description": _get_val(item, "description"),
                "price": _get_val(item, "price", 299.0),
                "rating": _get_val(item, "rating", 4.0),
                "image_url": _get_val(item, "image_url"),
                "image_source": _get_val(item, "image_source", "fallback"),
                "image_status": _get_val(item, "image_status", "fallback"),
                "margin_pct": _get_val(item, "margin_pct", 20.0),
                "inventory_count": _get_val(item, "inventory_count", 100),
                "quality_score": _get_val(item, "quality_score", 0.7),
                "business_priority": _get_val(item, "business_priority", 0.0),
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
