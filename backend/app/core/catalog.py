"""
Unified Catalog Abstraction Layer.

This module provides an explicit abstraction separating:
1. Database Catalog Items (Internal entity representation)
2. RetailRocket Collaborative Latent Factors (Item ID space)
3. BigBasket Content-Based Feature Vectors (Product ID space)

IMPORTANT ARCHITECTURAL RULE:
Never assume RetailRocket item_id == BigBasket product_id.
This catalog abstraction provides the contract and lookup registry without inventing false mappings.
"""
from typing import Dict, Optional, Any, List
import pandas as pd
import numpy as np


class CatalogManager:
    """
    Manages the unified item catalog and decouples the collaborative
    and content-based index spaces from database IDs.
    """

    def __init__(self):
        self._item_to_collaborative_idx: Dict[int, int] = {}
        self._item_to_content_idx: Dict[int, int] = {}
        self._catalog_metadata: Optional[pd.DataFrame] = None
        self._is_initialized: bool = False

    def is_ready(self) -> bool:
        return self._is_initialized

    def register_mappings(
        self,
        item_to_collab: Dict[int, int],
        item_to_content: Dict[int, int],
        metadata_df: Optional[pd.DataFrame] = None
    ) -> None:
        """Register explicit item ID mappings created during Phase 2 ingestion."""
        self._item_to_collaborative_idx = item_to_collab
        self._item_to_content_idx = item_to_content
        self._catalog_metadata = metadata_df
        self._is_initialized = True

    def get_collaborative_index(self, item_id: int) -> Optional[int]:
        """Returns the internal SVD item factor index for a given catalog item ID."""
        return self._item_to_collaborative_idx.get(item_id)

    def get_content_index(self, item_id: int) -> Optional[int]:
        """Returns the TF-IDF matrix row index for a given catalog item ID."""
        return self._item_to_content_idx.get(item_id)

    def get_item_metadata(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve cached catalog metadata for fast feature enrichment."""
        if self._catalog_metadata is None:
            return None
        # In Phase 2 this will perform O(1) indexed lookup
        return None


# Global singleton catalog instance
catalog_manager = CatalogManager()
