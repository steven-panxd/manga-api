"""empty message

Revision ID: 2e224e82f35b
Revises: 
Create Date: 2019-12-07 19:16:24.349014

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e224e82f35b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('is_deleted', sa.SmallInteger(), nullable=False))
    op.add_column('identity', sa.Column('is_deleted', sa.SmallInteger(), nullable=False))
    op.add_column('post', sa.Column('is_deleted', sa.SmallInteger(), nullable=False))
    op.add_column('user', sa.Column('is_deleted', sa.SmallInteger(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'is_deleted')
    op.drop_column('post', 'is_deleted')
    op.drop_column('identity', 'is_deleted')
    op.drop_column('comment', 'is_deleted')
    # ### end Alembic commands ###
