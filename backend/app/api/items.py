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
    paged = catalog.search_items(search=search, category=category, offset=offset, limit=limit)

    return [
        ItemResponse(
            item_id=_get_val(i, "item_id"),
            bigbasket_product_id=_get_val(i, "bigbasket_product_id"),
            retailrocket_item_id=_get_val(i, "retailrocket_item_id"),
            name=_get_val(i, "name"),
            category_name=_get_val(i, "category_name"),
            subcategory=_get_val(i, "subcategory"),
            brand=_get_val(i, "brand"),
            description=_get_val(i, "description"),
            price=float(_get_val(i, "price") or 299.0),
            rating=float(_get_val(i, "rating") or 4.0),
            image_url=_get_val(i, "image_url"),
            image_source=_get_val(i, "image_source", "fallback"),
            image_status=_get_val(i, "image_status", "fallback"),
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
        description=payload.description,
        price=payload.price,
        margin_pct=payload.margin_pct,
        inventory_count=payload.inventory_count,
        quality_score=payload.quality_score,
        business_priority=payload.business_priority,
        source="synthetic_cold_demo",
        source_id=item_id,
        is_cold_demo=True,
    )

    # Register in unified catalog abstraction
    catalog.add_item(new_catalog_item.to_dict())

    return ItemResponse(
        item_id=item_id,
        bigbasket_product_id=None,
        retailrocket_item_id=None,
        name=payload.name,
        category_name=payload.category_name,
        subcategory=payload.subcategory,
        brand=payload.brand,
        description=payload.description,
        price=payload.price,
        image_url=new_catalog_item.image_url,
        image_source=new_catalog_item.image_source,
        image_status=new_catalog_item.image_status,
        margin_pct=payload.margin_pct,
        inventory_count=payload.inventory_count,
        quality_score=payload.quality_score,
        tags=payload.tags or [payload.category_name.lower()],
        is_synthetic_cold_demo=True,
    )
