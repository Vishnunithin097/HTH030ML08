"""
Content-Based Recommendation Engine.
Utilizes pre-trained BigBasket TF-IDF vectorizer and sparse feature matrix.
"""
from typing import List, Dict, Optional, Any, Union
import numpy as np
import scipy.sparse as sp
from app.core.feature_extraction import feature_store
from app.core.preprocessing import clean_text


class ContentBasedRecommender:
    """
    Content-based engine matching user profile vectors and category signals
    against catalog TF-IDF representations using sparse cosine similarity.
    """

    def __init__(self):
        self.store = feature_store

    def build_user_profile_vector(
        self,
        interacted_product_ids: List[int] = None,
        category_preferences: List[str] = None,
        search_query: Optional[str] = None,
    ) -> Optional[sp.csr_matrix]:
        """
        Synthesizes a user content vector from interacted product TF-IDF rows,
        declared category preferences, and/or search text.
        """
        vectors = []

        # 1. Add TF-IDF vectors of interacted items
        if interacted_product_ids and self.store.tfidf_matrix is not None:
            for pid in interacted_product_ids:
                row_vec = self.store.get_product_tfidf_vector(pid)
                if row_vec is not None:
                    vectors.append(row_vec)

        # 2. Add TF-IDF vector from category keywords or search query
        text_signals = []
        if category_preferences:
            text_signals.extend(category_preferences)
        if search_query:
            text_signals.append(search_query)

        if text_signals and self.store.tfidf_vectorizer is not None:
            joined_text = " ".join(clean_text(s) for s in text_signals if s)
            if joined_text.strip():
                query_vec = self.store.transform_text_query(joined_text)
                if query_vec is not None:
                    # Give high weight to explicit stated preferences
                    vectors.append(query_vec * 2.0)

        if not vectors:
            return None

        # Stack and average vectors into a single normalized user representation
        stacked = sp.vstack(vectors)
        mean_vec = sp.csr_matrix(stacked.mean(axis=0))
        norm = sp.linalg.norm(mean_vec)
        if norm > 0:
            mean_vec = mean_vec / norm
        return mean_vec

    def predict_score(
        self, user_profile_vec: sp.csr_matrix, product_id: int
    ) -> Optional[float]:
        """
        Computes cosine similarity between user content profile and a single candidate item.
        """
        item_vec = self.store.get_product_tfidf_vector(product_id)
        if item_vec is None or user_profile_vec is None:
            return None

        # Cosine similarity for L2-normalized TF-IDF sparse vectors is dot product
        cos_sim = float(user_profile_vec.dot(item_vec.T).toarray()[0][0])
        # Clip to [0, 1]
        norm_score = max(0.0, min(cos_sim, 1.0))
        return float(np.round(norm_score, 5))

    def predict_batch(
        self, user_profile_vec: sp.csr_matrix, candidate_product_ids: List[int]
    ) -> Dict[int, float]:
        """
        Computes batch cosine similarities across candidate items efficiently using sparse dot products.
        """
        if user_profile_vec is None or self.store.tfidf_matrix is None or not candidate_product_ids:
            return {}

        valid_pids = []
        row_indices = []
        for pid in candidate_product_ids:
            idx = self.store.product_id_to_idx.get(pid)
            if idx is not None and idx < self.store.tfidf_matrix.shape[0]:
                valid_pids.append(pid)
                row_indices.append(idx)

        if not row_indices:
            return {}

        # Fast vectorized sparse matrix multiplication (1, 31138) x (N, 31138).T -> (1, N)
        sub_matrix = self.store.tfidf_matrix[row_indices]
        sim_scores = user_profile_vec.dot(sub_matrix.T).toarray()[0]

        results: Dict[int, float] = {}
        for pid, score in zip(valid_pids, sim_scores):
            results[pid] = float(np.round(max(0.0, min(float(score), 1.0)), 5))

        return results

    def item_similarity(self, product_id_a: int, product_id_b: int) -> Optional[float]:
        """
        Computes cosine similarity between two BigBasket catalog products.
        """
        va = self.store.get_product_tfidf_vector(product_id_a)
        vb = self.store.get_product_tfidf_vector(product_id_b)
        if va is None or vb is None:
            return None

        sim = float(va.dot(vb.T).toarray()[0][0])
        return float(np.round(max(0.0, min(sim, 1.0)), 5))

    get_item_similarity = item_similarity

    def recommend(
        self,
        user_profile_vec: Optional[sp.csr_matrix] = None,
        interacted_product_ids: Optional[List[int]] = None,
        category_preferences: Optional[List[str]] = None,
        candidate_product_ids: Optional[List[int]] = None,
        interacted_to_exclude: Optional[List[int]] = None,
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Generates top-K content-based recommendations by comparing candidate TF-IDF vectors
        with user profile representation or stated category preferences.
        """
        if user_profile_vec is None:
            user_profile_vec = self.build_user_profile_vector(
                interacted_product_ids=interacted_product_ids,
                category_preferences=category_preferences,
            )

        if user_profile_vec is None or self.store.tfidf_matrix is None:
            return []

        excluded = set(interacted_to_exclude or interacted_product_ids or [])

        if candidate_product_ids is None:
            candidate_product_ids = list(self.store.product_id_to_idx.keys())[:500]

        filtered_candidates = [pid for pid in candidate_product_ids if pid not in excluded]
        batch_scores = self.predict_batch(user_profile_vec, filtered_candidates)

        scored_candidates = [
            {
                "item_id": pid,
                "content_score": score,
                "recommendation_source": "tfidf_content_only",
            }
            for pid, score in batch_scores.items()
        ]

        scored_candidates.sort(key=lambda x: x["content_score"], reverse=True)
        for idx, item in enumerate(scored_candidates[:top_k]):
            item["rank"] = idx + 1

        return scored_candidates[:top_k]


content_recommender = ContentBasedRecommender()
