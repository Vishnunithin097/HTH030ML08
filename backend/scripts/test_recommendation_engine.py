"""
Comprehensive Test Suite for Cold-Start Aware Recommendation Engine with Business Guardrails.
Tests all 10 explicit architectural requirements using actual pre-trained ML artifacts.
"""
import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Set up paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from app.core.feature_extraction import feature_store
from app.core.catalog import catalog, CatalogItem
from app.recommenders.collaborative import collaborative_recommender
from app.recommenders.content_based import content_recommender
from app.recommenders.cold_start import cold_start_engine
from app.recommenders.hybrid import hybrid_recommender
from app.business.guardrails import GuardrailPolicy, guardrail_evaluator
from app.business.reranker import reranker
from app.explainability.explain import explainability_engine


def test_10_model_artifacts_loaded():
    """Requirement 10: Model artifacts load successfully."""
    print("\n--- Test 10: Pre-Trained ML Artifacts Loading ---")
    feature_store.load_artifacts()
    
    assert feature_store.svd_model is not None, "SVD model must be loaded"
    assert feature_store.user_factors is not None, "User factors matrix must be loaded"
    assert feature_store.item_factors is not None, "Item factors matrix must be loaded"
    assert feature_store.user_encoder is not None, "User encoder must be loaded"
    assert feature_store.item_encoder is not None, "Item encoder must be loaded"
    assert feature_store.tfidf_vectorizer is not None, "TF-IDF vectorizer must be loaded"
    assert feature_store.tfidf_matrix is not None, "TF-IDF matrix must be loaded"
    assert feature_store.product_metadata is not None, "Product metadata must be loaded"

    print(f"  [PASS] SVD Latent Components: {feature_store.svd_model.n_components}")
    print(f"  [PASS] User Factors Shape: {feature_store.user_factors.shape}")
    print(f"  [PASS] Item Factors Shape: {feature_store.item_factors.shape}")
    print(f"  [PASS] TF-IDF Matrix Shape: {feature_store.tfidf_matrix.shape}")
    print(f"  [PASS] Catalog Metadata Items: {len(feature_store.product_metadata)}")


def test_01_existing_user_svd_recommendation():
    """Requirement 1: Existing user -> SVD collaborative recommendation."""
    print("\n--- Test 1: Existing User SVD Recommendation ---")
    # Pick a known user from RetailRocket encoder
    known_users = list(feature_store.user_id_to_idx.keys())
    assert len(known_users) > 0, "Known users must exist in feature store"
    sample_user_id = known_users[0]

    assert collaborative_recommender.is_user_available(sample_user_id) is True

    # Generate collaborative recommendations
    recs = collaborative_recommender.recommend(
        user_id=sample_user_id,
        top_k=5,
    )
    assert len(recs) == 5, f"Expected 5 recommendations, got {len(recs)}"
    for idx, r in enumerate(recs):
        assert "collaborative_score" in r, "Must contain collaborative score"
        assert 0.0 <= r["collaborative_score"] <= 1.0, "Score must be bounded in [0, 1]"
        assert r["rank"] == idx + 1, "Rank must be 1-indexed ordered"

    print(f"  [PASS] Existing User #{sample_user_id} produced {len(recs)} top SVD recommendations.")
    print(f"  [PASS] Top SVD score: {recs[0]['collaborative_score']} (Item #{recs[0]['item_id']})")


def test_02_unknown_user_cold_start():
    """Requirement 2: Unknown/new user -> Cold-start recommendation."""
    print("\n--- Test 2: Unknown/New User Cold-Start Recommendation ---")
    unknown_user_id = 999_999_999  # Unseen user ID
    
    assert collaborative_recommender.is_user_available(unknown_user_id) is False
    assert cold_start_engine.is_cold_user(interaction_count=0) is True

    catalog.initialize_from_metadata()
    candidates = list(catalog._items_cache.values())[:50]

    recs = cold_start_engine.recommend_for_cold_user(
        user_id=unknown_user_id,
        selected_categories=["Snacks & Branded Foods", "Beverages"],
        candidate_items=candidates,
        limit=5,
    )

    assert len(recs) == 5
    for r in recs:
        assert r["is_cold_start"] is True, "Must be tagged cold start"
        assert r["collaborative_score"] is None, "Collaborative score must be None for cold user (not fake 0.0)"
        assert r["recommendation_source"] == "cold_start_category_content"
        assert 0.0 <= r["relevance_score"] <= 1.0

    print(f"  [PASS] Cold-start user #{unknown_user_id} correctly routed to ColdStartEngine.")
    print(f"  [PASS] Strategy marked as cold-start, collaborative_score=None, relevance={recs[0]['relevance_score']}")


