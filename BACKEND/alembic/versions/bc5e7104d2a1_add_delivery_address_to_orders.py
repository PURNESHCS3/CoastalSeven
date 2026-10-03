"""add delivery address to orders

Revision ID: bc5e7104d2a1
Revises: f184c2d9a732
Create Date: 2026-10-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "bc5e7104d2a1"
down_revision: Union[str, Sequence[str], None] = "f184c2d9a732"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "orders",
        sa.Column("delivery_address", sa.String(length=500), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("orders", "delivery_address")