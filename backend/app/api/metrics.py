from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db

router = APIRouter(prefix="/metrics", tags=["Metrics & Analytics"])


@router.get("/ranking")
async def get_ranking_metrics(db: AsyncSession = Depends(get_async_db)):
    """Placeholder ranking evaluation metrics (Phase 3/4)."""
    return {
        "ndcg_at_10": 0.742,
        "precision_at_10": 0.415,
        "recall_at_10": 0.380,
        "map": 0.521,
        "status": "baseline_mock_ready_for_phase_3"
    }


@router.get("/business")
async def get_business_metrics(db: AsyncSession = Depends(get_async_db)):
    """Placeholder business evaluation metrics (Phase 3/4)."""
    return {
        "average_margin_pct": 28.5,
        "inventory_turn_index": 1.42,
        "revenue_lift_pct": 14.8,
        "out_of_stock_avoidance_rate": 0.96,
        "status": "baseline_mock_ready_for_phase_3"
    }


@router.get("/diversity")
async def get_diversity_metrics(db: AsyncSession = Depends(get_async_db)):
    """Placeholder diversity evaluation metrics (Phase 3/4)."""
    return {
        "intra_list_diversity": 0.68,
        "category_coverage_pct": 82.4,
        "catalog_entropy": 3.85,
        "status": "baseline_mock_ready_for_phase_3"
    }
