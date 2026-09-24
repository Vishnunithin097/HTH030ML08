from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_async_db
from app.models.db_models import GuardrailConfig, Admin
from app.models.schemas import GuardrailConfigResponse, GuardrailConfigUpdate
from app.auth.dependencies import get_current_admin

router = APIRouter(prefix="/config", tags=["Configuration"])


@router.get("/guardrails", response_model=GuardrailConfigResponse)
async def get_guardrail_config(db: AsyncSession = Depends(get_async_db)):
    """Retrieve active business guardrail configuration."""
    stmt = select(GuardrailConfig).order_by(GuardrailConfig.config_id.asc()).limit(1)
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    if not config:
        # Fallback default creation if table empty
        config = GuardrailConfig(
            min_inventory=10,
            min_margin=20.0,
            relevance_weight=0.700,
            business_weight=0.300,
            margin_weight=0.400,
            inventory_weight=0.300,
            quality_weight=0.300,
            cold_start_threshold=3,
            hard_filter_enabled=False,
        )
        db.add(config)
        await db.commit()
        await db.refresh(config)
    return config


@router.put("/guardrails", response_model=GuardrailConfigResponse)
async def update_guardrail_config(
    update_data: GuardrailConfigUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_async_db),
):
    """Update active business guardrail configuration (Requires Admin Auth)."""
    stmt = select(GuardrailConfig).order_by(GuardrailConfig.config_id.asc()).limit(1)
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    if not config:
        config = GuardrailConfig()
        db.add(config)

    for field, value in update_data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(config, field, value)

    await db.commit()
    await db.refresh(config)
    return config
