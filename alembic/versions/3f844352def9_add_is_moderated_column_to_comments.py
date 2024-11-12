"""Add is_moderated column to comments

Revision ID: 3f844352def9
Revises: 0159cab2adfb
Create Date: 2024-11-02 21:25:10.158829

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f844352def9'
down_revision: Union[str, None] = '0159cab2adfb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the is_moderated column to the comments table
    op.add_column('comments', sa.Column('is_moderated', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    # Remove the is_moderated column from the comments table
    op.drop_column('comments', 'is_moderated')

def upgrade():
    op.add_column('comments', sa.Column('parent_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'comments', 'comments', ['parent_id'], ['id'])

def downgrade():
    op.drop_column('comments', 'parent_id')
