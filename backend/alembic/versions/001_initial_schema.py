"""001_initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-24 17:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable pgcrypto for password hashing and uuid generation
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    # 2. Users table
    op.create_table(
        'users',
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('signup_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('selected_categories', postgresql.ARRAY(sa.Text()), server_default=sa.text("'{}'"), nullable=False),
        sa.Column('is_synthetic_cold_demo', sa.Boolean(), server_default=sa.text('FALSE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=False)

    # 3. Items table
    op.create_table(
        'items',
        sa.Column('item_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.Text(), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('category_name', sa.Text(), nullable=True),
        sa.Column('subcategory', sa.Text(), nullable=True),
        sa.Column('brand', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('rating', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.Text()), server_default=sa.text("'{}'"), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('is_synthetic_cold_demo', sa.Boolean(), server_default=sa.text('FALSE'), nullable=False),
        sa.Column('created_at_db', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('item_id')
    )
    op.create_index(op.f('ix_items_item_id'), 'items', ['item_id'], unique=False)

    # 4. Interactions table
    op.create_table(
        'interactions',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('item_id', sa.BigInteger(), nullable=False),
        sa.Column('event_type', sa.Text(), nullable=False),
        sa.Column('event_weight', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint("event_type IN ('view', 'addtocart', 'transaction')", name='chk_event_type'),
        sa.ForeignKeyConstraint(['item_id'], ['items.item_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_interactions_event_type', 'interactions', ['event_type'], unique=False)
    op.create_index('idx_interactions_item', 'interactions', ['item_id'], unique=False)
    op.create_index('idx_interactions_timestamp', 'interactions', ['timestamp'], unique=False)
    op.create_index('idx_interactions_user', 'interactions', ['user_id'], unique=False)
    op.create_index('idx_interactions_user_item', 'interactions', ['user_id', 'item_id'], unique=False)

    # 5. Business Metadata table
    op.create_table(
        'business_metadata',
        sa.Column('item_id', sa.BigInteger(), nullable=False),
        sa.Column('margin_pct', sa.Numeric(precision=5, scale=2), server_default=sa.text('20.00'), nullable=False),
        sa.Column('inventory_count', sa.Integer(), server_default=sa.text('100'), nullable=False),
        sa.Column('quality_score', sa.Numeric(precision=3, scale=2), server_default=sa.text('0.50'), nullable=False),
        sa.Column('business_priority', sa.Numeric(precision=3, scale=2), server_default=sa.text('0.00'), nullable=False),
        sa.Column('is_synthetic', sa.Boolean(), server_default=sa.text('TRUE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint('business_priority >= 0 AND business_priority <= 1', name='chk_business_priority'),
        sa.CheckConstraint('inventory_count >= 0', name='chk_inventory_count'),
        sa.CheckConstraint('margin_pct >= 0 AND margin_pct <= 100', name='chk_margin_pct'),
        sa.CheckConstraint('quality_score >= 0 AND quality_score <= 1', name='chk_quality_score'),
        sa.ForeignKeyConstraint(['item_id'], ['items.item_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('item_id')
    )
    op.create_index('idx_business_inventory', 'business_metadata', ['inventory_count'], unique=False)
    op.create_index('idx_business_margin', 'business_metadata', ['margin_pct'], unique=False)
    op.create_index('idx_business_quality', 'business_metadata', ['quality_score'], unique=False)

    # 6. Guardrail Config table
    op.create_table(
        'guardrail_config',
        sa.Column('config_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('min_inventory', sa.Integer(), server_default=sa.text('10'), nullable=False),
        sa.Column('min_margin', sa.Numeric(precision=5, scale=2), server_default=sa.text('20.00'), nullable=False),
        sa.Column('relevance_weight', sa.Numeric(precision=4, scale=3), server_default=sa.text('0.700'), nullable=False),
        sa.Column('business_weight', sa.Numeric(precision=4, scale=3), server_default=sa.text('0.300'), nullable=False),
        sa.Column('margin_weight', sa.Numeric(precision=4, scale=3), server_default=sa.text('0.400'), nullable=False),
        sa.Column('inventory_weight', sa.Numeric(precision=4, scale=3), server_default=sa.text('0.300'), nullable=False),
        sa.Column('quality_weight', sa.Numeric(precision=4, scale=3), server_default=sa.text('0.300'), nullable=False),
        sa.Column('cold_start_threshold', sa.Integer(), server_default=sa.text('3'), nullable=False),
        sa.Column('hard_filter_enabled', sa.Boolean(), server_default=sa.text('FALSE'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint('business_weight >= 0 AND business_weight <= 1', name='chk_business_weight'),
        sa.CheckConstraint('cold_start_threshold >= 0', name='chk_cold_start_threshold'),
        sa.CheckConstraint('inventory_weight >= 0 AND inventory_weight <= 1', name='chk_inventory_weight'),
        sa.CheckConstraint('margin_weight >= 0 AND margin_weight <= 1', name='chk_margin_weight'),
        sa.CheckConstraint('min_inventory >= 0', name='chk_min_inventory'),
        sa.CheckConstraint('min_margin >= 0 AND min_margin <= 100', name='chk_min_margin'),
        sa.CheckConstraint('quality_weight >= 0 AND quality_weight <= 1', name='chk_quality_weight'),
        sa.CheckConstraint('relevance_weight >= 0 AND relevance_weight <= 1', name='chk_relevance_weight'),
        sa.PrimaryKeyConstraint('config_id')
    )

    # 7. Recommendation Logs table
    op.create_table(
        'recommendation_logs',
        sa.Column('request_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('mode', sa.Text(), nullable=False),
        sa.Column('item_id', sa.BigInteger(), nullable=False),
        sa.Column('collaborative_score', sa.Numeric(precision=6, scale=5), nullable=True),
        sa.Column('content_score', sa.Numeric(precision=6, scale=5), nullable=True),
        sa.Column('relevance_score', sa.Numeric(precision=6, scale=5), nullable=True),
        sa.Column('business_score', sa.Numeric(precision=6, scale=5), nullable=True),
        sa.Column('final_score', sa.Numeric(precision=6, scale=5), nullable=True),
        sa.Column('rank', sa.Integer(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('recommendation_source', sa.Text(), nullable=True),
        sa.Column('cold_start', sa.Boolean(), server_default=sa.text('FALSE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint("mode IN ('pure', 'business_aware')", name='chk_recommendation_mode'),
        sa.ForeignKeyConstraint(['item_id'], ['items.item_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('request_id')
    )
    op.create_index('idx_recommendation_created', 'recommendation_logs', ['created_at'], unique=False)
    op.create_index('idx_recommendation_item', 'recommendation_logs', ['item_id'], unique=False)
    op.create_index('idx_recommendation_mode', 'recommendation_logs', ['mode'], unique=False)
    op.create_index('idx_recommendation_user', 'recommendation_logs', ['user_id'], unique=False)

    # 8. Admins table
    op.create_table(
        'admins',
        sa.Column('admin_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.Text(), nullable=False),
        sa.Column('hashed_password', sa.Text(), nullable=False),
        sa.Column('role', sa.Text(), server_default=sa.text("'admin'"), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint("role = 'admin'", name='chk_admin_role'),
        sa.PrimaryKeyConstraint('admin_id'),
        sa.UniqueConstraint('username')
    )

    # 9. Seed Default Guardrail Config
    op.execute("""
        INSERT INTO guardrail_config (
            min_inventory,
            min_margin,
            relevance_weight,
            business_weight,
            margin_weight,
            inventory_weight,
            quality_weight,
            cold_start_threshold,
            hard_filter_enabled
        )
        SELECT 10, 20.00, 0.700, 0.300, 0.400, 0.300, 0.300, 3, FALSE
        WHERE NOT EXISTS (SELECT 1 FROM guardrail_config);
    """)

    # 10. Seed Default Admin (admin / Admin@123 using bcrypt)
    op.execute("""
        INSERT INTO admins (username, hashed_password, role)
        SELECT 'admin', crypt('Admin@123', gen_salt('bf', 12)), 'admin'
        WHERE NOT EXISTS (SELECT 1 FROM admins WHERE username = 'admin');
    """)

    # 11. Seed Cold-Start Demo User (user_id = 999999999)
    op.execute("""
        INSERT INTO users (user_id, signup_date, selected_categories, is_synthetic_cold_demo)
        VALUES (999999999, CURRENT_TIMESTAMP, ARRAY['Sports', 'Running', 'Fitness'], TRUE)
        ON CONFLICT (user_id) DO NOTHING;
    """)

    # 12. Seed Cold-Start Demo Item (item_id = 999999998)
    op.execute("""
        INSERT INTO items (
            item_id, name, category_id, category_name, subcategory, brand, description, price, rating, image_url, tags, created_at, is_synthetic_cold_demo
        )
        VALUES (
            999999998,
            'Demo Running Shoe',
            9999,
            'Sports',
            'Running',
            'DemoBrand',
            'Lightweight running shoe designed for daily training and fitness activities.',
            4999.00,
            4.50,
            'https://via.placeholder.com/400x400?text=Running+Shoe',
            ARRAY['running', 'sports', 'fitness', 'shoes'],
            CURRENT_TIMESTAMP,
            TRUE
        )
        ON CONFLICT (item_id) DO NOTHING;
    """)

    # 13. Seed Business Metadata for Demo Item
    op.execute("""
        INSERT INTO business_metadata (item_id, margin_pct, inventory_count, quality_score, business_priority, is_synthetic)
        VALUES (999999998, 35.00, 100, 0.90, 0.80, TRUE)
        ON CONFLICT (item_id) DO NOTHING;
    """)


def downgrade() -> None:
    op.drop_table('admins')
    op.drop_table('recommendation_logs')
    op.drop_table('guardrail_config')
    op.drop_table('business_metadata')
    op.drop_table('interactions')
    op.drop_table('items')
    op.drop_table('users')
