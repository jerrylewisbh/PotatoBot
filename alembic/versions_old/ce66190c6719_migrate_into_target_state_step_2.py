"""Migrate into target state - Step 2

Revision ID: ce66190c6719
Revises: be758ca0c846
Create Date: 2018-07-16 08:09:47.572743+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'ce66190c6719'
down_revision = 'be758ca0c846'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'users',
        'is_api_profile_allowed',
        existing_type=mysql.TINYINT(display_width=4),
        nullable=False,
        server_default=sa.text('false')
    )
    op.alter_column(
        'users',
        'is_api_stock_allowed',
        existing_type=mysql.TINYINT(display_width=4),
        nullable=False,
        server_default=sa.text('false')
    )
    op.alter_column(
        'users',
        'is_api_trade_allowed',
        existing_type=mysql.TINYINT(display_width=4),
        nullable=False,
        server_default = sa.text('false')
    )


def downgrade():
    pass
