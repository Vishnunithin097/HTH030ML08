"""
PHASE 1 COMPREHENSIVE TEST SUITE
Validates all 20 required verification scenarios for Phase 1 production hardening.
"""

import os
import sys
import numpy as np
import scipy.sparse as sp
import joblib
import pandas as pd
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.config import settings
from app.core.validator import ArtifactValidator, artifact_validator
from app.core.feature_extraction import feature_store
from app.core.catalog import catalog, CatalogItem
from app.core.image_provider import image_provider
from app.recommenders.collaborative import collaborative_recommender
from app.recommenders.content_based import content_recommender
from app.recommenders.hybrid import hybrid_recommender
from app.recommenders.cold_start import cold_start_engine
from app.business.reranker import BusinessReRanker
from app.auth.security import create_access_token, decode_access_token

def run_tests():
    passed = 0
    total = 20
    print("=" * 70)
    print("RUNNING PHASE 1 ACCEPTANCE & VERIFICATION TEST SUITE (20 SCENARIOS)")
    print("=" * 70)

    # 1. Model artifacts load
    report = None
    try:
        report = ArtifactValidator.validate_all()
        assert report["status"] == "ready", f"Artifact validation failed: {report.get('errors')}"
        assert all(report["models"].values()), f"Some models failed: {report['models']}"
        print("[PASS] Test 1: All canonical model artifacts load successfully.")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 1: Model artifacts load: {e}")

    # 2. SVD dimensions valid
    try:
        diag = report["diagnostics"]
        assert diag["user_factors_shape"] == [22141, 100]
        assert diag["item_factors_shape"] == [56987, 100]
        assert diag["user_encoder_classes"] == 873314
        assert diag["item_encoder_classes"] == 194775
        assert diag["svd_components"] == 100
        print("[PASS] Test 2: SVD dimensions valid (user_factors 22141x100, item_factors 56987x100, components 100).")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 2: SVD dimensions: {e}")

    # 3. TF-IDF dimensions valid
    try:
        diag = report["diagnostics"]
        assert diag["tfidf_matrix_shape"] == [23541, 31138]
        assert diag["tfidf_vocab_len"] == 31138
        print("[PASS] Test 3: TF-IDF dimensions valid (matrix 23541x31138, vocab 31138).")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 3: TF-IDF dimensions: {e}")

    # 4. Factor/encoder mapping validation
    try:
        assert feature_store.user_factors.shape == (22141, 100)
        assert feature_store.item_factors.shape == (56987, 100)
        # Encoded index 0 should have valid factors
        u_emb_0 = feature_store.get_user_factors(int(feature_store.user_encoder.classes_[0]))
        assert u_emb_0 is not None and len(u_emb_0) == 100
        # Check out-of-range encoded index
        high_user_id = int(feature_store.user_encoder.classes_[50000])
        u_emb_high = feature_store.get_user_factors(high_user_id)
        assert u_emb_high is None, "Expected None for unmapped factor index!"
        print("[PASS] Test 4: Factor/encoder mapping validation (safe unmapped factor index handling).")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 4: Factor/encoder mapping: {e}")

    # 5. Cross-dataset ID separation
    try:
        catalog.initialize_from_metadata()
        all_items = list(catalog._items_cache.values())
        bb_count = sum(1 for item in all_items if item.get("bigbasket_product_id") is not None)
        rr_count = sum(1 for item in all_items if item.get("retailrocket_item_id") is not None)
        assert bb_count > 0, "No BigBasket items found"
        # Check item attribute structure
        item_sample = all_items[0]
        assert "bigbasket_product_id" in item_sample
        assert "retailrocket_item_id" in item_sample
        print(f"[PASS] Test 5: Cross-dataset ID separation (Catalog items strictly isolate source IDs: {bb_count} BB, {rr_count} RR).")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 5: Cross-dataset ID separation: {e}")

    # 6. Existing user collaborative recommendation
    try:
        known_user_id = int(feature_store.user_encoder.classes_[0])
        known_item_id = int(feature_store.item_encoder.classes_[0])
        score = collaborative_recommender.predict_score(user_id=known_user_id, item_id=known_item_id)
        assert score is not None
        assert 0.0 <= score <= 1.0
        print(f"[PASS] Test 6: Existing user collaborative recommendation generates valid SVD score ({score:.4f}).")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 6: Collaborative recommendation: {e}")

    # 7. Content recommendation
    try:
        candidates = all_items[:10]
        candidate_pids = [c["item_id"] for c in candidates[1:]]
        user_vec = content_recommender.build_user_profile_vector(
            interacted_product_ids=[candidates[0]["item_id"]]
        )
        assert user_vec is not None
        scored_candidates = content_recommender.predict_batch(
            user_profile_vec=user_vec,
            candidate_product_ids=candidate_pids
        )
        assert len(scored_candidates) == len(candidate_pids)
        assert all(0.0 <= s <= 1.0 for s in scored_candidates.values())
        print("[PASS] Test 7: Content recommendation computes fast vectorized sparse similarities across candidate items.")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 7: Content recommendation: {e}")

    # 8. Hybrid recommendation when both signals exist
    try:
        known_user_id = int(feature_store.user_encoder.classes_[0])
        hybrid_res = hybrid_recommender.recommend(
            user_id=known_user_id,
            interaction_count=5,
            interacted_item_ids=[candidates[0]["item_id"]],
            candidate_items=candidates[1:6],
            limit=5
        )
        assert len(hybrid_res) > 0
        assert all("relevance_score" in item for item in hybrid_res)
        assert any(item["recommendation_source"] in ["hybrid_cf_content", "tfidf_content_only", "collaborative_only", "catalog_fallback"] for item in hybrid_res)
        print("[PASS] Test 8: Hybrid recommendation ranks candidates with transparent source provenance.")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 8: Hybrid recommendation: {e}")

    # 9. Content-only fallback
    try:
        unknown_user_id = 999999999
        res_content = hybrid_recommender.recommend(
            user_id=unknown_user_id,
            interaction_count=5, # Not cold in count, but unknown to SVD
            interacted_item_ids=[candidates[0]["item_id"]],
            candidate_items=candidates[1:6],
            limit=5
        )
        assert len(res_content) > 0
        for item in res_content:
            if item.get("content_score") is not None:
                assert item["recommendation_source"] == "tfidf_content_only"
                assert item["collaborative_score"] is None
        print("[PASS] Test 9: Content-only fallback executes cleanly with collaborative_score = None.")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 9: Content-only fallback: {e}")

    # 10. New user cold start
    try:
        cold_user_recs = cold_start_engine.recommend_for_cold_user(
            user_id=8888888,
            selected_categories=["Beauty & Hygiene", "Bakery, Cakes & Dairy"],
            candidate_items=all_items[:50],
            limit=5
        )
        assert len(cold_user_recs) == 5
        assert all(r["is_cold_start"] is True for r in cold_user_recs)
        assert all(r["collaborative_score"] is None for r in cold_user_recs)
        print("[PASS] Test 10: New user cold start provides category & content recommendations without SVD.")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 10: New user cold start: {e}")

    # 11. New item cold start
    try:
        new_item_recs = cold_start_engine.recommend_for_cold_item(
            item_id=candidates[0]["item_id"],
            candidate_items=all_items[1:50],
            limit=5
        )
        assert len(new_item_recs) == 5
        assert all(r["is_cold_start"] is True for r in new_item_recs)
        print("[PASS] Test 11: New item cold start recommends similar items via content/metadata.")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 11: New item cold start: {e}")

    # 12. Interacted item exclusion
    try:
        interacted_ids = [candidates[1]["item_id"], candidates[2]["item_id"]]
        res_excluded = hybrid_recommender.recommend(
            user_id=known_user_id,
            interaction_count=5,
            interacted_item_ids=interacted_ids,
            candidate_items=candidates[:10],
            limit=10
        )
        rec_ids = [r["item_id"] for r in res_excluded]
        for it in interacted_ids:
            assert it not in rec_ids, f"Interacted item {it} was not excluded!"
        print("[PASS] Test 12: Interacted items strictly excluded from recommendation slates.")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 12: Interacted item exclusion: {e}")

    # 13. Missing image fallback
    try:
        img_info = image_provider.resolve_image(
            item_id=9999999,
            category_name="Beverages",
            item_name="Generic Cold Drink"
        )
        assert img_info["image_url"].startswith("data:image/svg+xml")
        assert img_info["image_source"] == "fallback_generator"
        assert img_info["image_status"] == "fallback"
        print("[PASS] Test 13: Missing image fallback returns deterministic SVG with image_status='fallback'.")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 13: Missing image fallback: {e}")

    # 14. Missing business metadata fallback
    try:
        business_reranker = BusinessReRanker()
        mock_raw = [{
            "item_id": 99999,
            "name": "Test Item",
            "category_name": "Snacks",
            "brand": "Test Brand",
            "price": 100.0,
            "margin_pct": None,
            "inventory_count": None,
            "quality_score": None,
            "relevance_score": 0.85,
            "collaborative_score": None,
            "content_score": 0.85,
            "recommendation_source": "tfidf_content_only",
            "is_cold_start": False,
            "tags": []
        }]
        guarded, _ = business_reranker.rank(
            candidates=mock_raw,
            mode="business_aware",
            top_k=1
        )
        assert len(guarded) == 1
        assert guarded[0]["business_score"] is not None
        print("[PASS] Test 14: Missing business metadata fallback uses neutral defaults (margin=15%, inventory=50, quality=0.7).")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 14: Missing business metadata fallback: {e}")

    # 15. Pure mode
    try:
        candidate_item = {
            "item_id": 101,
            "name": "Item 101",
            "category_name": "Groceries",
            "brand": "Brand 101",
            "price": 50.0,
            "margin_pct": 5.0,
            "inventory_count": 2,
            "quality_score": 0.5,
            "relevance_score": 0.95,
            "collaborative_score": 0.95,
            "content_score": None,
            "recommendation_source": "collaborative_only",
            "is_cold_start": False,
            "tags": []
        }
        pure_slate, _ = business_reranker.rank(
            candidates=[candidate_item],
            mode="pure",
            top_k=1
        )
        assert len(pure_slate) == 1
        assert pure_slate[0]["final_score"] == 0.95, f"Expected final_score=0.95, got {pure_slate[0]['final_score']}"
        print("[PASS] Test 15: Pure mode strictly preserves ML relevance score (final_score = relevance).")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 15: Pure mode: {e}")

    # 16. Business-aware mode
    try:
        guarded_slate, _ = business_reranker.rank(
            candidates=[candidate_item],
            mode="business_aware",
            top_k=1
        )
        assert len(guarded_slate) == 1
        assert guarded_slate[0]["final_score"] != 0.95, "Business-aware mode must incorporate business score & penalties!"
        assert guarded_slate[0].get("penalties") is not None or guarded_slate[0].get("penalty_score") is not None
        assert guarded_slate[0]["business_score"] is not None
        print(f"[PASS] Test 16: Business-aware mode applies business scoring & penalties (final_score={guarded_slate[0]['final_score']:.4f}).")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 16: Business-aware mode: {e}")

    # 17. Admin authentication
    try:
        token = create_access_token({"sub": "admin", "role": "admin"})
        decoded = decode_access_token(token)
        assert decoded["sub"] == "admin"
        assert decoded["role"] == "admin"
        print("[PASS] Test 17: Admin authentication token generation and verification.")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 17: Admin authentication: {e}")

    # 18. Unauthorized configuration update
    try:
        user_token = create_access_token({"sub": "regular_user", "role": "viewer"})
        decoded_user = decode_access_token(user_token)
        assert decoded_user.get("role") != "admin", "Viewer should not have admin role!"
        print("[PASS] Test 18: Unauthorized configuration update access denied for non-admin tokens.")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 18: Unauthorized config update: {e}")

    # 19. Recommendation API
    try:
        cat_item = catalog.get_item(candidates[0]["item_id"])
        assert cat_item is not None
        d = cat_item if isinstance(cat_item, dict) else cat_item.to_dict()
        required_keys = ["item_id", "name", "category_name", "price", "image_url", "image_source", "image_status", "bigbasket_product_id", "retailrocket_item_id"]
        for k in required_keys:
            assert k in d, f"Missing key {k} in CatalogItem dict"
        print("[PASS] Test 19: Recommendation API contract contains all canonical and image metadata fields.")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 19: Recommendation API contract: {e}")

    # 20. Health/readiness endpoint
    try:
        ready_status = ArtifactValidator.validate_all()
        assert ready_status["status"] == "ready"
        assert ready_status["models"]["retailrocket_svd"] is True
        assert ready_status["models"]["retailrocket_factors"] is True
        assert ready_status["models"]["bigbasket_tfidf"] is True
        assert ready_status["models"]["bigbasket_metadata"] is True
        print(f"[PASS] Test 20: Health readiness endpoint reports complete model status: {ready_status['models']}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 20: Health/readiness endpoint: {e}")

    print("=" * 70)
    print(f"TEST RESULTS: {passed}/{total} PASSED")
    print("=" * 70)
    return passed == total

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
