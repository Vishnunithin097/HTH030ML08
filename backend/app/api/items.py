from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_async_db
from app.models.db_models import Item, BusinessMetadata
from app.models.schemas import ItemResponse, ColdStartItemCreateRequest

router = APIRouter(tags=["Items"])


@router.get("/items", response_model=List[ItemResponse])
async def list_items(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category_name: Optional[str] = Query(None),
    is_cold_demo: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_async_db),
):
    stmt = select(Item).options(selectinload(Item.business_metadata))
    if category_name:
        stmt = stmt.where(Item.category_name == category_name)
    if is_cold_demo is not None:
        stmt = stmt.where(Item.is_synthetic_cold_demo == is_cold_demo)
    stmt = stmt.limit(limit).offset(offset)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return items


@router.post("/demo/cold-start/item", response_model=ItemResponse)
async def create_cold_start_item(
    payload: ColdStartItemCreateRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """Register a new cold-start item for interactive demonstration."""
    import random
    item_id = random.randint(900000000, 999999990)
    new_item = Item(
        item_id=item_id,
        name=payload.name,
        category_name=payload.category_name,
        subcategory=payload.subcategory,
        brand=payload.brand,
        description=payload.description,
        price=payload.price,
        rating=payload.quality_score * 5.0,
        tags=payload.tags,
        is_synthetic_cold_demo=True,
    )
    db.add(new_item)
    await db.flush()

    new_meta = BusinessMetadata(
        item_id=item_id,
        margin_pct=payload.margin_pct,
        inventory_count=payload.inventory_count,
        quality_score=payload.quality_score,
        business_priority=payload.business_priority,
        is_synthetic=True,
    )
    db.add(new_meta)
    await db.commit()
    await db.refresh(new_item)
    return new_item
