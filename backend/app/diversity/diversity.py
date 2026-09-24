"""
Diversity and Maximal Marginal Relevance (MMR) Engine.
Computes intra-list diversity metrics and provides optional MMR category de-duplication.
"""
from typing import List, Dict, Any, Set
import numpy as np


class DiversityEngine:
    """
    Computes intra-list diversity and performs MMR re-ranking for category variety.
    """

    def compute_intra_list_diversity(self, slate: List[Dict[str, Any]]) -> float:
        """
        Computes intra-list category diversity score in [0.0, 1.0].
        1.0 means every item in slate belongs to a different category.
        """
        if not slate:
            return 0.0

        categories = [item.get("category_name", "Unknown") for item in slate if item]
        if not categories:
            return 0.0

        unique_cats = len(set(categories))
        return round(float(unique_cats / len(categories)), 4)

    def compute_catalog_entropy(self, slate: List[Dict[str, Any]]) -> float:
        """
        Computes Shannon entropy across the category distribution in the recommendation slate.
        """
        if not slate:
            return 0.0

        categories = [item.get("category_name", "Unknown") for item in slate]
        total = len(categories)
        counts = {}
        for c in categories:
            counts[c] = counts.get(c, 0) + 1

        probs = [count / total for count in counts.values()]
        entropy = -sum(p * np.log2(p) for p in probs if p > 0)
        return round(float(entropy), 4)

    def mmr_rerank(
        self,
        candidates: List[Dict[str, Any]],
        top_k: int = 10,
        diversity_lambda: float = 0.70,
    ) -> List[Dict[str, Any]]:
        """
        Applies Maximal Marginal Relevance (MMR) to prevent category monopolization.
        Score_MMR(d) = lambda * Score(d) - (1 - lambda) * MaxSimilarity(d, Selected)
        """
        if not candidates or len(candidates) <= top_k:
            return candidates[:top_k]

        selected: List[Dict[str, Any]] = []
        selected_categories: Set[str] = set()
        pool = list(candidates)

        while len(selected) < top_k and pool:
            best_idx = 0
            best_mmr_score = -float("inf")

            for idx, candidate in enumerate(pool):
                base_score = candidate.get("final_score", candidate.get("relevance_score", 0.5))
                cat = candidate.get("category_name", "General")

                # Redundancy penalty if category is already heavily represented in selected
                category_penalty = 0.40 if cat in selected_categories else 0.0
                mmr_score = diversity_lambda * base_score - (1.0 - diversity_lambda) * category_penalty

                if mmr_score > best_mmr_score:
                    best_mmr_score = mmr_score
                    best_idx = idx

            chosen = pool.pop(best_idx)
            selected.append(chosen)
            selected_categories.add(chosen.get("category_name", "General"))

        for idx, item in enumerate(selected):
            item["rank"] = idx + 1

        return selected


diversity_engine = DiversityEngine()
