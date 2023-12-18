"""Ticker added

Revision ID: 892b31df4c12
Revises: f5e848217e92
Create Date: 2023-12-11 18:54:25.074667

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '892b31df4c12'
down_revision: Union[str, None] = 'f5e848217e92'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stock', sa.Column('ticker', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('stock', 'ticker')
    # ### end Alembic commands ###
