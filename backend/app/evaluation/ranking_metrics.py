"""
Information Retrieval and Recommendation Ranking Metrics.
Implements standard Precision@K, Recall@K, NDCG@K, and MAP.
"""
from typing import List, Set, Any
import numpy as np


def compute_precision_at_k(recommended_ids: List[int], ground_truth_ids: Set[int], k: int = 10) -> float:
    """Computes Precision@K: Fraction of top-K recommended items that are relevant."""
    if not recommended_ids or not ground_truth_ids:
        return 0.0
    top_k = recommended_ids[:k]
    hits = sum(1 for item_id in top_k if item_id in ground_truth_ids)
    return round(float(hits / len(top_k)), 4)


def compute_recall_at_k(recommended_ids: List[int], ground_truth_ids: Set[int], k: int = 10) -> float:
    """Computes Recall@K: Fraction of relevant items captured in top-K recommendations."""
    if not ground_truth_ids or not recommended_ids:
        return 0.0
    top_k = recommended_ids[:k]
    hits = sum(1 for item_id in top_k if item_id in ground_truth_ids)
    return round(float(hits / len(ground_truth_ids)), 4)


def compute_ndcg_at_k(recommended_ids: List[int], ground_truth_ids: Set[int], k: int = 10) -> float:
    """
    Computes Normalized Discounted Cumulative Gain at rank K.
    Binary relevance: 1 if item in ground_truth_ids else 0.
    """
    if not recommended_ids or not ground_truth_ids:
        return 0.0

    top_k = recommended_ids[:k]
    rel = [1.0 if item_id in ground_truth_ids else 0.0 for item_id in top_k]
    if sum(rel) == 0:
        return 0.0

    # DCG
    dcg = sum((2.0 ** r - 1.0) / np.log2(idx + 2) for idx, r in enumerate(rel))

    # IDCG
    ideal_rel = sorted(rel, reverse=True)
    idcg = sum((2.0 ** r - 1.0) / np.log2(idx + 2) for idx, r in enumerate(ideal_rel))

    if idcg == 0:
        return 0.0
    return round(float(dcg / idcg), 4)


def compute_map(recommended_ids: List[int], ground_truth_ids: Set[int], k: int = 10) -> float:
    """Computes Mean Average Precision at rank K."""
    if not recommended_ids or not ground_truth_ids:
        return 0.0

    top_k = recommended_ids[:k]
    running_hits = 0
    precisions = []

    for idx, item_id in enumerate(top_k):
        if item_id in ground_truth_ids:
            running_hits += 1
            precisions.append(running_hits / (idx + 1))

    if not precisions:
        return 0.0
    return round(float(sum(precisions) / min(len(ground_truth_ids), k)), 4)
