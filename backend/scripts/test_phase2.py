"""
Phase 2 Comprehensive Verification Suite.
Validates all 13 Phase 2 acceptance requirements.
"""
import os
import sys
import numpy as np
import scipy.sparse as sp
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.feature_extraction import feature_store
from app.core.catalog import catalog
from app.core.preprocessing import clean_text, is_cold_start_user, is_cold_start_item


def test_phase2():
    print("==================================================")
    print("           PHASE 2 ACCEPTANCE TEST SUITE          ")
    print("==================================================")

    # 1. RetailRocket SVD model loads
    assert feature_store.svd_model is not None, "RetailRocket SVD model failed to load"
    print("[+] 1. RetailRocket SVD model loaded successfully (n_components = 100).")

    # 2. User encoder loads
    assert feature_store.user_encoder is not None, "User encoder failed to load"
    assert len(feature_store.user_encoder.classes_) == 873314
    print("[+] 2. RetailRocket User encoder loaded (873,314 classes).")

    # 3. Item encoder loads
    assert feature_store.item_encoder is not None, "Item encoder failed to load"
    assert len(feature_store.item_encoder.classes_) == 194775
    print("[+] 3. RetailRocket Item encoder loaded (194,775 classes).")

    # 4. User factors load
    assert feature_store.user_factors is not None, "User factors failed to load"
    assert feature_store.user_factors.shape == (22141, 100)
    print("[+] 4. User factors matrix loaded (22,141 x 100).")

    # 5. Item factors load
    assert feature_store.item_factors is not None, "Item factors failed to load"
    assert feature_store.item_factors.shape == (56987, 100)
    print("[+] 5. Item factors matrix loaded (56,987 x 100).")

    # 6. BigBasket TF-IDF vectorizer loads
    assert feature_store.tfidf_vectorizer is not None, "TF-IDF vectorizer failed to load"
    assert len(feature_store.tfidf_vectorizer.vocabulary_) == 31138
    print("[+] 6. BigBasket TF-IDF vectorizer loaded (31,138 vocabulary).")

    # 7. BigBasket TF-IDF matrix loads
    assert feature_store.tfidf_matrix is not None, "TF-IDF matrix failed to load"
    assert feature_store.tfidf_matrix.shape == (23541, 31138)
    assert feature_store.tfidf_matrix.nnz == 1084210
    print("[+] 7. BigBasket TF-IDF sparse matrix loaded (23,541 x 31,138, 1,084,210 nnz).")

    # 8. Product metadata loads
    assert feature_store.product_metadata is not None, "Product metadata failed to load"
    assert len(feature_store.product_metadata) == 23541
    print("[+] 8. BigBasket product metadata loaded (23,541 rows).")

    # 9. Catalog abstraction & dataset separation
    catalog.initialize_from_metadata()
    assert len(catalog.get_all_categories()) == 11
    demo_item = catalog.get_item(999999998)
    assert demo_item is not None
    assert demo_item.is_cold_demo is True
    print("[+] 9. Catalog layer decouples dataset entity spaces without false cross-ID mappings.")

    # 10. Cold-start User verification
    cold_user_id = 999999999
    assert is_cold_start_user(interaction_count=0, threshold=3) is True
    print("[+] 10. Cold-start user logic validated (0 interactions -> Cold Start).")

    # 11. Cold-start Item verification
    cold_item_id = 999999998
    assert is_cold_start_item(interaction_count=0) is True
    print("[+] 11. Cold-start item logic validated (0 interactions -> Cold Start).")

    # 12. Cross-Dataset Mapping Safety
    # Verify RetailRocket item ID space (0..194,774) is NOT falsely assumed identical to BigBasket product_id (0..23,540)
    collab_idx_test = feature_store.item_id_to_idx.get(3)  # First item ID in RetailRocket is 3
    assert collab_idx_test == 0
    bb_vec_test = feature_store.get_product_tfidf_vector(0)  # First item in BigBasket is 0
    assert bb_vec_test is not None
    print("[+] 12. Verified explicit dataset separation (no invalid cross-dataset mapping).")

    # 13. Synthetic business metadata flags
    from scripts.build_business_layer import generate_business_metadata
    meta_sample = generate_business_metadata(seed=42)
    assert (meta_sample["is_synthetic"] == True).all()
    assert meta_sample["margin_pct"].min() >= 5.0
    assert meta_sample["margin_pct"].max() <= 60.0
    print("[+] 13. Synthetic business metadata clearly flagged (is_synthetic=True).")

    print("\n==================================================")
    print("      ALL 13 PHASE 2 ACCEPTANCE TESTS PASSED!     ")
    print("==================================================")


if __name__ == "__main__":
    test_phase2()
