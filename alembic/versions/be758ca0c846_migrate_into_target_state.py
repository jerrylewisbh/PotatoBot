"""Migrate into target state

Revision ID: be758ca0c846
Revises: 231a1345d050
Create Date: 2018-07-16 08:03:33.410493+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'be758ca0c846'
down_revision = '231a1345d050'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('user_auction_watchlist',
                    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=True),
                    sa.Column('item_id', sa.BigInteger(), nullable=True),
                    sa.Column('max_price', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['item_id'], ['item.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
    )

    op.drop_table('admins_old')
    op.drop_column('squads', 'silence_enabled')
    op.drop_column('squads', 'reminders_enabled')
    op.drop_column('squads', 'thorns_enabled')

def downgrade():
    pass
