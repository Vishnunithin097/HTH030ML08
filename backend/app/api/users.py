"""
Users and Cold-Start Shopper API Controller.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_async_db
from app.models.db_models import User
from app.models.schemas import UserResponse, ColdStartUserCreateRequest

router = APIRouter(tags=["Users"])

# In-memory mock shoppers for fast demonstration fallback
_cached_demo_users = [
    UserResponse(
        user_id=999999999,
        signup_date=datetime.utcnow(),
        selected_categories=["Sports", "Running", "Fitness"],
        is_synthetic_cold_demo=True,
    ),
    UserResponse(
        user_id=111016,
        signup_date=datetime.utcnow(),
        selected_categories=["Beauty & Hygiene", "Beverages"],
        is_synthetic_cold_demo=False,
    ),
    UserResponse(
        user_id=257597,
        signup_date=datetime.utcnow(),
        selected_categories=["Gourmet & World Food", "Snacks & Branded Foods"],
        is_synthetic_cold_demo=False,
    ),
    UserResponse(
        user_id=992329,
        signup_date=datetime.utcnow(),
        selected_categories=["Cleaning & Household", "Kitchen, Garden & Pets"],
        is_synthetic_cold_demo=False,
    ),
]


from app.core.catalog import catalog

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    is_cold_demo: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Retrieves available shopper profiles with their cold-start status and category preferences.
    """
    db_users: List[User] = []
    try:
        stmt = select(User)
        if is_cold_demo is not None:
            stmt = stmt.where(User.is_synthetic_cold_demo == is_cold_demo)
        stmt = stmt.order_by(User.created_at.desc()).limit(limit).offset(offset)
        res = db.execute(stmt)
        db_users = list(res.scalars().all())
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Database user query failed, serving cached demo users: {e}")

    # Merge cached demo users and db users (avoiding duplicates)
    seen_ids = set()
    merged: List[UserResponse] = []

    # First add any cached demo users (e.g. freshly created)
    for u in _cached_demo_users:
        if is_cold_demo is not None and u.is_synthetic_cold_demo != is_cold_demo:
            continue
        if u.user_id not in seen_ids:
            seen_ids.add(u.user_id)
            merged.append(u)

    # Then append database users
    for u in db_users:
        if u.user_id not in seen_ids:
            seen_ids.add(u.user_id)
            merged.append(
                UserResponse(
                    user_id=u.user_id,
                    signup_date=u.signup_date,
                    selected_categories=list(u.selected_categories or []),
                    is_synthetic_cold_demo=u.is_synthetic_cold_demo,
                    is_cold_start=u.is_synthetic_cold_demo,
                    interaction_count=0 if u.is_synthetic_cold_demo else 12,
                )
            )

    return merged[offset : offset + limit]


@router.post("/demo/cold-start/user", response_model=UserResponse)
async def create_cold_start_user(
    payload: ColdStartUserCreateRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Spawns a new cold-start shopper persona with declared category preferences.
    """
    import random
    user_id = payload.user_id or random.randint(900000000, 999999990)

    # Create UserResponse with explicit cold start and zero interactions
    new_user = UserResponse(
        user_id=user_id,
        signup_date=datetime.utcnow(),
        selected_categories=list(payload.selected_categories),
        is_synthetic_cold_demo=True,
        is_cold_start=True,
        interaction_count=0,
    )
    # Register in in-memory caches and catalog immediately
    _cached_demo_users.insert(0, new_user)
    catalog.add_user(
        user_id=user_id,
        categories=list(payload.selected_categories),
        is_cold=True,
    )

    # Also persist to DB if available
    try:
        db_user = User(
            user_id=user_id,
            signup_date=datetime.utcnow(),
            selected_categories=list(payload.selected_categories),
            is_synthetic_cold_demo=True,
        )
        db.add(db_user)
        db.commit()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Database write for demo user #{user_id} failed (in-memory only): {e}")

    return new_user
