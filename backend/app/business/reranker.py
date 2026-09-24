"""
Business Multi-Objective Re-Ranker.
Re-ranks pure ML candidates using business value, margin weight, and inventory scores.
(Implementation scheduled for Phase 3).
"""
from typing import List, Dict, Any


class BusinessReRanker:
    """Combines ML relevance with business scalarization scores."""

    def __init__(
        self,
        relevance_weight: float = 0.70,
        business_weight: float = 0.30,
        margin_weight: float = 0.40,
        inventory_weight: float = 0.30,
        quality_weight: float = 0.30,
    ):
        self.relevance_weight = relevance_weight
        self.business_weight = business_weight
        self.margin_weight = margin_weight
        self.inventory_weight = inventory_weight
        self.quality_weight = quality_weight

    def calculate_business_score(
        self, margin_pct: float, inventory_count: int, quality_score: float
    ) -> float:
        # Normalized margin score (capped at 50% for 1.0)
        norm_margin = min(margin_pct / 50.0, 1.0)
        # Normalized inventory score (capped at 100 for 1.0)
        norm_inventory = min(inventory_count / 100.0, 1.0)
        norm_quality = max(0.0, min(quality_score, 1.0))

        return (
            self.margin_weight * norm_margin
            + self.inventory_weight * norm_inventory
            + self.quality_weight * norm_quality
        )

    def calculate_final_score(self, relevance_score: float, business_score: float) -> float:
        return (
            self.relevance_weight * relevance_score
            + self.business_weight * business_score
        )
