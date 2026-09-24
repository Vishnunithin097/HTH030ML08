import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- User Schemas ---
class UserBase(BaseModel):
    user_id: int
    selected_categories: List[str] = Field(default_factory=list)
    is_synthetic_cold_demo: bool = False


class UserCreate(UserBase):
    signup_date: Optional[datetime] = None


class UserResponse(UserBase):
    signup_date: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Business Metadata Schemas ---
class BusinessMetadataBase(BaseModel):
    margin_pct: float = Field(default=20.0, ge=0.0, le=100.0)
    inventory_count: int = Field(default=100, ge=0)
    quality_score: float = Field(default=0.50, ge=0.0, le=1.0)
    business_priority: float = Field(default=0.0, ge=0.0, le=1.0)
    is_synthetic: bool = True


class BusinessMetadataCreate(BusinessMetadataBase):
    item_id: int


class BusinessMetadataResponse(BusinessMetadataBase):
    item_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Item Schemas ---
class ItemBase(BaseModel):
    item_id: int
    name: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    rating: Optional[float] = None
    image_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    is_synthetic_cold_demo: bool = False


class ItemCreate(ItemBase):
    created_at: Optional[datetime] = None


class ItemResponse(ItemBase):
    created_at: Optional[datetime] = None
    created_at_db: datetime
    updated_at: datetime
    business_metadata: Optional[BusinessMetadataResponse] = None

    model_config = ConfigDict(from_attributes=True)


# --- Interaction Schemas ---
class InteractionBase(BaseModel):
    user_id: int
    item_id: int
    event_type: str = Field(..., pattern="^(view|addtocart|transaction)$")
    event_weight: Optional[float] = None


class InteractionCreate(InteractionBase):
    timestamp: Optional[datetime] = None


class InteractionResponse(InteractionBase):
    id: int
    timestamp: datetime

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
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Recommendation Schemas ---
class RecommendationItem(BaseModel):
    item_id: int
    name: Optional[str] = None
    category_name: Optional[str] = None
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    rating: Optional[float] = None
    margin_pct: Optional[float] = None
    inventory_count: Optional[int] = None
    quality_score: Optional[float] = None
    collaborative_score: Optional[float] = None
    content_score: Optional[float] = None
    relevance_score: float
    business_score: Optional[float] = None
    final_score: float
    rank: int
    explanation: str
    recommendation_source: str
    is_cold_start: bool = False


class RecommendationResponse(BaseModel):
    user_id: int
    mode: str
    is_cold_start_user: bool
    interaction_count: int
    total_recommendations: int
    recommendations: List[RecommendationItem]


# --- Admin & Auth Schemas ---
class AdminLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


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
