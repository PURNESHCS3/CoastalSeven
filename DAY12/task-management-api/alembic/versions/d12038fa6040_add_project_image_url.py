"""add project image url

Revision ID: d12038fa6040
Revises: c02038fa6030
Create Date: 2026-09-30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d12038fa6040"
down_revision: Union[str, Sequence[str], None] = "c02038fa6030"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("projects")}
    if "image_url" not in columns:
        op.add_column("projects", sa.Column("image_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("projects", "image_url")
