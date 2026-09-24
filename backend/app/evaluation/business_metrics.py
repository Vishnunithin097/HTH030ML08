"""
Business Guardrail Evaluation Metrics.
Quantifies margin realization, stockout avoidance, and inventory efficiency gains.
"""
from typing import List, Dict, Any


def compute_average_margin(slate: List[Dict[str, Any]]) -> float:
    """Computes mean profit margin percentage across recommendation slate."""
    if not slate:
        return 0.0
    margins = [float(item.get("margin_pct") or 20.0) for item in slate]
    return round(float(sum(margins) / len(margins)), 2)


def compute_stockout_risk_rate(slate: List[Dict[str, Any]], threshold: int = 10) -> float:
    """Computes the fraction of items in the slate with inventory below the safety threshold."""
    if not slate:
        return 0.0
    low_stock = sum(1 for item in slate if int(item.get("inventory_count") or 100) < threshold)
    return round(float(low_stock / len(slate)), 4)


def compute_business_lift_metrics(
    pure_slates: List[List[Dict[str, Any]]],
    guarded_slates: List[List[Dict[str, Any]]],
    inventory_threshold: int = 10,
) -> Dict[str, Any]:
    """
    Computes comparative business performance between Pure and Guarded recommendation slates.
    """
    if not pure_slates or not guarded_slates:
        return {
            "pure_avg_margin_pct": 0.0,
            "guarded_avg_margin_pct": 0.0,
            "margin_lift_pct": 0.0,
            "stockout_reduction_pct": 0.0,
        }

    pure_margins = [compute_average_margin(s) for s in pure_slates]
    guarded_margins = [compute_average_margin(s) for s in guarded_slates]

    avg_pure_margin = sum(pure_margins) / len(pure_margins) if pure_margins else 0.0
    avg_guarded_margin = sum(guarded_margins) / len(guarded_margins) if guarded_margins else 0.0

    margin_lift = (
        ((avg_guarded_margin - avg_pure_margin) / avg_pure_margin) * 100.0
        if avg_pure_margin > 0
        else 0.0
    )

    pure_stockout_rates = [compute_stockout_risk_rate(s, inventory_threshold) for s in pure_slates]
    guarded_stockout_rates = [compute_stockout_risk_rate(s, inventory_threshold) for s in guarded_slates]

    avg_pure_stockout = sum(pure_stockout_rates) / len(pure_stockout_rates)
    avg_guarded_stockout = sum(guarded_stockout_rates) / len(guarded_stockout_rates)

    stockout_reduction = max(0.0, avg_pure_stockout - avg_guarded_stockout) * 100.0

    return {
        "pure_avg_margin_pct": round(avg_pure_margin, 2),
        "guarded_avg_margin_pct": round(avg_guarded_margin, 2),
        "margin_lift_pct": round(margin_lift, 2),
        "pure_stockout_rate": round(avg_pure_stockout, 4),
        "guarded_stockout_rate": round(avg_guarded_stockout, 4),
        "stockout_reduction_pct": round(stockout_reduction, 2),
    }
