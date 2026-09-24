"""
Feature extraction and vector calculation utilities.
"""
from typing import List, Dict, Any
import numpy as np


def build_user_preference_vector(category_names: List[str], category_to_index: Dict[str, int]) -> np.ndarray:
    """Builds a binary or weighted preference vector across available categories."""
    vec = np.zeros(len(category_to_index), dtype=np.float32)
    for cat in category_names:
        if cat in category_to_index:
            vec[category_to_index[cat]] = 1.0
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec
