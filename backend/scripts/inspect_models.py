"""
Model inspection script to verify artifacts, shapes, and properties.
"""
import os
import sys
import joblib
import scipy.sparse as sp
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.data_loader import model_loader


def inspect():
    print("=== Inspecting RetailRocket Artifacts ===")
    try:
        rr = model_loader.load_retailrocket_artifacts()
        print("[+] SVD Model:", type(rr["svd_model"]), f"(components: {rr['svd_model'].n_components})")
        print("[+] User Factors Shape:", rr["user_factors"].shape)
        print("[+] Item Factors Shape:", rr["item_factors"].shape)
        print("[+] User Encoder Classes:", len(rr["user_encoder"].classes_))
        print("[+] Item Encoder Classes:", len(rr["item_encoder"].classes_))
    except Exception as e:
        print("[-] RetailRocket Error:", e)

    print("\n=== Inspecting BigBasket Artifacts ===")
    try:
        bb = model_loader.load_bigbasket_artifacts()
        print("[+] TF-IDF Vectorizer Vocab:", len(bb["tfidf_vectorizer"].vocabulary_))
        print("[+] TF-IDF Matrix Shape:", bb["tfidf_matrix"].shape, f"(nnz: {bb['tfidf_matrix'].nnz})")
        print("[+] Product Metadata Shape:", bb["product_metadata"].shape)
        print("[+] Product Metadata Columns:", bb["product_metadata"].columns.tolist())
    except Exception as e:
        print("[-] BigBasket Error:", e)


if __name__ == "__main__":
    inspect()
