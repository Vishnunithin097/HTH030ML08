"""
Information Retrieval / Ranking Metrics (NDCG, Precision@k, Recall@k, MAP).
(Implementation scheduled for Phase 3).
"""
import numpy as np
from typing import List


def compute_ndcg_at_k(relevance_scores: List[float], k: int = 10) -> float:
    """Computes Normalized Discounted Cumulative Gain at rank k."""
    if not relevance_scores:
        return 0.0
    r = np.asfarray(relevance_scores)[:k]
    if r.size == 0:
        return 0.0
    dcg = np.sum(r / np.log2(np.arange(2, r.size + 2)))
    ideal_r = np.sort(r)[::-1]
    idcg = np.sum(ideal_r / np.log2(np.arange(2, ideal_r.size + 2)))
    if idcg == 0:
        return 0.0
    return float(dcg / idcg)
