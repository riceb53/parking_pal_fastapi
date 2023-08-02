"""add citation_issued_day_of_week

Revision ID: f18e26ed5250
Revises: 8a935984dccf
Create Date: 2023-07-12 13:16:00.406725

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f18e26ed5250'
down_revision = '8a935984dccf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('citations', sa.Column('citation_issued_day_of_week', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('citations', 'citation_issued_day_of_week')
    # ### end Alembic commands ###
