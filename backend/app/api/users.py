from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_async_db
from app.models.db_models import User
from app.models.schemas import UserResponse, ColdStartUserCreateRequest

router = APIRouter(tags=["Users"])


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    is_cold_demo: bool = Query(None),
    db: AsyncSession = Depends(get_async_db),
):
    stmt = select(User)
    if is_cold_demo is not None:
        stmt = stmt.where(User.is_synthetic_cold_demo == is_cold_demo)
    stmt = stmt.limit(limit).offset(offset)
    result = await db.execute(stmt)
    users = result.scalars().all()
    return users


@router.post("/demo/cold-start/user", response_model=UserResponse)
async def create_cold_start_user(
    payload: ColdStartUserCreateRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """Register a new cold-start user persona for interactive demonstration."""
    import random
    user_id = payload.user_id or random.randint(900000000, 999999990)
    new_user = User(
        user_id=user_id,
        selected_categories=payload.selected_categories,
        is_synthetic_cold_demo=True,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
