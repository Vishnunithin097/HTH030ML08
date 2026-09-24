"""
Pydantic v2 Schemas for Request & Response Data Models.
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


# --- User Schemas ---
class UserBase(BaseModel):
    user_id: int
    selected_categories: List[str] = Field(default_factory=list)
    is_synthetic_cold_demo: bool = False


class UserCreate(UserBase):
    signup_date: Optional[datetime] = None


class UserResponse(UserBase):
    signup_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- Business Metadata Schemas ---
class BusinessMetadataBase(BaseModel):
    margin_pct: float = Field(default=20.0, ge=0.0, le=100.0)
    inventory_count: int = Field(default=100, ge=0)
    quality_score: float = Field(default=0.50, ge=0.0, le=1.0)
    business_priority: float = Field(default=0.0, ge=0.0, le=1.0)
    is_synthetic: bool = True


class BusinessMetadataResponse(BusinessMetadataBase):
    item_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- Item Schemas ---
class ItemBase(BaseModel):
    item_id: int
    bigbasket_product_id: Optional[int] = None
    retailrocket_item_id: Optional[int] = None
    name: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    rating: Optional[float] = None
    image_url: Optional[str] = None
    image_source: Optional[str] = "fallback"
    image_status: Optional[str] = "fallback"
    tags: List[str] = Field(default_factory=list)
    is_synthetic_cold_demo: bool = False


class ItemResponse(ItemBase):
    created_at: Optional[datetime] = None
    created_at_db: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    margin_pct: Optional[float] = None
    inventory_count: Optional[int] = None
    quality_score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


# --- Guardrail Config Schemas ---
class GuardrailConfigBase(BaseModel):
    min_inventory: int = Field(default=10, ge=0)
    min_margin: float = Field(default=20.0, ge=0.0, le=100.0)
    relevance_weight: float = Field(default=0.700, ge=0.0, le=1.0)
    business_weight: float = Field(default=0.300, ge=0.0, le=1.0)
    margin_weight: float = Field(default=0.400, ge=0.0, le=1.0)
    inventory_weight: float = Field(default=0.300, ge=0.0, le=1.0)
    quality_weight: float = Field(default=0.300, ge=0.0, le=1.0)
    cold_start_threshold: int = Field(default=3, ge=0)
    hard_filter_enabled: bool = False


class GuardrailConfigUpdate(BaseModel):
    min_inventory: Optional[int] = Field(default=None, ge=0)
    min_margin: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    relevance_weight: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    business_weight: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    margin_weight: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    inventory_weight: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    quality_weight: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    cold_start_threshold: Optional[int] = Field(default=None, ge=0)
    hard_filter_enabled: Optional[bool] = None


class GuardrailConfigResponse(GuardrailConfigBase):
    config_id: int
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- Recommendation Schemas ---
class RecommendationItem(BaseModel):
    item_id: int
    bigbasket_product_id: Optional[int] = None
    retailrocket_item_id: Optional[int] = None
    name: Optional[str] = None
    category_name: Optional[str] = None
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    image_source: Optional[str] = "fallback"
    image_status: Optional[str] = "fallback"
    rating: Optional[float] = None
    margin_pct: Optional[float] = None
    inventory_count: Optional[int] = None
    quality_score: Optional[float] = None
    collaborative_score: Optional[float] = None
    content_score: Optional[float] = None
    relevance_score: float
    business_score: Optional[float] = None
    penalty_score: Optional[float] = 0.0
    final_score: float
    rank: int
    explanation: str
    recommendation_source: str
    is_cold_start: bool = False
    penalty_reasons: List[str] = Field(default_factory=list)


class GuardrailHealthSummary(BaseModel):
    mode: str
    top_k: int
    churn_count: int
    filtered_items_count: int
    suppression_rate: float
    health_status: str
    health_message: str


class GMVProjectionSummary(BaseModel):
    projected_gmv: float
    projected_margin_inr: float
    avg_margin_pct: float
    stockout_risk_items: int


class RecommendationResponse(BaseModel):
    request_id: str
    user_id: int
    mode: str
    cold_start: bool
    cold_start_type: Optional[str] = None
    interaction_count: int
    total_recommendations: int
    guardrail_health: GuardrailHealthSummary
    gmv_projection: GMVProjectionSummary
    recommendations: List[RecommendationItem]


# --- Counterfactual & Explainability Schemas ---
class ExplanationResponse(BaseModel):
    item_id: int
    user_id: int
    name: str
    category_name: str
    brand: Optional[str] = None
    relevance_score: float
    business_score: Optional[float] = None
    collaborative_score: Optional[float] = None
    content_score: Optional[float] = None
    margin_pct: Optional[float] = None
    inventory_count: Optional[int] = None
    quality_score: Optional[float] = None
    explanation: str
    signal_breakdown: Dict[str, Any]


class CounterfactualResponse(BaseModel):
    item_id: int
    user_id: int
    baseline_score: float
    simulated_score: float
    score_delta: float
    simulated_business_score: float
    simulated_penalty: float
    reasons: List[str]
    summary: str


# --- Admin & Auth Schemas ---
class AdminLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str


# --- Cold Start Demo Payloads ---
class ColdStartUserCreateRequest(BaseModel):
    user_id: Optional[int] = None
    selected_categories: List[str] = Field(..., min_length=1)


class ColdStartItemCreateRequest(BaseModel):
    name: str
    category_name: str
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    price: float
    margin_pct: float = Field(default=30.0, ge=0, le=100)
    inventory_count: int = Field(default=100, ge=0)
    quality_score: float = Field(default=0.8, ge=0, le=1)
    business_priority: float = Field(default=0.5, ge=0, le=1)
    tags: List[str] = Field(default_factory=list)
