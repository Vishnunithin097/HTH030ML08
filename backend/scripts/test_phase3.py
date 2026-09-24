"""
Phase 3 Unit Test Suite.
Validates:
1. Collaborative Filtering Scoring & Dimensions
2. Content-Based TF-IDF Profile & Cosine Matching
3. Hybrid Score Fusion (ML Relevance)
4. Cold-Start Detection & Fallbacks
5. Business Guardrail Scoring & Penalties
6. Re-Ranking (Pure vs Business-Aware)
7. Counterfactual Sensitivity Simulation
8. Signal-Derived Explainability
9. MMR & Intra-List Diversity
10. Evaluation Metrics (NDCG, Recall, Precision, MAP, Business Lift)
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.feature_extraction import feature_store
from app.core.catalog import catalog, CatalogItem
from app.recommenders.collaborative import collaborative_recommender
from app.recommenders.content_based import content_recommender
from app.recommenders.hybrid import hybrid_recommender
from app.recommenders.cold_start import cold_start_engine
from app.business.guardrails import GuardrailPolicy, guardrail_evaluator
from app.business.reranker import reranker
from app.business.revenue_impact import revenue_calculator
from app.explainability.explain import explainability_engine
from app.diversity.diversity import diversity_engine
from app.evaluation.ranking_metrics import compute_precision_at_k, compute_recall_at_k, compute_ndcg_at_k, compute_map
from app.evaluation.coldstart_metrics import compute_cold_category_hit_rate
from app.evaluation.business_metrics import compute_average_margin, compute_business_lift_metrics


def run_unit_tests():
    print("==================================================")
    print("           PHASE 3 UNIT TEST SUITE                ")
    print("==================================================")

    # 1. Collaborative Filtering
    print("[1] Testing Collaborative Recommender...")
    # User 0 and Item 3 exist in RetailRocket encoders
    cf_score = collaborative_recommender.predict_score(user_id=0, item_id=3)
    assert cf_score is not None, "Collaborative score should not be None for seen entities"
    assert 0.0 <= cf_score <= 1.0, f"CF score {cf_score} out of [0, 1] bounds"
    
    # Unseen user returns None gracefully
    unseen_cf = collaborative_recommender.predict_score(user_id=999999999, item_id=3)
    assert unseen_cf is None, "CF score for unseen user must be None"

    # Item similarity test
    item_sim = collaborative_recommender.item_similarity(3, 4)
    assert item_sim is not None and 0.0 <= item_sim <= 1.0
    print("  [+] CF scoring & item similarity verified.")

    # 2. Content-Based Recommender
    print("\n[2] Testing Content-Based Recommender...")
    user_vec = content_recommender.build_user_profile_vector(
        interacted_product_ids=[0, 1],
        category_preferences=["Beauty & Hygiene"]
    )
    assert user_vec is not None, "User content vector synthesis failed"
    content_score = content_recommender.predict_score(user_vec, product_id=0)
    assert content_score is not None and 0.0 <= content_score <= 1.0
    
    prod_sim = content_recommender.item_similarity(0, 4)
    assert prod_sim is not None and 0.0 <= prod_sim <= 1.0
    print("  [+] Content vector synthesis & cosine similarity verified.")

    # 3. Hybrid Recommender
    print("\n[3] Testing Hybrid Recommender...")
    catalog.initialize_from_metadata()
    candidates = list(catalog._items_cache.values())[:30]
    hybrid_res = hybrid_recommender.recommend(
        user_id=111016,
        interaction_count=10,
        interacted_item_ids=[0, 1],
        candidate_items=candidates,
        limit=10,
    )
    assert len(hybrid_res) == 10
    for r in hybrid_res:
        assert "relevance_score" in r
        assert 0.0 <= r["relevance_score"] <= 1.0
    print("  [+] Hybrid recommendation candidate fusion verified.")

    # 4. Cold-Start Engine
    print("\n[4] Testing Cold-Start Engine...")
    assert cold_start_engine.is_cold_user(interaction_count=0) is True
    assert cold_start_engine.is_cold_user(interaction_count=5) is False
    assert cold_start_engine.is_cold_item(interaction_count=0) is True
    
    cold_res = cold_start_engine.recommend_for_cold_user(
        user_id=999999999,
        selected_categories=["Beauty & Hygiene"],
        candidate_items=candidates,
        limit=5,
    )
    assert len(cold_res) == 5
    assert all(c["is_cold_start"] is True for c in cold_res)
    assert all(c["collaborative_score"] is None for c in cold_res)
    print("  [+] Cold-start shopper detection and recommendation verified.")

    # 5. Business Guardrails & Scoring
    print("\n[5] Testing Business Guardrails & Scoring...")
    policy = GuardrailPolicy(min_inventory=10, min_margin=20.0)
    biz_score = guardrail_evaluator.compute_business_score(margin_pct=35.0, inventory_count=80, quality_score=0.9, policy=policy)
    assert 0.0 <= biz_score <= 1.0
    
    # Soft penalty test for low stock
    penalty, reasons = guardrail_evaluator.compute_penalty(margin_pct=25.0, inventory_count=4, policy=policy)
    assert penalty > 0.0
    assert any("inventory" in r.lower() for r in reasons)

    # Hard filter test
    strict_policy = GuardrailPolicy(min_inventory=10, hard_filter_enabled=True)
    passes, reason = guardrail_evaluator.passes_hard_filters(margin_pct=30.0, inventory_count=2, policy=strict_policy)
    assert passes is False
    print("  [+] Business scoring, soft penalties, and hard filters verified.")

    # 6. Re-Ranking (Pure vs Business-Aware)
    print("\n[6] Testing Re-Ranker...")
    pure_slate, pure_diag = reranker.rank(hybrid_res, mode="pure", policy=policy, top_k=5)
    biz_slate, biz_diag = reranker.rank(hybrid_res, mode="business_aware", policy=policy, top_k=5)
    assert len(pure_slate) == 5
    assert len(biz_slate) == 5
    assert pure_diag["mode"] == "pure"
    assert biz_diag["mode"] == "business_aware"
    assert "churn_count" in biz_diag
    print("  [+] Pure vs Business-Aware re-ranking & churn tracking verified.")

    # 7. Counterfactual Simulation
    print("\n[7] Testing Counterfactual Simulation...")
    cf = guardrail_evaluator.evaluate_counterfactual(
        relevance_score=0.80,
        margin_pct=15.0,
        inventory_count=100,
        quality_score=0.85,
        current_final_score=0.65,
        hypothetical_min_margin=10.0,  # lower margin floor removes penalty
        policy=policy,
    )
    assert "simulated_score" in cf
    assert "score_delta" in cf
    print("  [+] Counterfactual sensitivity analysis verified.")

    # 8. Explainability Engine
    print("\n[8] Testing Signal-Backed Explainability...")
    exp_cold = explainability_engine.explain(cold_res[0], is_cold_user=True)
    assert "Cold-Start" in exp_cold or "introductory" in exp_cold
    
    exp_warm = explainability_engine.explain(biz_slate[0])
    assert len(exp_warm) > 10
    print("  [+] Verifiable explanations verified.")

    # 9. Diversity & MMR
    print("\n[9] Testing Diversity & MMR...")
    div_score = diversity_engine.compute_intra_list_diversity(biz_slate)
    assert 0.0 <= div_score <= 1.0
    
    mmr_slate = diversity_engine.mmr_rerank(hybrid_res, top_k=5, diversity_lambda=0.7)
    assert len(mmr_slate) == 5
    print("  [+] Intra-list diversity & MMR re-ranking verified.")

    # 10. Evaluation Metrics
    print("\n[10] Testing Evaluation Metrics Suite...")
    recs = [1, 2, 3, 4, 5]
    gt = {2, 4, 6, 8}
    p5 = compute_precision_at_k(recs, gt, k=5)
    r5 = compute_recall_at_k(recs, gt, k=5)
    ndcg5 = compute_ndcg_at_k(recs, gt, k=5)
    map5 = compute_map(recs, gt, k=5)
    assert p5 == 0.4  # 2 hits out of 5
    assert r5 == 0.5  # 2 hits out of 4
    assert ndcg5 > 0.0
    assert map5 > 0.0

    hit_rate = compute_cold_category_hit_rate(cold_res, ["Beauty & Hygiene"])
    assert 0.0 <= hit_rate <= 1.0

    lift_res = compute_business_lift_metrics([pure_slate], [biz_slate])
    assert "margin_lift_pct" in lift_res
    print("  [+] Precision, Recall, NDCG, MAP, Cold hit rate, and Business lift verified.")

    print("\n==================================================")
    print("      ALL 10 PHASE 3 UNIT TESTS PASSED!          ")
    print("==================================================")


if __name__ == "__main__":
    run_unit_tests()
