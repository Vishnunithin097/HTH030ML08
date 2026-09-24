"""
Content-Based Recommender using TF-IDF feature representations and cosine similarities.
(Implementation scheduled for Phase 3).
"""
from typing import List, Tuple
import numpy as np


class ContentBasedRecommender:
    """Content-based filtering using BigBasket TF-IDF text features."""

    def __init__(self):
        pass

    def compute_similarity(self, query_vec, target_matrix) -> np.ndarray:
        """Computes cosine similarity against candidate item sparse vectors."""
        return np.asarray(target_matrix.dot(query_vec.T).todense()).flatten()
