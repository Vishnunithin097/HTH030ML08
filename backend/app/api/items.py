"""
Catalog Items API Controller.
Provides product searching, category browsing, and cold-start item simulation.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db
from app.models.schemas import ItemResponse, ColdStartItemCreateRequest
from app.core.catalog import catalog, CatalogItem

router = APIRouter(tags=["Items"])


def _get_val(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


@router.get("/items", response_model=List[ItemResponse])
async def list_items(
    search: Optional[str] = Query(None, description="Keyword search in product title/brand"),
    category: Optional[str] = Query(None, description="Category filter"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Retrieves catalog items with optional text search and category filtering.
    """
    catalog.initialize_from_metadata()
    all_items = list(catalog._items_cache.values())

    filtered = all_items
    if category:
        cat_lower = category.lower().strip()
        filtered = [i for i in filtered if cat_lower in str(_get_val(i, "category_name") or "").lower()]

    if search:
        search_lower = search.lower().strip()
        filtered = [
            i for i in filtered
            if search_lower in str(_get_val(i, "name") or "").lower()
            or search_lower in str(_get_val(i, "brand") or "").lower()
        ]

    paged = filtered[offset : offset + limit]

    return [
        ItemResponse(
            item_id=_get_val(i, "item_id"),
            name=_get_val(i, "name"),
            category_name=_get_val(i, "category_name"),
            subcategory=_get_val(i, "subcategory"),
            brand=_get_val(i, "brand"),
            price=float(_get_val(i, "price") or 299.0),
            margin_pct=float(_get_val(i, "margin_pct") or 20.0),
            inventory_count=int(_get_val(i, "inventory_count") or 100),
            quality_score=float(_get_val(i, "quality_score") or 0.8),
            tags=[str(_get_val(i, "category_name") or "General").lower()],
            is_synthetic_cold_demo=bool(_get_val(i, "is_cold_demo") or _get_val(i, "is_synthetic_cold_demo")),
        )
        for i in paged
    ]


@router.post("/demo/cold-start/item", response_model=ItemResponse)
async def create_cold_start_item(
    payload: ColdStartItemCreateRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Registers a brand-new cold-start catalog item for interactive demonstration.
    """
    import random
    item_id = random.randint(900000000, 999999990)

    new_catalog_item = CatalogItem(
        item_id=item_id,
        name=payload.name,
        category_name=payload.category_name,
        subcategory=payload.subcategory,
        brand=payload.brand,
        price=payload.price,
        margin_pct=payload.margin_pct,
        inventory_count=payload.inventory_count,
        quality_score=payload.quality_score,
        business_priority=payload.business_priority,
        source="synthetic_cold_demo",
        source_id=item_id,
        is_cold_demo=True,
    )

    # Register in in-memory catalog
    catalog._items_cache[item_id] = new_catalog_item

    return ItemResponse(
        item_id=item_id,
        name=payload.name,
        category_name=payload.category_name,
        subcategory=payload.subcategory,
        brand=payload.brand,
        description=payload.description,
        price=payload.price,
        margin_pct=payload.margin_pct,
        inventory_count=payload.inventory_count,
        quality_score=payload.quality_score,
        tags=payload.tags,
        is_synthetic_cold_demo=True,
    )
