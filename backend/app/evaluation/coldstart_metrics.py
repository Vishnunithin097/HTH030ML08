"""
Cold-Start Benchmark Metrics.
(Implementation scheduled for Phase 3).
"""
from typing import List


def compute_cold_start_coverage(recommended_categories: List[str], target_categories: List[str]) -> float:
    """Computes category hit rate for cold-start personas."""
    if not target_categories:
        return 0.0
    hits = sum(1 for c in recommended_categories if c in target_categories)
    return hits / len(target_categories)