def test_03_existing_user_hybrid_recommendation():
    """Requirement 3: Existing user -> Hybrid recommendation combining CF and Content."""
    print("\n--- Test 3: Existing User Hybrid Recommendation ---")
    known_users = list(feature_store.user_id_to_idx.keys())
    sample_user_id = known_users[0]

    catalog.initialize_from_metadata()
    candidates = list(catalog._items_cache.values())[:50]

    recs = hybrid_recommender.recommend(
        user_id=sample_user_id,
        interaction_count=10,  # Warm user
        interacted_item_ids=[candidates[0]["item_id"], candidates[1]["item_id"]],
        selected_categories=["Snacks & Branded Foods"],
        candidate_items=candidates,
        limit=5,
    )

    assert len(recs) > 0
    for r in recs:
        assert "relevance_score" in r
        assert 0.0 <= r["relevance_score"] <= 1.0

    print(f"  [PASS] Warm User #{sample_user_id} received {len(recs)} hybrid scored candidates.")
    print(f"  [PASS] Top candidate #{recs[0]['item_id']} relevance={recs[0]['relevance_score']}")


def test_04_new_item_content_based_recommendation():
    """Requirement 4: New item -> Content-based recommendation without CF dependency."""
    print("\n--- Test 4: New Item Content-Based Recommendation ---")
    new_demo_item = CatalogItem(
        item_id=888_888_888,
        name="Organic Artisanal Cold Brew Coffee",
        category_name="Beverages",
        subcategory="Coffee",
        brand="Artisan Craft",
        price=350.0,
        margin_pct=35.0,
        inventory_count=50,
        quality_score=0.90,
        business_priority=0.80,
        is_cold_demo=True,
    )

    scored = cold_start_engine.score_cold_item(
        cold_item=new_demo_item,
        user_category_preferences=["Beverages"],
    )

    assert scored["is_cold_start"] is True
    assert scored["collaborative_score"] is None, "Cold item must not require SVD factors"
    assert scored["relevance_score"] > 0.0
    assert scored["recommendation_source"] == "cold_start_item_boost"

    print(f"  [PASS] New Item #{new_demo_item.item_id} successfully scored via content & strategic metadata.")
    print(f"  [PASS] Collaborative score is None, content relevance={scored['relevance_score']}")


def test_05_interacted_items_excluded():
    """Requirement 5: Already interacted items -> Excluded from recommendations."""
    print("\n--- Test 5: Interacted Items Exclusion ---")
    catalog.initialize_from_metadata()
    candidates = list(catalog._items_cache.values())[:30]
    excluded_item_id = candidates[0]["item_id"]
    known_users = list(feature_store.user_id_to_idx.keys())
    sample_user_id = known_users[0]

    recs = hybrid_recommender.recommend(
        user_id=sample_user_id,
        interaction_count=5,
        interacted_item_ids=[excluded_item_id],
        candidate_items=candidates,
        limit=10,
    )

    recommended_ids = [r["item_id"] for r in recs]
    assert excluded_item_id not in recommended_ids, f"Interacted item #{excluded_item_id} must be excluded!"

    print(f"  [PASS] Interacted item #{excluded_item_id} successfully excluded from top recommendations.")


def test_06_pure_mode_relevance_ranking():
    """Requirement 6: Pure mode -> Pure relevance-based ranking."""
    print("\n--- Test 6: Pure Engagement Mode Ranking ---")
    mock_candidates = [
        {"item_id": 1, "name": "Item A", "relevance_score": 0.95, "margin_pct": 5.0, "inventory_count": 2},
        {"item_id": 2, "name": "Item B", "relevance_score": 0.80, "margin_pct": 40.0, "inventory_count": 100},
        {"item_id": 3, "name": "Item C", "relevance_score": 0.70, "margin_pct": 50.0, "inventory_count": 200},
    ]

    slate, diag = reranker.rank(candidates=mock_candidates, mode="pure", top_k=3)

    assert slate[0]["item_id"] == 1, "Pure mode must rank item with highest relevance (0.95) at #1"
    assert slate[1]["item_id"] == 2
    assert slate[2]["item_id"] == 3
    assert diag["mode"] == "pure"
    assert slate[0]["guardrail_applied"] is False

    print(f"  [PASS] Pure mode ranks strictly by relevance: 1st={slate[0]['item_id']} (rel={slate[0]['final_score']})")


