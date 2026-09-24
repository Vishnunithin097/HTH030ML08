"""002_add_image_and_source_fields

Revision ID: 002_add_image_and_source_fields
Revises: 001_initial_schema
Create Date: 2026-09-24 23:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_add_image_and_source_fields'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add source mapping columns
    op.add_column('items', sa.Column('bigbasket_product_id', sa.BigInteger(), nullable=True))
    op.add_column('items', sa.Column('retailrocket_item_id', sa.BigInteger(), nullable=True))
    op.add_column('items', sa.Column('image_source', sa.Text(), nullable=True, server_default='fallback'))
    op.add_column('items', sa.Column('image_status', sa.Text(), nullable=True, server_default='fallback'))

    op.create_index(op.f('ix_items_bigbasket_product_id'), 'items', ['bigbasket_product_id'], unique=False)
    op.create_index(op.f('ix_items_retailrocket_item_id'), 'items', ['retailrocket_item_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_items_retailrocket_item_id'), table_name='items')
    op.drop_index(op.f('ix_items_bigbasket_product_id'), table_name='items')
    op.drop_column('items', 'image_status')
    op.drop_column('items', 'image_source')
    op.drop_column('items', 'retailrocket_item_id')
    op.drop_column('items', 'bigbasket_product_id')
