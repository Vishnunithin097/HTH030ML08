"""
Comprehensive model artifact inspection script for Phase 2.
"""
import os
import sys
import joblib
import scipy.sparse as sp
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.data_loader import model_loader


def inspect():
    print("==================================================")
    print("      MODEL ARTIFACTS & DATASET INSPECTION        ")
    print("==================================================")

    print("\n[1] RetailRocket Collaborative Filtering Artifacts:")
    try:
        rr = model_loader.load_retailrocket_artifacts()
        print(f"  [+] SVD Model: {type(rr['svd_model'])} (n_components: {rr['svd_model'].n_components})")
        print(f"  [+] User Factors Shape: {rr['user_factors'].shape}, dtype: {rr['user_factors'].dtype}")
        print(f"  [+] Item Factors Shape: {rr['item_factors'].shape}, dtype: {rr['item_factors'].dtype}")
        print(f"  [+] User Encoder Size: {len(rr['user_encoder'].classes_)} IDs (sample: {rr['user_encoder'].classes_[:5]})")
        print(f"  [+] Item Encoder Size: {len(rr['item_encoder'].classes_)} IDs (sample: {rr['item_encoder'].classes_[:5]})")
    except Exception as e:
        print(f"  [-] RetailRocket Error: {e}")

    print("\n[2] BigBasket Content-Based Filtering Artifacts:")
    try:
        bb = model_loader.load_bigbasket_artifacts()
        print(f"  [+] TF-IDF Vectorizer Vocab Size: {len(bb['tfidf_vectorizer'].vocabulary_)}")
        print(f"  [+] TF-IDF Matrix Shape: {bb['tfidf_matrix'].shape}, nnz: {bb['tfidf_matrix'].nnz}")
        print(f"  [+] Product Metadata Records: {len(bb['product_metadata'])}")
        print(f"  [+] Columns: {bb['product_metadata'].columns.tolist()}")
        print(f"  [+] Unique Categories: {bb['product_metadata']['category'].nunique()}")
        print(f"  [+] Unique Subcategories: {bb['product_metadata']['sub_category'].nunique()}")
        print(f"  [+] Unique Brands: {bb['product_metadata']['brand'].nunique()}")
    except Exception as e:
        print(f"  [-] BigBasket Error: {e}")

    print("\n==================================================")
    print("               INSPECTION COMPLETE                ")
    print("==================================================")


if __name__ == "__main__":
    inspect()