def test_07_business_aware_mode_guardrail_reranking():
    """Requirement 7: Business-aware mode -> Guardrail re-ranking with soft penalties & multi-objective scoring."""
    print("\n--- Test 7: Business-Aware Guardrail Re-Ranking ---")
    mock_candidates = [
        {"item_id": 1, "name": "Low Margin Out-of-Stock", "relevance_score": 0.95, "margin_pct": 5.0, "inventory_count": 2, "quality_score": 0.5, "business_priority": 0.0},
        {"item_id": 2, "name": "High Margin Well-Stocked", "relevance_score": 0.85, "margin_pct": 40.0, "inventory_count": 100, "quality_score": 0.9, "business_priority": 0.5},
        {"item_id": 3, "name": "Standard Item", "relevance_score": 0.75, "margin_pct": 25.0, "inventory_count": 50, "quality_score": 0.8, "business_priority": 0.1},
    ]

    policy = GuardrailPolicy(min_margin=10.0, min_inventory=10, business_weight=0.50, relevance_weight=0.50)
    slate, diag = reranker.rank(candidates=mock_candidates, mode="business_aware", policy=policy, top_k=2)

    # Item 1 has 5% margin (<10% threshold) and 2 inventory (<10 threshold) -> soft penalized / filtered
    # Item 2 has high margin + stock -> should overtake Item 1 and displace Item 1 from rank #1
    assert slate[0]["item_id"] == 2, "High-margin well-stocked item should rank #1 in business-aware mode"
    assert slate[0]["guardrail_applied"] is True
    assert "business_score" in slate[0]
    assert diag["churn_count"] >= 1

    print(f"  [PASS] Business-aware mode successfully re-ranked slate: #1 is Item #{slate[0]['item_id']} (score={slate[0]['final_score']})")
    print(f"  [PASS] Churn count: {diag['churn_count']}, suppression rate: {diag['suppression_rate']}")


def test_08_missing_metadata_graceful_fallback():
    """Requirement 8: Missing metadata -> Graceful fallback."""
    print("\n--- Test 8: Missing Metadata Graceful Fallback ---")
    corrupt_candidate = [
        {
            "item_id": 9999,
            "name": None,
            "category_name": None,
            "margin_pct": None,
            "inventory_count": None,
            "quality_score": None,
            "relevance_score": None,
        }
    ]

    slate, diag = reranker.rank(candidates=corrupt_candidate, mode="business_aware", top_k=1)
    assert len(slate) == 1
    assert slate[0]["final_score"] is not None
    assert slate[0]["rank"] == 1

    print(f"  [PASS] Missing metadata item gracefully handled with default imputed parameters. Score={slate[0]['final_score']}")


def test_09_explanation_matches_actual_signals():
    """Requirement 9: Explanation matches actual signals without hallucination."""
    print("\n--- Test 9: Signal-Backed Explainability ---")
    
    # Cold start item
    cold_item = {"category_name": "Beverages", "is_cold_start": True}
    cold_exp = explainability_engine.explain(cold_item, user_category_preferences=["Beverages"], is_cold_user=True)
    assert "Cold-Start" in cold_exp or "Beverages" in cold_exp

    # Collaborative dominant
    cf_item = {"category_name": "Snacks", "brand": "Lays", "recommendation_source": "collaborative_only", "collaborative_score": 0.88}
    cf_exp = explainability_engine.explain(cf_item)
    assert "similar purchase journeys" in cf_exp or "Lays" in cf_exp

    # Content dominant
    content_item = {"category_name": "Dairy", "brand": "Amul", "recommendation_source": "content_only", "content_score": 0.79}
    content_exp = explainability_engine.explain(content_item)
    assert "viewing profile" in content_exp or "Amul" in content_exp or "Dairy" in content_exp

    # Hybrid with guardrails
    hybrid_item = {"category_name": "Bakery", "recommendation_source": "hybrid_cf_content", "guardrail_applied": True, "margin_pct": 35.0, "inventory_count": 80, "quality_score": 0.9}
    hybrid_exp = explainability_engine.explain(hybrid_item)
    assert "in-stock" in hybrid_exp or "hybrid" in hybrid_exp or "co-purchase" in hybrid_exp

    print(f"  [PASS] Cold-start explanation: '{cold_exp}'")
    print(f"  [PASS] CF explanation: '{cf_exp}'")
    print(f"  [PASS] Content explanation: '{content_exp}'")
    print(f"  [PASS] Hybrid guardrail explanation: '{hybrid_exp}'")


def run_all_tests():
    print("=" * 70)
    print("RECOMMENDATION ENGINE & SVD LAYER 10-POINT TEST VERIFICATION")
    print("=" * 70)

    test_10_model_artifacts_loaded()
    test_01_existing_user_svd_recommendation()
    test_02_unknown_user_cold_start()
    test_03_existing_user_hybrid_recommendation()
    test_04_new_item_content_based_recommendation()
    test_05_interacted_items_excluded()
    test_06_pure_mode_relevance_ranking()
    test_07_business_aware_mode_guardrail_reranking()
    test_08_missing_metadata_graceful_fallback()
    test_09_explanation_matches_actual_signals()

    print("\n" + "=" * 70)
    print("ALL 10 TESTS COMPLETED AND VERIFIED 100% SUCCESSFUL!")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()
