"""
Business Impact Simulator API Controller.
Provides simulation/estimation endpoints for admin evaluation of recommendation revenue & margin potential.
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_admin
from app.core.catalog import catalog
from app.business.guardrails import GuardrailPolicy
from app.api.config import get_current_guardrail_policy

router = APIRouter(prefix="/simulation", tags=["Simulation"])


class BusinessImpactRequest(BaseModel):
    users_exposed: int = Field(..., gt=0, description="Number of users exposed to recommendations")
    recommendations_per_user: int = Field(..., gt=0, description="Number of recommendations per user")
    ctr: float = Field(..., ge=0.0, description="Estimated Click-Through Rate (as decimal e.g. 0.12 or percentage e.g. 12)")
    conversion_rate: float = Field(..., ge=0.0, description="Estimated Conversion Rate (as decimal e.g. 0.04 or percentage e.g. 4)")
    average_order_value: float = Field(..., ge=0.0, description="Average Order Value in INR")
    margin_percentage: float = Field(..., ge=0.0, description="Average Gross Margin % (as decimal e.g. 0.22 or percentage e.g. 22)")
    user_id: Optional[int] = Field(None, description="Optional shopper context ID for product-level simulation")


class ProductContributionItem(BaseModel):
    item_id: int
    name: str
    category_name: str
    price: float
    margin_pct: float
    inventory_count: int
    quality_score: float
    business_priority: str
    estimated_contribution: float


class ModeComparisonSummary(BaseModel):
    mode: str
    products_considered: int
    avg_price: float
    avg_margin_pct: float
    estimated_revenue: float
    estimated_gross_margin: float


class BusinessImpactResponse(BaseModel):
    total_impressions: int
    estimated_clicks: float
    estimated_conversions: float
    estimated_revenue: float
    estimated_gross_margin: float
    assumptions: Dict[str, Any]
    product_contributions: List[ProductContributionItem]
    pure_vs_business_aware: Dict[str, ModeComparisonSummary]
    disclaimer: str


@router.post("/business-impact", response_model=BusinessImpactResponse)
async def calculate_business_impact(
    payload: BusinessImpactRequest,
    admin_auth: dict = Depends(get_current_admin),
):
    """
    Simulates estimated business impact (impressions, clicks, conversions, revenue, gross margin)
    based on admin assumptions and existing business metadata. (Requires Admin JWT Token)
    """
    # 1. Validation & Normalization
    if payload.users_exposed <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number of users exposed must be greater than 0.",
        )

    if payload.recommendations_per_user <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recommendations per user must be greater than 0.",
        )

    ctr = float(payload.ctr)
    if ctr > 1.0:
        ctr = ctr / 100.0
    if ctr < 0.0 or ctr > 1.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Click-through rate (CTR) must be between 0% and 100%.",
        )

    conv = float(payload.conversion_rate)
    if conv > 1.0:
        conv = conv / 100.0
    if conv < 0.0 or conv > 1.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversion rate must be between 0% and 100%.",
        )

    if payload.average_order_value < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Average order value must be non-negative.",
        )

    margin = float(payload.margin_percentage)
    if margin > 1.0:
        margin = margin / 100.0
    if margin < 0.0 or margin > 1.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Margin percentage must be between 0% and 100%.",
        )

    # 2. Macro Formula Calculation
    total_impressions = payload.users_exposed * payload.recommendations_per_user
    estimated_clicks = round(total_impressions * ctr, 2)
    estimated_conversions = round(estimated_clicks * conv, 2)
    estimated_revenue = round(estimated_conversions * payload.average_order_value, 2)
    estimated_gross_margin = round(estimated_revenue * margin, 2)

    # 3. Product-Level Simulation using Catalog Business Metadata
    catalog.initialize_from_metadata()
    sample_items = list(catalog._items_cache.values())[:payload.recommendations_per_user]
    if not sample_items:
        sample_items = []

    product_contributions: List[ProductContributionItem] = []
    conversions_per_slot = estimated_conversions / max(len(sample_items), 1)

    for item in sample_items:
        item_id = int(item.get("item_id", 0))
        name = str(item.get("name", "Product"))
        category = str(item.get("category_name", "General"))
        price = float(item.get("price") or payload.average_order_value or 100.0)
        item_margin = float(item.get("margin_pct") or (margin * 100.0))
        inventory = int(item.get("inventory_count") or 100)
        quality = float(item.get("quality_score") or 0.8)

        # Priority label based on margin & inventory
        if item_margin >= 30 and inventory >= 50:
            priority = "High Margin & Stock"
        elif item_margin >= 25:
            priority = "High Margin"
        elif inventory < 20:
            priority = "Low Inventory"
        else:
            priority = "Standard"

        # Estimated contribution = expected units sold * price * item margin %
        est_item_contrib = round(conversions_per_slot * price * (item_margin / 100.0), 2)

        product_contributions.append(
            ProductContributionItem(
                item_id=item_id,
                name=name,
                category_name=category,
                price=price,
                margin_pct=item_margin,
                inventory_count=inventory,
                quality_score=quality,
                business_priority=priority,
                estimated_contribution=est_item_contrib,
            )
        )

    # 4. Pure Relevance vs Business-Aware Side-by-Side Simulation
    all_catalog_items = list(catalog._items_cache.values())
    if all_catalog_items:
        pure_sample = sorted(all_catalog_items, key=lambda x: float(x.get("rating") or 4.0), reverse=True)[:payload.recommendations_per_user]
        guarded_sample = sorted(all_catalog_items, key=lambda x: float(x.get("margin_pct") or 20.0), reverse=True)[:payload.recommendations_per_user]
    else:
        pure_sample = sample_items
        guarded_sample = sample_items

    pure_avg_price = sum(float(i.get("price") or 100.0) for i in pure_sample) / max(len(pure_sample), 1)
    pure_avg_margin = sum(float(i.get("margin_pct") or 20.0) for i in pure_sample) / max(len(pure_sample), 1)

    guarded_avg_price = sum(float(i.get("price") or 100.0) for i in guarded_sample) / max(len(guarded_sample), 1)
    guarded_avg_margin = sum(float(i.get("margin_pct") or 25.0) for i in guarded_sample) / max(len(guarded_sample), 1)

    pure_est_rev = round(estimated_conversions * pure_avg_price, 2)
    pure_est_margin = round(pure_est_rev * (pure_avg_margin / 100.0), 2)

    guarded_est_rev = round(estimated_conversions * guarded_avg_price, 2)
    guarded_est_margin = round(guarded_est_rev * (guarded_avg_margin / 100.0), 2)

    pure_vs_business_aware = {
        "pure_relevance": ModeComparisonSummary(
            mode="Pure Relevance",
            products_considered=len(pure_sample),
            avg_price=round(pure_avg_price, 2),
            avg_margin_pct=round(pure_avg_margin, 2),
            estimated_revenue=pure_est_rev,
            estimated_gross_margin=pure_est_margin,
        ),
        "business_aware": ModeComparisonSummary(
            mode="Business-Aware",
            products_considered=len(guarded_sample),
            avg_price=round(guarded_avg_price, 2),
            avg_margin_pct=round(guarded_avg_margin, 2),
            estimated_revenue=guarded_est_rev,
            estimated_gross_margin=guarded_est_margin,
        ),
    }

    return BusinessImpactResponse(
        total_impressions=total_impressions,
        estimated_clicks=estimated_clicks,
        estimated_conversions=estimated_conversions,
        estimated_revenue=estimated_revenue,
        estimated_gross_margin=estimated_gross_margin,
        assumptions={
            "users_exposed": payload.users_exposed,
            "recommendations_per_user": payload.recommendations_per_user,
            "ctr_pct": round(ctr * 100, 2),
            "conversion_rate_pct": round(conv * 100, 2),
            "average_order_value_inr": payload.average_order_value,
            "margin_percentage_pct": round(margin * 100, 2),
        },
        product_contributions=product_contributions,
        pure_vs_business_aware=pure_vs_business_aware,
        disclaimer="Simulation only. Actual outcomes depend on user behavior, conversion, pricing, inventory and other business factors.",
    )
