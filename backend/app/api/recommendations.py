"""
Recommendation Engine API Controller.
Exposes public endpoints for Pure and Business-Aware recommendations,
signal-derived explanations, counterfactual simulations, and recommendation audit logs.
"""
import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_async_db
from app.models.db_models import User, Item, RecommendationLog
from app.models.schemas import (
    RecommendationResponse,
    ExplanationResponse,
    CounterfactualResponse,
    GuardrailHealthSummary,
    GMVProjectionSummary,
    RecommendationItem,
)
from app.core.catalog import catalog, CatalogItem
from app.recommenders.hybrid import hybrid_recommender
from app.recommenders.cold_start import cold_start_engine
from app.business.guardrails import guardrail_evaluator
from app.business.reranker import reranker
from app.business.revenue_impact import revenue_calculator
from app.explainability.explain import explainability_engine
from app.api.config import get_current_guardrail_policy

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("", response_model=RecommendationResponse)
async def get_recommendations(
    user_id: int = Query(..., description="Shopper User ID"),
    mode: str = Query("business_aware", pattern="^(pure|business_aware)$", description="Recommendation mode"),
    limit: int = Query(10, ge=1, le=50, description="Top-K recommendations count"),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Generates personalized recommendations in Pure Engagement or Business-Aware modes.
    """
    request_id = str(uuid.uuid4())
    policy = get_current_guardrail_policy()

    # 1. Fetch Shopper Profile & Interacted Items
    selected_categories = ["General"]
    interaction_count = 0
    interacted_ids = []
    is_cold_shopper = False
    cold_type = None

    try:
        stmt = select(User).where(User.user_id == user_id)
        res = await db.execute(stmt)
        user_record = res.scalar_one_or_none()
        if user_record:
            selected_categories = user_record.selected_categories or ["General"]
            if user_record.is_synthetic_cold_demo:
                is_cold_shopper = True
                cold_type = "synthetic_cold_demo_shopper"
    except Exception:
        pass

    # Check if user is unseen/cold in the recommender engine
    if not is_cold_shopper:
        is_cold_shopper = cold_start_engine.is_cold_user(interaction_count, threshold=policy.cold_start_threshold)
        if is_cold_shopper:
            cold_type = "new_shopper_zero_history"

    # 2. Retrieve Candidate Items
    catalog.initialize_from_metadata()
    # Filter candidates by category preference if cold shopper, else broader candidate pool
    if is_cold_shopper and selected_categories:
        candidate_pool = []
        for cat in selected_categories:
            candidate_pool.extend(catalog.get_items_by_category(cat, limit=30))
        if not candidate_pool:
            candidate_pool = list(catalog._items_cache.values())[:100]
    else:
        candidate_pool = list(catalog._items_cache.values())[:150]

    # 3. Generate ML Candidate Scores (Layer 1)
    raw_candidates = hybrid_recommender.recommend(
        user_id=user_id,
        interaction_count=interaction_count if not is_cold_shopper else 0,
        interacted_item_ids=interacted_ids,
        selected_categories=selected_categories,
        candidate_items=candidate_pool,
        limit=max(limit * 2, 20),
    )

    # 4. Apply Business Guardrails & Re-Ranking (Layer 2)
    ranked_slate, health_diag = reranker.rank(
        candidates=raw_candidates,
        mode=mode,
        policy=policy,
        top_k=limit,
    )

    # 5. Attach Signal-Backed Explanations (Layer 3)
    response_items: List[RecommendationItem] = []
    for item in ranked_slate:
        explanation = explainability_engine.explain(
            item=item,
            user_category_preferences=selected_categories,
            is_cold_user=is_cold_shopper,
        )
        item["explanation"] = explanation

        response_items.append(RecommendationItem(
            item_id=item["item_id"],
            name=item.get("name"),
            category_name=item.get("category_name"),
            subcategory=item.get("subcategory"),
            brand=item.get("brand"),
            price=item.get("price"),
            image_url=item.get("image_url", "https://via.placeholder.com/300x300?text=Product"),
            rating=item.get("rating", 4.0),
            margin_pct=item.get("margin_pct"),
            inventory_count=item.get("inventory_count"),
            quality_score=item.get("quality_score"),
            collaborative_score=item.get("collaborative_score"),
            content_score=item.get("content_score"),
            relevance_score=item.get("relevance_score", 0.5),
            business_score=item.get("business_score"),
            penalty_score=item.get("penalty_score", 0.0),
            final_score=item.get("final_score", 0.5),
            rank=item.get("rank", 1),
            explanation=explanation,
            recommendation_source=item.get("recommendation_source", "hybrid"),
            is_cold_start=item.get("is_cold_start", False),
            penalty_reasons=item.get("penalty_reasons", []),
        ))

    # 6. Simulate Commercial GMV / Margin Impact
    pure_slate_baseline, _ = reranker.rank(candidates=raw_candidates, mode="pure", policy=policy, top_k=limit)
    sim_impact = revenue_calculator.simulate_impact(pure_slate=pure_slate_baseline, guarded_slate=ranked_slate)
    gmv_info = (
        sim_impact["business_aware_mode"]
        if mode == "business_aware"
        else sim_impact["pure_mode"]
    )

    # 7. Asynchronously Log Recommendations for Analytics
    try:
        logs_to_insert = [
            RecommendationLog(
                request_id=uuid.UUID(request_id),
                user_id=user_id,
                mode=mode,
                item_id=r.item_id,
                collaborative_score=r.collaborative_score,
                content_score=r.content_score,
                relevance_score=r.relevance_score,
                business_score=r.business_score,
                final_score=r.final_score,
                rank=r.rank,
                explanation=r.explanation,
                recommendation_source=r.recommendation_source,
                cold_start=r.is_cold_start,
            )
            for r in response_items
        ]
        db.add_all(logs_to_insert)
        await db.commit()
    except Exception:
        # Non-blocking logging failure
        pass

    return RecommendationResponse(
        request_id=request_id,
        user_id=user_id,
        mode=mode,
        cold_start=is_cold_shopper,
        cold_start_type=cold_type,
        interaction_count=interaction_count,
        total_recommendations=len(response_items),
        guardrail_health=GuardrailHealthSummary(
            mode=health_diag.get("mode", mode),
            top_k=health_diag.get("top_k", limit),
            churn_count=health_diag.get("churn_count", 0),
            filtered_items_count=health_diag.get("filtered_items_count", 0),
            suppression_rate=health_diag.get("suppression_rate", 0.0),
            health_status=health_diag.get("health_status", "healthy"),
            health_message=health_diag.get("health_message", "Optimal"),
        ),
        gmv_projection=GMVProjectionSummary(
            projected_gmv=gmv_info["projected_gmv"],
            projected_margin_inr=gmv_info["projected_margin_inr"],
            avg_margin_pct=gmv_info["avg_margin_pct"],
            stockout_risk_items=gmv_info["stockout_risk_items"],
        ),
        recommendations=response_items,
    )


@router.get("/{item_id}/explain", response_model=ExplanationResponse)
async def get_item_explanation(
    item_id: int,
    user_id: int = Query(..., description="Shopper Context User ID"),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Returns an audited breakdown of signal attribution and score decomposition for an item.
    """
    catalog.initialize_from_metadata()
    item = catalog.get_item(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item #{item_id} not found in catalog",
        )

    # Compute signals
    cf_score = hybrid_recommender.recommend(user_id=user_id, candidate_items=[item])
    item_dict = item.to_dict()
    if cf_score:
        item_dict.update(cf_score[0])

    explanation = explainability_engine.explain(item_dict)

    return ExplanationResponse(
        item_id=item_id,
        user_id=user_id,
        name=item.name,
        category_name=item.category_name,
        brand=item.brand,
        relevance_score=item_dict.get("relevance_score", 0.5),
        business_score=item_dict.get("business_score"),
        collaborative_score=item_dict.get("collaborative_score"),
        content_score=item_dict.get("content_score"),
        margin_pct=item.margin_pct,
        inventory_count=item.inventory_count,
        quality_score=item.quality_score,
        explanation=explanation,
        signal_breakdown={
            "collaborative_available": item_dict.get("collaborative_score") is not None,
            "content_available": item_dict.get("content_score") is not None,
            "is_cold_demo_item": item.is_cold_demo,
            "category": item.category_name,
            "margin_pct": item.margin_pct,
            "inventory_count": item.inventory_count,
        },
    )


@router.get("/{item_id}/counterfactual", response_model=CounterfactualResponse)
async def get_counterfactual_analysis(
    item_id: int,
    user_id: int = Query(..., description="Shopper User ID"),
    hypothetical_min_margin: Optional[float] = Query(None, description="Hypothetical margin floor (%)"),
    hypothetical_min_inventory: Optional[int] = Query(None, description="Hypothetical inventory floor (units)"),
    hypothetical_margin_pct: Optional[float] = Query(None, description="Simulated item margin (%)"),
    hypothetical_inventory_count: Optional[int] = Query(None, description="Simulated item inventory"),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Executes an on-demand sensitivity simulation on how guardrail parameter shifts impact ranking.
    """
    catalog.initialize_from_metadata()
    item = catalog.get_item(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item #{item_id} not found in catalog",
        )

    policy = get_current_guardrail_policy()
    relevance = 0.70  # Baseline estimated relevance

    cf_eval = guardrail_evaluator.evaluate_counterfactual(
        relevance_score=relevance,
        margin_pct=item.margin_pct,
        inventory_count=item.inventory_count,
        quality_score=item.quality_score,
        current_final_score=0.68,
        hypothetical_min_margin=hypothetical_min_margin,
        hypothetical_min_inventory=hypothetical_min_inventory,
        hypothetical_margin_pct=hypothetical_margin_pct,
        hypothetical_inventory_count=hypothetical_inventory_count,
        policy=policy,
    )

    return CounterfactualResponse(
        item_id=item_id,
        user_id=user_id,
        baseline_score=cf_eval["baseline_score"],
        simulated_score=cf_eval["simulated_score"],
        score_delta=cf_eval["score_delta"],
        simulated_business_score=cf_eval["simulated_business_score"],
        simulated_penalty=cf_eval["simulated_penalty"],
        reasons=cf_eval["reasons"],
        summary=cf_eval["summary"],
    )
