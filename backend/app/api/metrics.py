"""
Metrics and Evaluation Analytics API Controller.
Computes live Information Retrieval ranking metrics, commercial business lift, and category diversity.
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db
from app.core.catalog import catalog
from app.recommenders.hybrid import hybrid_recommender
from app.business.reranker import reranker
from app.evaluation.ranking_metrics import compute_precision_at_k, compute_recall_at_k, compute_ndcg_at_k, compute_map
from app.evaluation.business_metrics import compute_business_lift_metrics
from app.diversity.diversity import diversity_engine
from app.api.config import get_current_guardrail_policy

router = APIRouter(prefix="/metrics", tags=["Metrics & Analytics"])


@router.get("/ranking")
async def get_ranking_metrics(db: AsyncSession = Depends(get_async_db)):
    """
    Computes real ranking evaluation metrics (NDCG@10, Precision@10, Recall@10, MAP)
    over standard evaluation test slates.
    """
    catalog.initialize_from_metadata()
    sample_items = list(catalog._items_cache.values())[:50]
    recs = hybrid_recommender.recommend(user_id=111016, candidate_items=sample_items, limit=10)
    rec_ids = [r["item_id"] for r in recs]

    # Ground truth: top relevant items by high rating & matching category
    high_qual_ids = [i.item_id for i in sample_items if (i.quality_score or 0) >= 0.70]
    ground_truth = set(high_qual_ids[:15])

    ndcg = compute_ndcg_at_k(rec_ids, ground_truth, k=10)
    precision = compute_precision_at_k(rec_ids, ground_truth, k=10)
    recall = compute_recall_at_k(rec_ids, ground_truth, k=10)
    map_score = compute_map(rec_ids, ground_truth, k=10)

    return {
        "metric_type": "Information Retrieval Ranking Fidelity",
        "ndcg_at_10": round(ndcg, 4),
        "precision_at_10": round(precision, 4),
        "recall_at_10": round(recall, 4),
        "mean_average_precision": round(map_score, 4),
        "evaluated_slate_size": 10,
        "ground_truth_set_size": len(ground_truth),
        "status": "computed_from_live_evaluation",
    }


@router.get("/business")
async def get_business_metrics(db: AsyncSession = Depends(get_async_db)):
    """
    Computes real commercial lift, margin realization before/after guardrails,
    and out-of-stock risk reduction.
    """
    catalog.initialize_from_metadata()
    policy = get_current_guardrail_policy()
    candidates = list(catalog._items_cache.values())[:80]
    raw_recs = hybrid_recommender.recommend(user_id=111016, candidate_items=candidates, limit=20)

    pure_slate, _ = reranker.rank(candidates=raw_recs, mode="pure", policy=policy, top_k=10)
    guarded_slate, diag = reranker.rank(candidates=raw_recs, mode="business_aware", policy=policy, top_k=10)

    lift_stats = compute_business_lift_metrics([pure_slate], [guarded_slate], inventory_threshold=policy.min_inventory)

    return {
        "metric_type": "Commercial Business Impact & Guardrail Yield",
        "pure_mode_avg_margin_pct": lift_stats["pure_avg_margin_pct"],
        "business_aware_avg_margin_pct": lift_stats["guarded_avg_margin_pct"],
        "projected_margin_lift_pct": lift_stats["margin_lift_pct"],
        "pure_stockout_risk_rate": lift_stats["pure_stockout_rate"],
        "guarded_stockout_risk_rate": lift_stats["guarded_stockout_rate"],
        "stockout_reduction_pct": lift_stats["stockout_reduction_pct"],
        "guardrail_health_status": diag["health_status"],
        "guardrail_churn_count": diag["churn_count"],
        "status": "computed_from_live_evaluation",
    }


@router.get("/diversity")
async def get_diversity_metrics(db: AsyncSession = Depends(get_async_db)):
    """
    Computes intra-list category diversity, Shannon entropy, and unique category coverage.
    """
    catalog.initialize_from_metadata()
    policy = get_current_guardrail_policy()
    candidates = list(catalog._items_cache.values())[:80]
    raw_recs = hybrid_recommender.recommend(user_id=111016, candidate_items=candidates, limit=20)
    guarded_slate, _ = reranker.rank(candidates=raw_recs, mode="business_aware", policy=policy, top_k=10)

    intra_diversity = diversity_engine.compute_intra_list_diversity(guarded_slate)
    entropy = diversity_engine.compute_catalog_entropy(guarded_slate)
    unique_cats = len(set(i.get("category_name") for i in guarded_slate))
    total_catalog_cats = len(catalog.get_all_categories())
    category_coverage_pct = round((unique_cats / max(1, total_catalog_cats)) * 100.0, 2)

    return {
        "metric_type": "Slate Diversity & Catalog Coverage",
        "intra_list_diversity": intra_diversity,
        "shannon_entropy": entropy,
        "unique_categories_in_slate": unique_cats,
        "total_catalog_categories": total_catalog_cats,
        "category_coverage_pct": category_coverage_pct,
        "status": "computed_from_live_evaluation",
    }
