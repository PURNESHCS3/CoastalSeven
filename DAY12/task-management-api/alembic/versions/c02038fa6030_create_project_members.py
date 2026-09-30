"""create project members association table

Revision ID: c02038fa6030
Revises: b01027ef5929
Create Date: 2026-09-29 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c02038fa6030'
down_revision: Union[str, Sequence[str], None] = 'b01027ef5929'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if table already created
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if 'project_members' not in insp.get_table_names():
        op.create_table(
            'project_members',
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('project_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('user_id', 'project_id')
        )


def downgrade() -> None:
    op.drop_table('project_members')
