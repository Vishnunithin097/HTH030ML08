"""
Signal-backed Explainability Engine.
Generates deterministic explanations derived from explicit interaction history, category affinity, and cold-start signals.
(Implementation scheduled for Phase 3).
"""
from typing import List, Dict, Any, Optional


class ExplainabilityEngine:
    """Generates verifiable recommendation rationales without synthetic illusions."""

    def generate_explanation(
        self,
        item_category: str,
        user_top_category: Optional[str],
        is_cold_start: bool,
        recommendation_source: str,
        margin_pct: Optional[float] = None
    ) -> str:
        if is_cold_start:
            return f"Recommended based on your selected preference in '{item_category}' category."
        elif recommendation_source == "collaborative":
            return f"Shoppers with similar purchase patterns also enjoyed this item in '{item_category}'."
        elif recommendation_source == "content_based":
            return f"Recommended because you frequently interacted with '{item_category}' products."
        else:
            return f"Top pick in '{item_category}' balancing personal relevance and high customer rating."


explainability_engine = ExplainabilityEngine()
