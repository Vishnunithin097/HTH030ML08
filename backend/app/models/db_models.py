import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Text,
    Numeric,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    CheckConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, index=True)
    signup_date = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=text("CURRENT_TIMESTAMP"))
    selected_categories = Column(ARRAY(Text), nullable=False, default=list, server_default=text("'{}'"))
    is_synthetic_cold_demo = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, server_default=text("CURRENT_TIMESTAMP"))

    # Relationships
    interactions = relationship("Interaction", back_populates="user", cascade="all, delete-orphan")
    recommendation_logs = relationship("RecommendationLog", back_populates="user", cascade="all, delete-orphan")


class Item(Base):
    __tablename__ = "items"

    item_id = Column(BigInteger, primary_key=True, index=True)
    bigbasket_product_id = Column(BigInteger, nullable=True, index=True)
    retailrocket_item_id = Column(BigInteger, nullable=True, index=True)
    name = Column(Text, nullable=True)
    category_id = Column(Integer, nullable=True)
    category_name = Column(Text, nullable=True)
    subcategory = Column(Text, nullable=True)
    brand = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    rating = Column(Numeric(3, 2), nullable=True)
    image_url = Column(Text, nullable=True)
    image_source = Column(Text, nullable=True, default="fallback")
    image_status = Column(Text, nullable=True, default="fallback")
    tags = Column(ARRAY(Text), nullable=False, default=list, server_default=text("'{}'"))
    created_at = Column(DateTime, nullable=True)
    is_synthetic_cold_demo = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    created_at_db = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, server_default=text("CURRENT_TIMESTAMP"))

    # Relationships
    business_metadata = relationship("BusinessMetadata", back_populates="item", uselist=False, cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="item", cascade="all, delete-orphan")
    recommendation_logs = relationship("RecommendationLog", back_populates="item", cascade="all, delete-orphan")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    item_id = Column(BigInteger, ForeignKey("items.item_id", ondelete="CASCADE"), nullable=False)
    event_type = Column(Text, nullable=False)
    event_weight = Column(Numeric(5, 2), nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=text("CURRENT_TIMESTAMP"))

    # Relationships
    user = relationship("User", back_populates="interactions")
    item = relationship("Item", back_populates="interactions")

    __table_args__ = (
        CheckConstraint("event_type IN ('view', 'addtocart', 'transaction')", name="chk_event_type"),
        Index("idx_interactions_user", "user_id"),
        Index("idx_interactions_item", "item_id"),
        Index("idx_interactions_user_item", "user_id", "item_id"),
        Index("idx_interactions_timestamp", "timestamp"),
        Index("idx_interactions_event_type", "event_type"),
    )


class BusinessMetadata(Base):
    __tablename__ = "business_metadata"

    item_id = Column(BigInteger, ForeignKey("items.item_id", ondelete="CASCADE"), primary_key=True)
    margin_pct = Column(Numeric(5, 2), nullable=False, default=20.00, server_default=text("20.00"))
    inventory_count = Column(Integer, nullable=False, default=100, server_default=text("100"))
    quality_score = Column(Numeric(3, 2), nullable=False, default=0.50, server_default=text("0.50"))
    business_priority = Column(Numeric(3, 2), nullable=False, default=0.00, server_default=text("0.00"))
    is_synthetic = Column(Boolean, nullable=False, default=True, server_default=text("TRUE"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, server_default=text("CURRENT_TIMESTAMP"))

    # Relationship
    item = relationship("Item", back_populates="business_metadata")

    __table_args__ = (
        CheckConstraint("margin_pct >= 0 AND margin_pct <= 100", name="chk_margin_pct"),
        CheckConstraint("inventory_count >= 0", name="chk_inventory_count"),
        CheckConstraint("quality_score >= 0 AND quality_score <= 1", name="chk_quality_score"),
        CheckConstraint("business_priority >= 0 AND business_priority <= 1", name="chk_business_priority"),
        Index("idx_business_inventory", "inventory_count"),
        Index("idx_business_margin", "margin_pct"),
        Index("idx_business_quality", "quality_score"),
    )


class GuardrailConfig(Base):
    __tablename__ = "guardrail_config"

    config_id = Column(Integer, primary_key=True, autoincrement=True)
    min_inventory = Column(Integer, nullable=False, default=10, server_default=text("10"))
    min_margin = Column(Numeric(5, 2), nullable=False, default=20.00, server_default=text("20.00"))
    relevance_weight = Column(Numeric(4, 3), nullable=False, default=0.700, server_default=text("0.700"))
    business_weight = Column(Numeric(4, 3), nullable=False, default=0.300, server_default=text("0.300"))
    margin_weight = Column(Numeric(4, 3), nullable=False, default=0.400, server_default=text("0.400"))
    inventory_weight = Column(Numeric(4, 3), nullable=False, default=0.300, server_default=text("0.300"))
    quality_weight = Column(Numeric(4, 3), nullable=False, default=0.300, server_default=text("0.300"))
    cold_start_threshold = Column(Integer, nullable=False, default=3, server_default=text("3"))
    hard_filter_enabled = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        CheckConstraint("min_inventory >= 0", name="chk_min_inventory"),
        CheckConstraint("min_margin >= 0 AND min_margin <= 100", name="chk_min_margin"),
        CheckConstraint("relevance_weight >= 0 AND relevance_weight <= 1", name="chk_relevance_weight"),
        CheckConstraint("business_weight >= 0 AND business_weight <= 1", name="chk_business_weight"),
        CheckConstraint("margin_weight >= 0 AND margin_weight <= 1", name="chk_margin_weight"),
        CheckConstraint("inventory_weight >= 0 AND inventory_weight <= 1", name="chk_inventory_weight"),
        CheckConstraint("quality_weight >= 0 AND quality_weight <= 1", name="chk_quality_weight"),
        CheckConstraint("cold_start_threshold >= 0", name="chk_cold_start_threshold"),
    )


class RecommendationLog(Base):
    __tablename__ = "recommendation_logs"

    request_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    mode = Column(Text, nullable=False)
    item_id = Column(BigInteger, ForeignKey("items.item_id", ondelete="CASCADE"), nullable=False)
    collaborative_score = Column(Numeric(6, 5), nullable=True)
    content_score = Column(Numeric(6, 5), nullable=True)
    relevance_score = Column(Numeric(6, 5), nullable=True)
    business_score = Column(Numeric(6, 5), nullable=True)
    final_score = Column(Numeric(6, 5), nullable=True)
    rank = Column(Integer, nullable=True)
    explanation = Column(Text, nullable=True)
    recommendation_source = Column(Text, nullable=True)
    cold_start = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=text("CURRENT_TIMESTAMP"))

    # Relationships
    user = relationship("User", back_populates="recommendation_logs")
    item = relationship("Item", back_populates="recommendation_logs")

    __table_args__ = (
        CheckConstraint("mode IN ('pure', 'business_aware')", name="chk_recommendation_mode"),
        Index("idx_recommendation_user", "user_id"),
        Index("idx_recommendation_item", "item_id"),
        Index("idx_recommendation_created", "created_at"),
        Index("idx_recommendation_mode", "mode"),
    )


class Admin(Base):
    __tablename__ = "admins"

    admin_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(Text, unique=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    role = Column(Text, nullable=False, default="admin", server_default=text("'admin'"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        CheckConstraint("role = 'admin'", name="chk_admin_role"),
    )
