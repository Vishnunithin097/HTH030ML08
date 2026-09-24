"""
Cold-Start Benchmark Evaluation Metrics.
Evaluates category alignment, cold item exposure, and cold shopper hit rates.
"""
from typing import List, Dict, Any, Set


def compute_cold_category_hit_rate(
    recommended_slate: List[Dict[str, Any]],
    user_selected_categories: List[str]
) -> float:
    """
    Computes the fraction of recommended items that belong to the cold user's declared categories.
    """
    if not recommended_slate or not user_selected_categories:
        return 0.0

    target_cats = [c.lower().strip() for c in user_selected_categories if c]
    hits = 0

    for item in recommended_slate:
        cat = (item.get("category_name") or "").lower().strip()
        sub = (item.get("subcategory") or "").lower().strip()
        if any(tc in cat or tc in sub for tc in target_cats):
            hits += 1

    return round(float(hits / len(recommended_slate)), 4)


def compute_cold_item_exposure(
    all_recommended_slates: List[List[Dict[str, Any]]],
    cold_item_ids: Set[int]
) -> Dict[str, Any]:
    """
    Measures catalog exposure and impression share for new/cold-start items across user feeds.
    """
    if not all_recommended_slates or not cold_item_ids:
        return {"total_slates": 0, "cold_item_impressions": 0, "exposure_rate": 0.0}

    total_impressions = sum(len(slate) for slate in all_recommended_slates)
    cold_impressions = sum(
        1 for slate in all_recommended_slates for item in slate if item.get("item_id") in cold_item_ids
    )

    exposure_rate = cold_impressions / max(1, total_impressions)
    return {
        "total_slates": len(all_recommended_slates),
        "total_impressions": total_impressions,
        "cold_item_impressions": cold_impressions,
        "exposure_rate": round(float(exposure_rate), 4),
    }
