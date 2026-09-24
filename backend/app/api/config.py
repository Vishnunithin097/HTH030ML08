"""
Business Guardrail Configuration Controller.
Provides active policy retrieval and admin-authenticated updates.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_async_db
from app.models.db_models import GuardrailConfig
from app.models.schemas import GuardrailConfigResponse, GuardrailConfigUpdate
from app.auth.dependencies import get_current_admin
from app.business.guardrails import GuardrailPolicy

router = APIRouter(prefix="/config", tags=["Configuration"])

# In-memory singleton active policy cache for ultra-fast request evaluation
_active_policy = GuardrailPolicy()


def get_current_guardrail_policy() -> GuardrailPolicy:
    return _active_policy


@router.get("/guardrails", response_model=GuardrailConfigResponse)
async def get_guardrail_config(db: AsyncSession = Depends(get_async_db)):
    """
    Retrieves the currently active business guardrail parameters.
    """
    try:
        stmt = select(GuardrailConfig).order_by(GuardrailConfig.config_id.asc()).limit(1)
        result = await db.execute(stmt)
        config = result.scalar_one_or_none()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Guardrail config db fetch fallback to in-memory: {e}")
        config = None

    if not config:
        return GuardrailConfigResponse(
            config_id=1,
            min_inventory=_active_policy.min_inventory,
            min_margin=_active_policy.min_margin,
            relevance_weight=_active_policy.relevance_weight,
            business_weight=_active_policy.business_weight,
            margin_weight=_active_policy.margin_weight,
            inventory_weight=_active_policy.inventory_weight,
            quality_weight=_active_policy.quality_weight,
            cold_start_threshold=_active_policy.cold_start_threshold,
            hard_filter_enabled=_active_policy.hard_filter_enabled,
            updated_at=datetime.utcnow(),
        )

    # Sync in-memory policy
    _active_policy.min_inventory = config.min_inventory
    _active_policy.min_margin = float(config.min_margin)
    _active_policy.relevance_weight = float(config.relevance_weight)
    _active_policy.business_weight = float(config.business_weight)
    _active_policy.margin_weight = float(config.margin_weight)
    _active_policy.inventory_weight = float(config.inventory_weight)
    _active_policy.quality_weight = float(config.quality_weight)
    _active_policy.cold_start_threshold = config.cold_start_threshold
    _active_policy.hard_filter_enabled = config.hard_filter_enabled

    return config


@router.put("/guardrails", response_model=GuardrailConfigResponse)
async def update_guardrail_config(
    payload: GuardrailConfigUpdate,
    admin_auth: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Updates active business guardrail parameters (Requires Admin JWT Token).
    """
    # 1. Update in-memory active policy immediately
    if payload.min_inventory is not None:
        _active_policy.min_inventory = payload.min_inventory
    if payload.min_margin is not None:
        _active_policy.min_margin = payload.min_margin
    if payload.relevance_weight is not None:
        _active_policy.relevance_weight = payload.relevance_weight
    if payload.business_weight is not None:
        _active_policy.business_weight = payload.business_weight
    if payload.margin_weight is not None:
        _active_policy.margin_weight = payload.margin_weight
    if payload.inventory_weight is not None:
        _active_policy.inventory_weight = payload.inventory_weight
    if payload.quality_weight is not None:
        _active_policy.quality_weight = payload.quality_weight
    if payload.cold_start_threshold is not None:
        _active_policy.cold_start_threshold = payload.cold_start_threshold
    if payload.hard_filter_enabled is not None:
        _active_policy.hard_filter_enabled = payload.hard_filter_enabled

    # 2. Persist to PostgreSQL if connected
    config = None
    try:
        stmt = select(GuardrailConfig).order_by(GuardrailConfig.config_id.asc()).limit(1)
        result = await db.execute(stmt)
        config = result.scalar_one_or_none()

        if not config:
            config = GuardrailConfig(config_id=1)
            db.add(config)

        for field, val in payload.model_dump(exclude_unset=True).items():
            if val is not None:
                setattr(config, field, val)

        config.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(config)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Could not persist guardrail config to database (in-memory policy active): {e}")

    return GuardrailConfigResponse(
        config_id=config.config_id if config else 1,
        min_inventory=_active_policy.min_inventory,
        min_margin=_active_policy.min_margin,
        relevance_weight=_active_policy.relevance_weight,
        business_weight=_active_policy.business_weight,
        margin_weight=_active_policy.margin_weight,
        inventory_weight=_active_policy.inventory_weight,
        quality_weight=_active_policy.quality_weight,
        cold_start_threshold=_active_policy.cold_start_threshold,
        hard_filter_enabled=_active_policy.hard_filter_enabled,
        updated_at=config.updated_at if config else datetime.utcnow(),
    )
