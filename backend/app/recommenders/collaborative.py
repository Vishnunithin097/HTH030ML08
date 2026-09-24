"""
Collaborative Filtering Recommender Engine.
Utilizes pre-trained RetailRocket TruncatedSVD latent factors and label encoders.
"""
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
from app.core.feature_extraction import feature_store


class CollaborativeRecommender:
    """
    Collaborative filtering engine computing user-item latent affinity scores
    and item-item vector similarities using trained TruncatedSVD embeddings.
    """

    def __init__(self):
        self.store = feature_store

    def is_user_available(self, user_id: int) -> bool:
        """Checks if user has a trained latent factor representation."""
        idx = self.store.user_id_to_idx.get(user_id)
        return idx is not None and idx < (len(self.store.user_factors) if self.store.user_factors is not None else 0)

    def is_item_available(self, item_id: int) -> bool:
        """Checks if item has a trained latent factor representation."""
        idx = self.store.item_id_to_idx.get(item_id)
        return idx is not None and idx < (len(self.store.item_factors) if self.store.item_factors is not None else 0)

    def predict_score(self, user_id: int, item_id: int) -> Optional[float]:
        """
        Computes the collaborative filtering affinity score between user and item.
        Returns a normalized score in [0.0, 1.0], or None if either user or item is unseen.
        """
        u_factors = self.store.get_user_factors(user_id)
        i_factors = self.store.get_item_factors(item_id)

        if u_factors is None or i_factors is None:
            return None

        # Compute dot product in 100-dimensional latent space
        raw_dot = float(np.dot(u_factors, i_factors))

        # Apply sigmoid normalization to bound score strictly in (0, 1)
        # SVD latent dot products for RetailRocket typically span [-5, 5]
        norm_score = 1.0 / (1.0 + np.exp(-np.clip(raw_dot, -10.0, 10.0)))
        return float(np.round(norm_score, 5))

    def predict_user_candidates(
        self, user_id: int, candidate_item_ids: List[int]
    ) -> Dict[int, float]:
        """
        Computes batch collaborative affinity scores across candidate items.
        """
        u_factors = self.store.get_user_factors(user_id)
        if u_factors is None:
            return {}

        results: Dict[int, float] = {}
        for item_id in candidate_item_ids:
            i_factors = self.store.get_item_factors(item_id)
            if i_factors is not None:
                dot = float(np.dot(u_factors, i_factors))
                score = 1.0 / (1.0 + np.exp(-np.clip(dot, -10.0, 10.0)))
                results[item_id] = float(np.round(score, 5))

        return results

    def item_similarity(self, item_id_a: int, item_id_b: int) -> Optional[float]:
        """
        Computes cosine similarity between two item factor representations.
        """
        fa = self.store.get_item_factors(item_id_a)
        fb = self.store.get_item_factors(item_id_b)
        if fa is None or fb is None:
            return None

        norm_a = np.linalg.norm(fa)
        norm_b = np.linalg.norm(fb)
        if norm_a == 0 or norm_b == 0:
            return 0.0

        cos_sim = float(np.dot(fa, fb) / (norm_a * norm_b))
        # Rescale [-1, 1] to [0, 1]
        return float(np.round((cos_sim + 1.0) / 2.0, 5))


collaborative_recommender = CollaborativeRecommender()
