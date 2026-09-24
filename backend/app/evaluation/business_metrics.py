"""
Business Impact Evaluation Metrics.
(Implementation scheduled for Phase 3).
"""
from typing import List, Dict, Any


def compute_business_lift(baseline_margin: float, guardrail_margin: float) -> float:
    """Computes percentage lift in margin yield achieved by business guardrails."""
    if baseline_margin == 0:
        return 0.0
    return ((guardrail_margin - baseline_margin) / baseline_margin) * 100.0
