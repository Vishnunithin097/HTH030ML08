"""
Diversity and Catalog Coverage Metric Calculations.
(Implementation scheduled for Phase 3).
"""
from typing import List, Set


class DiversityCalculator:
    """Calculates intra-list category diversity and catalog entropy."""

    def compute_intra_list_diversity(self, categories: List[str]) -> float:
        if not categories:
            return 0.0
        unique_count = len(set(categories))
        return unique_count / len(categories)
