"""
Business-Aware Re-Ranker and Guardrail Health Engine.
The single source of truth for Pure Engagement vs. Business-Aware candidate ranking.
"""
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from app.business.guardrails import GuardrailPolicy, guardrail_evaluator


class BusinessReRanker:
    """
    Ranks recommendation candidates in Pure Engagement or Business-Aware modes,
    and monitors guardrail health and item churn.
    """

    def __init__(self):
        self.evaluator = guardrail_evaluator

    def rank(
        self,
        candidates: List[Dict[str, Any]],
        mode: str = "business_aware",
        policy: Optional[GuardrailPolicy] = None,
        top_k: int = 10,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Ranks candidates according to mode ('pure' vs 'business_aware') and returns
        the ranked list alongside guardrail health diagnostics.
        """
        p = policy or GuardrailPolicy()

        if not candidates:
            return [], {"status": "empty", "suppression_rate": 0.0}

        # 1. Compute Pure Engagement baseline ranking
        pure_ranked = sorted(candidates, key=lambda x: x.get("relevance_score", 0.0), reverse=True)
        pure_top_ids = set(c["item_id"] for c in pure_ranked[:top_k])

        if mode == "pure":
            for idx, c in enumerate(pure_ranked[:top_k]):
                c["rank"] = idx + 1
                c["final_score"] = c.get("relevance_score", 0.0)
                c["business_score"] = None
                c["penalties"] = 0.0
                c["guardrail_applied"] = False
            return pure_ranked[:top_k], {
                "mode": "pure",
                "top_k": top_k,
                "churn_count": 0,
                "suppression_rate": 0.0,
                "health_status": "optimal",
            }

        # 2. Business-Aware Re-Ranking Mode
        guarded_candidates = []
        filtered_count = 0

        for item in candidates:
            margin_pct = float(item.get("margin_pct") or 20.0)
            inventory = int(item.get("inventory_count") if item.get("inventory_count") is not None else 100)
            quality = float(item.get("quality_score") or 0.70)
            priority = float(item.get("business_priority") or 0.0)
            relevance = float(item.get("relevance_score") or 0.5)

            # Check Hard Constraint Filter
            passes_hard, filter_reason = self.evaluator.passes_hard_filters(margin_pct, inventory, policy=p)
            if not passes_hard:
                filtered_count += 1
                continue

            # Compute Business Score & Soft Penalties
            biz_score = self.evaluator.compute_business_score(margin_pct, inventory, quality, priority, policy=p)
            penalty, penalty_reasons = self.evaluator.compute_penalty(margin_pct, inventory, policy=p)

            # Scalarized Final Score
            final_score = float(np.clip(
                p.relevance_weight * relevance
                + p.business_weight * biz_score
                - penalty,
                0.0, 1.0
            ))

            guarded_item = dict(item)
            guarded_item["relevance_score"] = round(relevance, 5)
            guarded_item["business_score"] = round(biz_score, 5)
            guarded_item["penalty_score"] = round(penalty, 5)
            guarded_item["final_score"] = round(final_score, 5)
            guarded_item["penalty_reasons"] = penalty_reasons
            guarded_item["guardrail_applied"] = True

            guarded_candidates.append(guarded_item)

        # Sort by final score descending
        guarded_ranked = sorted(guarded_candidates, key=lambda x: x["final_score"], reverse=True)
        final_slate = guarded_ranked[:top_k]

        for idx, c in enumerate(final_slate):
            c["rank"] = idx + 1

        # 3. Calculate Guardrail Health & Churn Metrics
        biz_top_ids = set(c["item_id"] for c in final_slate)
        displaced_pure_items = pure_top_ids - biz_top_ids
        churn_count = len(displaced_pure_items)
        suppression_rate = (filtered_count + churn_count) / max(1, len(candidates))

        # Health status evaluation
        if suppression_rate > 0.50:
            health_status = "warning_high_suppression"
            warning_msg = f"Guardrail suppression is high ({suppression_rate*100:.1f}%). High-relevance items may be overly restricted."
        elif suppression_rate > 0.25:
            health_status = "moderate_churn"
            warning_msg = f"Guardrails actively re-ranking {churn_count} top items to optimize margin and stock."
        else:
            health_status = "healthy"
            warning_msg = "Re-ranking achieved healthy balance between ML relevance and commercial guardrails."

        diagnostics = {
            "mode": "business_aware",
            "top_k": top_k,
            "churn_count": churn_count,
            "filtered_items_count": filtered_count,
            "suppression_rate": round(float(suppression_rate), 4),
            "health_status": health_status,
            "health_message": warning_msg,
        }

        return final_slate, diagnostics


reranker = BusinessReRanker()
