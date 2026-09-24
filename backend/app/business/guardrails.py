"""
Business Guardrail Layer.
Computes business scores, soft penalties, hard constraint filters,
and counterfactual sensitivity evaluations without modifying the ML models.
"""
from typing import Dict, Any, List, Optional, Tuple
import numpy as np


class GuardrailPolicy:
    """Encapsulates business guardrail parameters."""

    def __init__(
        self,
        min_inventory: int = 10,
        min_margin: float = 20.0,
        relevance_weight: float = 0.700,
        business_weight: float = 0.300,
        margin_weight: float = 0.400,
        inventory_weight: float = 0.300,
        quality_weight: float = 0.300,
        cold_start_threshold: int = 3,
        hard_filter_enabled: bool = False,
    ):
        self.min_inventory = min_inventory
        self.min_margin = min_margin
        self.relevance_weight = relevance_weight
        self.business_weight = business_weight
        self.margin_weight = margin_weight
        self.inventory_weight = inventory_weight
        self.quality_weight = quality_weight
        self.cold_start_threshold = cold_start_threshold
        self.hard_filter_enabled = hard_filter_enabled


class BusinessGuardrailEvaluator:
    """
    Evaluates business metrics, applies penalty multipliers, and filters items.
    """

    def compute_business_score(
        self,
        margin_pct: float,
        inventory_count: int,
        quality_score: float,
        business_priority: float = 0.0,
        policy: Optional[GuardrailPolicy] = None,
    ) -> float:
        """
        Computes a normalized business score in [0.0, 1.0].
        """
        p = policy or GuardrailPolicy()

        # Margin score: 0% -> 0.0, 50%+ -> 1.0
        norm_margin = float(np.clip(margin_pct / 50.0, 0.0, 1.0))

        # Inventory score: 0 -> 0.0, 100+ units -> 1.0
        norm_inv = float(np.clip(inventory_count / 100.0, 0.0, 1.0))

        # Quality score: 0.0 -> 1.0
        norm_qual = float(np.clip(quality_score, 0.0, 1.0))

        # Strategic priority: 0.0 -> 1.0
        norm_prio = float(np.clip(business_priority, 0.0, 1.0))

        # Weighted business value
        biz_score = (
            p.margin_weight * norm_margin
            + p.inventory_weight * norm_inv
            + p.quality_weight * norm_qual
            + 0.10 * norm_prio
        )
        return float(np.clip(biz_score, 0.0, 1.0))

    def compute_penalty(
        self,
        margin_pct: float,
        inventory_count: int,
        policy: Optional[GuardrailPolicy] = None,
    ) -> Tuple[float, List[str]]:
        """
        Computes soft penalties and returns penalty reasons.
        """
        p = policy or GuardrailPolicy()
        penalty = 0.0
        reasons = []

        # Low inventory penalty
        if inventory_count < p.min_inventory:
            deficit_ratio = (p.min_inventory - max(0, inventory_count)) / max(1, p.min_inventory)
            inv_penalty = 0.25 * deficit_ratio
            penalty += inv_penalty
            reasons.append(f"Low inventory warning ({inventory_count} < {p.min_inventory} units)")

        # Low margin penalty
        if margin_pct < p.min_margin:
            margin_deficit = (p.min_margin - max(0.0, margin_pct)) / max(1.0, p.min_margin)
            marg_penalty = 0.20 * margin_deficit
            penalty += marg_penalty
            reasons.append(f"Low margin warning ({margin_pct:.1f}% < {p.min_margin:.1f}%)")

        return float(np.clip(penalty, 0.0, 0.50)), reasons

    def passes_hard_filters(
        self,
        margin_pct: float,
        inventory_count: int,
        policy: Optional[GuardrailPolicy] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Evaluates hard filter exclusions when enabled.
        """
        p = policy or GuardrailPolicy()
        if not p.hard_filter_enabled:
            return True, None

        if inventory_count < p.min_inventory:
            return False, f"Filtered: Out of Stock / Low Inventory ({inventory_count} < {p.min_inventory})"

        if margin_pct < p.min_margin:
            return False, f"Filtered: Margin Below Floor ({margin_pct:.1f}% < {p.min_margin:.1f}%)"

        return True, None

    def evaluate_counterfactual(
        self,
        relevance_score: float,
        margin_pct: float,
        inventory_count: int,
        quality_score: float,
        current_final_score: float,
        hypothetical_min_margin: Optional[float] = None,
        hypothetical_min_inventory: Optional[int] = None,
        hypothetical_margin_pct: Optional[float] = None,
        hypothetical_inventory_count: Optional[int] = None,
        policy: Optional[GuardrailPolicy] = None,
    ) -> Dict[str, Any]:
        """
        Performs sensitivity simulation to explain how changes in business parameters
        or product metadata affect the final re-ranking score.
        """
        base_policy = policy or GuardrailPolicy()
        
        sim_policy = GuardrailPolicy(
            min_inventory=hypothetical_min_inventory if hypothetical_min_inventory is not None else base_policy.min_inventory,
            min_margin=hypothetical_min_margin if hypothetical_min_margin is not None else base_policy.min_margin,
            relevance_weight=base_policy.relevance_weight,
            business_weight=base_policy.business_weight,
            margin_weight=base_policy.margin_weight,
            inventory_weight=base_policy.inventory_weight,
            quality_weight=base_policy.quality_weight,
            hard_filter_enabled=base_policy.hard_filter_enabled,
        )

        sim_margin = hypothetical_margin_pct if hypothetical_margin_pct is not None else margin_pct
        sim_inv = hypothetical_inventory_count if hypothetical_inventory_count is not None else inventory_count

        sim_biz_score = self.compute_business_score(sim_margin, sim_inv, quality_score, policy=sim_policy)
        sim_penalty, sim_reasons = self.compute_penalty(sim_margin, sim_inv, policy=sim_policy)

        sim_final_score = float(np.clip(
            sim_policy.relevance_weight * relevance_score
            + sim_policy.business_weight * sim_biz_score
            - sim_penalty,
            0.0, 1.0
        ))

        score_delta = round(sim_final_score - current_final_score, 5)

        return {
            "baseline_score": current_final_score,
            "simulated_score": round(sim_final_score, 5),
            "score_delta": score_delta,
            "simulated_business_score": round(sim_biz_score, 5),
            "simulated_penalty": round(sim_penalty, 5),
            "reasons": sim_reasons,
            "summary": (
                f"Score changes by {score_delta:+.3f} (from {current_final_score:.3f} to {sim_final_score:.3f}) "
                f"under hypothetical conditions."
            )
        }


guardrail_evaluator = BusinessGuardrailEvaluator()
