"""Add photos_id migration

Revision ID: c2891c768aa0
Revises: 3f844352def9
Create Date: 2024-11-12 15:13:56.255298

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c2891c768aa0'
down_revision: Union[str, None] = '3f844352def9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('blog_categories')
    op.alter_column('blogs', 'photo_id',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.Integer(),
               existing_nullable=True,
               postgresql_using="photo_id::integer")
    op.create_foreign_key(None, 'blogs', 'photos', ['photo_id'], ['id'])
    op.drop_column('blogs', 'created_at')
    op.alter_column('comments', 'is_moderated',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text('false'))
    op.drop_constraint('fk_parent_id', 'comments', type_='foreignkey')
    op.create_foreign_key(None, 'comments', 'comments', ['parent_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'comments', type_='foreignkey')
    op.create_foreign_key('fk_parent_id', 'comments', 'comments', ['parent_id'], ['id'], ondelete='CASCADE')
    op.alter_column('comments', 'is_moderated',
               existing_type=sa.BOOLEAN(),
               nullable=False,
               existing_server_default=sa.text('false'))
    op.add_column('blogs', sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'blogs', type_='foreignkey')
    op.alter_column('blogs', 'photo_id',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
    op.create_table('blog_categories',
    sa.Column('blog_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('category_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['blog_id'], ['blogs.id'], name='blog_categories_blog_id_fkey'),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name='blog_categories_category_id_fkey'),
    sa.PrimaryKeyConstraint('blog_id', 'category_id', name='blog_categories_pkey')
    )
    # ### end Alembic commands ###