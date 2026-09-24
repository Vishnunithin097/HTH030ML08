"""
Preprocessing and interaction handling utilities.
Provides reusable functions for interaction weights, cold-start detection, and text cleaning.
"""
import re
from typing import List, Dict, Any, Optional
import numpy as np


EVENT_WEIGHTS = {
    "view": 1.0,
    "addtocart": 2.5,
    "transaction": 5.0,
}


def clean_text(text: Optional[str]) -> str:
    """Normalizes raw product description / title text."""
    if not text or not isinstance(text, str):
        return ""
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.lower().split())


def extract_keywords(tags: List[str]) -> str:
    """Combines list of tags into a normalized keyword string."""
    if not tags:
        return ""
    return " ".join(clean_text(tag) for tag in tags if tag)


def get_event_weight(event_type: str) -> float:
    """Returns the numerical interaction weight for an event."""
    return EVENT_WEIGHTS.get(event_type.lower(), 1.0)


def is_cold_start_user(interaction_count: int, threshold: int = 3) -> bool:
    """Determines if a user qualifies as a cold-start shopper."""
    return interaction_count < threshold


def is_cold_start_item(interaction_count: int, threshold: int = 1) -> bool:
    """Determines if an item has zero or sub-threshold interactions."""
    return interaction_count < threshold


def compute_normalized_score(val: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Safely normalizes any scalar score to the [0.0, 1.0] range."""
    if max_val <= min_val:
        return 0.5
    normalized = (val - min_val) / (max_val - min_val)
    return float(np.clip(normalized, 0.0, 1.0))
