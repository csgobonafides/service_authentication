"""two_migration

Revision ID: 8c1be29560ad
Revises: 9e6f09c081c7
Create Date: 2025-01-25 19:37:45.850561

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c1be29560ad'
down_revision: Union[str, None] = '9e6f09c081c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'user_model', ['login'])
    op.create_unique_constraint(None, 'user_model', ['email'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user_model', type_='unique')
    op.drop_constraint(None, 'user_model', type_='unique')
    # ### end Alembic commands ###
