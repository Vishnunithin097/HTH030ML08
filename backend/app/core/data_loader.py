"""
Data loader utilities for model artifacts and datasets.
Loads pre-trained artifacts directly without retraining during application lifecycle.
"""
import os
import joblib
import scipy.sparse as sp
import pandas as pd
from typing import Dict, Any, Optional
from app.config import settings


class ModelArtifactLoader:
    """Manages loading and caching of pre-trained model artifacts."""

    def __init__(self):
        self._artifacts: Dict[str, Any] = {}
        self._loaded: bool = False

    def find_path(self, *relative_paths: str) -> str:
        """Finds first existing path checking models/ and model/ directories."""
        for p in relative_paths:
            if os.path.exists(p):
                return p
        # Fallback to first path
        return relative_paths[0]

    def load_retailrocket_artifacts(self) -> Dict[str, Any]:
        """Loads RetailRocket SVD and factor matrices."""
        rr_dir = self.find_path(settings.RETAILROCKET_DIR, settings.ALT_RETAILROCKET_DIR)
        artifacts = {
            "svd_model": joblib.load(os.path.join(rr_dir, "svd_model.joblib")),
            "user_factors": joblib.load(os.path.join(rr_dir, "user_factors.joblib")),
            "item_factors": joblib.load(os.path.join(rr_dir, "item_factors.joblib")),
            "user_encoder": joblib.load(os.path.join(rr_dir, "user_encoder.joblib")),
            "item_encoder": joblib.load(os.path.join(rr_dir, "item_encoder.joblib")),
        }
        return artifacts

    def load_bigbasket_artifacts(self) -> Dict[str, Any]:
        """Loads BigBasket TF-IDF vectorizer, sparse matrix, and product metadata."""
        bb_dir = self.find_path(settings.BIGBASKET_DIR, settings.ALT_BIGBASKET_DIR)
        artifacts = {
            "tfidf_vectorizer": joblib.load(os.path.join(bb_dir, "tfidf_vectorizer.joblib")),
            "tfidf_matrix": sp.load_npz(os.path.join(bb_dir, "tfidf_matrix.npz")),
            "product_metadata": pd.read_parquet(os.path.join(bb_dir, "product_metadata.parquet")),
        }
        return artifacts


model_loader = ModelArtifactLoader()
