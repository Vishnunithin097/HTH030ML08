"""
Feature Extraction and Artifact Store.
Provides singleton, zero-copy, cached access to pre-trained ML models and matrices.
Does NOT refit or train models during runtime.
"""
import os
import joblib
import scipy.sparse as sp
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple

from app.config import settings


class FeatureStore:
    """Singleton in-memory store for pre-trained model artifacts."""

    _instance: Optional["FeatureStore"] = None

    def __init__(self):
        self._retailrocket_loaded: bool = False
        self._bigbasket_loaded: bool = False

        # RetailRocket Artifacts
        self.svd_model: Optional[Any] = None
        self.user_factors: Optional[np.ndarray] = None
        self.item_factors: Optional[np.ndarray] = None
        self.user_encoder: Optional[Any] = None
        self.item_encoder: Optional[Any] = None
        self.user_id_to_idx: Dict[int, int] = {}
        self.item_id_to_idx: Dict[int, int] = {}

        # BigBasket Artifacts
        self.tfidf_vectorizer: Optional[Any] = None
        self.tfidf_matrix: Optional[sp.csr_matrix] = None
        self.product_metadata: Optional[pd.DataFrame] = None
        self.product_id_to_idx: Dict[int, int] = {}

    @classmethod
    def get_instance(cls) -> "FeatureStore":
        if cls._instance is None:
            cls._instance = FeatureStore()
            cls._instance.initialize_all()
        return cls._instance

    def _find_path(self, *relative_paths: str) -> str:
        for p in relative_paths:
            if os.path.exists(p):
                return p
        return relative_paths[0]

    def initialize_all(self):
        """Loads both RetailRocket and BigBasket artifacts into memory once."""
        self.load_retailrocket()
        self.load_bigbasket()

    def load_retailrocket(self):
        """Loads SVD model, factor matrices, and label encoders."""
        if self._retailrocket_loaded:
            return

        rr_dir = self._find_path(settings.RETAILROCKET_DIR, settings.ALT_RETAILROCKET_DIR)
        svd_path = os.path.join(rr_dir, "svd_model.joblib")
        uf_path = os.path.join(rr_dir, "user_factors.joblib")
        itemf_path = os.path.join(rr_dir, "item_factors.joblib")
        ue_path = os.path.join(rr_dir, "user_encoder.joblib")
        ie_path = os.path.join(rr_dir, "item_encoder.joblib")

        if os.path.exists(svd_path):
            self.svd_model = joblib.load(svd_path)
        if os.path.exists(uf_path):
            self.user_factors = joblib.load(uf_path)
        if os.path.exists(itemf_path):
            self.item_factors = joblib.load(itemf_path)
        if os.path.exists(ue_path):
            self.user_encoder = joblib.load(ue_path)
            if hasattr(self.user_encoder, "classes_"):
                self.user_id_to_idx = {int(uid): idx for idx, uid in enumerate(self.user_encoder.classes_)}
        if os.path.exists(ie_path):
            self.item_encoder = joblib.load(ie_path)
            if hasattr(self.item_encoder, "classes_"):
                self.item_id_to_idx = {int(iid): idx for idx, iid in enumerate(self.item_encoder.classes_)}

        self._retailrocket_loaded = True

    def load_bigbasket(self):
        """Loads TF-IDF vectorizer, sparse matrix, and product metadata."""
        if self._bigbasket_loaded:
            return

        bb_dir = self._find_path(settings.BIGBASKET_DIR, settings.ALT_BIGBASKET_DIR)
        vec_path = os.path.join(bb_dir, "tfidf_vectorizer.joblib")
        mat_path = os.path.join(bb_dir, "tfidf_matrix.npz")
        meta_path = os.path.join(bb_dir, "product_metadata.parquet")

        if os.path.exists(vec_path):
            self.tfidf_vectorizer = joblib.load(vec_path)
        if os.path.exists(mat_path):
            self.tfidf_matrix = sp.load_npz(mat_path)
        if os.path.exists(meta_path):
            self.product_metadata = pd.read_parquet(meta_path)
            id_col = "index" if "index" in self.product_metadata.columns else "product_id"
            if id_col in self.product_metadata.columns:
                self.product_id_to_idx = {
                    int(pid): idx for idx, pid in enumerate(self.product_metadata[id_col])
                }

        self._bigbasket_loaded = True

    @property
    def bigbasket_meta(self) -> Optional[pd.DataFrame]:
        return self.product_metadata

    # --- RetailRocket Latent Factor Access ---
    def get_user_factors(self, user_id: int) -> Optional[np.ndarray]:
        """Returns the 100-dim SVD factor vector for a user if available."""
        if self.user_factors is None:
            return None
        idx = self.user_id_to_idx.get(user_id)
        if idx is not None and idx < len(self.user_factors):
            return self.user_factors[idx]
        return None

    def get_item_factors(self, item_id: int) -> Optional[np.ndarray]:
        """Returns the 100-dim SVD factor vector for an item if available."""
        if self.item_factors is None:
            return None
        idx = self.item_id_to_idx.get(item_id)
        if idx is not None and idx < len(self.item_factors):
            return self.item_factors[idx]
        return None

    get_user_vector = get_user_factors
    get_item_vector = get_item_factors

    def get_raw_item_id_from_encoded(self, idx: int) -> Optional[int]:
        if self.item_encoder is not None and hasattr(self.item_encoder, "classes_"):
            if 0 <= idx < len(self.item_encoder.classes_):
                return int(self.item_encoder.classes_[idx])
        return None

    def get_bigbasket_product_id(self, idx: int) -> Optional[int]:
        if self.product_metadata is not None:
            id_col = "index" if "index" in self.product_metadata.columns else "product_id"
            if 0 <= idx < len(self.product_metadata):
                return int(self.product_metadata.iloc[idx][id_col])
        return None

    # --- BigBasket Content Vector Access ---
    def get_product_tfidf_vector(self, product_id: int) -> Optional[sp.csr_matrix]:
        """Returns the TF-IDF sparse row vector for a BigBasket product."""
        if self.tfidf_matrix is None:
            return None
        idx = self.product_id_to_idx.get(product_id)
        if idx is not None and idx < self.tfidf_matrix.shape[0]:
            return self.tfidf_matrix.getrow(idx)
        return None

    def transform_text_query(self, query_text: str) -> Optional[sp.csr_matrix]:
        """Transforms raw search/preference text into the fitted 31,138 TF-IDF space."""
        if self.tfidf_vectorizer is None or not query_text:
            return None
        return self.tfidf_vectorizer.transform([query_text])


feature_store = FeatureStore.get_instance()
