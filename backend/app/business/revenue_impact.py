"""
Revenue and Profit Margin Impact Simulation Engine.
Computes financial projections and commercial lift across recommendation slates.
"""
from typing import List, Dict, Any


class RevenueImpactCalculator:
    """
    Simulates projected commercial metrics (GMV, profit margin, lift)
    comparing Pure Relevance against Business-Aware recommendation slates.
    """

    def simulate_impact(
        self,
        pure_slate: List[Dict[str, Any]],
        guarded_slate: List[Dict[str, Any]],
        assumed_conversion_rate: float = 0.05,
        assumed_impressions: int = 1000,
    ) -> Dict[str, Any]:
        """
        Calculates projected GMV and margin yield between Pure and Guarded recommendation slates.
        """
        def calculate_slate_metrics(slate: List[Dict[str, Any]]) -> Dict[str, float]:
            if not slate:
                return {
                    "total_gmv": 0.0,
                    "total_margin_inr": 0.0,
                    "avg_margin_pct": 0.0,
                    "stockout_risk_items": 0,
                }

            total_gmv = 0.0
            total_margin_inr = 0.0
            margin_pcts = []
            stockout_risk = 0

            for item in slate:
                price = float(item.get("price") or 299.0)
                margin_pct = float(item.get("margin_pct") or 20.0)
                inventory = int(item.get("inventory_count") or 100)

                # Projected sales units = impressions * conversion_rate / slate_size
                projected_units = (assumed_impressions * assumed_conversion_rate) / len(slate)
                gmv = projected_units * price
                margin_inr = gmv * (margin_pct / 100.0)

                total_gmv += gmv
                total_margin_inr += margin_inr
                margin_pcts.append(margin_pct)

                if inventory < 10:
                    stockout_risk += 1

            avg_margin_pct = sum(margin_pcts) / len(margin_pcts) if margin_pcts else 0.0

            return {
                "projected_gmv": round(total_gmv, 2),
                "projected_margin_inr": round(total_margin_inr, 2),
                "avg_margin_pct": round(avg_margin_pct, 2),
                "stockout_risk_items": stockout_risk,
            }

        pure_metrics = calculate_slate_metrics(pure_slate)
        guarded_metrics = calculate_slate_metrics(guarded_slate)

        # Compute Lift
        pure_margin_inr = pure_metrics["projected_margin_inr"]
        guarded_margin_inr = guarded_metrics["projected_margin_inr"]

        if pure_margin_inr > 0:
            margin_lift_pct = round(((guarded_margin_inr - pure_margin_inr) / pure_margin_inr) * 100.0, 2)
        else:
            margin_lift_pct = 0.0

        return {
            "simulation_notice": "Projection/Simulation based on catalog pricing and synthetic margin parameters.",
            "assumed_impressions": assumed_impressions,
            "assumed_conversion_rate": assumed_conversion_rate,
            "pure_mode": pure_metrics,
            "business_aware_mode": guarded_metrics,
            "projected_margin_lift_pct": margin_lift_pct,
            "stockout_risk_avoided": max(0, pure_metrics["stockout_risk_items"] - guarded_metrics["stockout_risk_items"]),
        }


revenue_calculator = RevenueImpactCalculator()
