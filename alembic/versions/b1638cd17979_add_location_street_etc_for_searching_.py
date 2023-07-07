"""add location_street etc for searching by address rather than street sweeping segments

Revision ID: b1638cd17979
Revises: afb2cc76dacc
Create Date: 2023-07-05 20:33:14.299771

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1638cd17979'
down_revision = 'afb2cc76dacc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('citations', sa.Column('location_street', sa.String(length=255), nullable=True))
    op.add_column('citations', sa.Column('location_number', sa.Integer(), nullable=True))
    op.add_column('citations', sa.Column('location_suffix', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('citations', 'location_suffix')
    op.drop_column('citations', 'location_number')
    op.drop_column('citations', 'location_street')
    # ### end Alembic commands ###