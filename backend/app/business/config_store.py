"""
Guardrail Configuration Caching & Store.
Reads and caches active business policy parameters from PostgreSQL.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.db_models import GuardrailConfig


class GuardrailConfigStore:
    """Provides fast access to database guardrail parameters."""

    def __init__(self):
        self._cached_config: Optional[GuardrailConfig] = None

    async def get_active_config(self, db: AsyncSession) -> GuardrailConfig:
        stmt = select(GuardrailConfig).order_by(GuardrailConfig.config_id.asc()).limit(1)
        result = db.execute(stmt)
        config = result.scalar_one_or_none()
        if not config:
            config = GuardrailConfig()
        return config


config_store = GuardrailConfigStore()
