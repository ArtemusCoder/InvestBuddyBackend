"""Balance added

Revision ID: 128c138224bb
Revises: c3a7e9aae0ce
Create Date: 2023-12-11 02:37:57.801637

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '128c138224bb'
down_revision: Union[str, None] = 'c3a7e9aae0ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('personal_stocks', 'price')
    op.add_column('user', sa.Column('balance', sa.Integer(), nullable=False, server_default='0',))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'balance')
    op.add_column('personal_stocks', sa.Column('price', sa.INTEGER(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###