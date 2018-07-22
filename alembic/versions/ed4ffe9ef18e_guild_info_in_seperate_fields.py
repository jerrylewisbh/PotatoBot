"""Guild info in seperate fields

Revision ID: ed4ffe9ef18e
Revises: cb6e81b49983
Create Date: 2018-07-22 17:54:52.769126+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ed4ffe9ef18e'
down_revision = 'cb6e81b49983'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('characters', sa.Column('guild', sa.UnicodeText(length=250), nullable=True))
    op.add_column('characters', sa.Column('guild_tag', sa.UnicodeText(length=10), nullable=True))
    op.drop_column('characters', 'maxStamina')
    op.drop_index('cw_id', table_name='item')

    # Index has to be created by hand since there doesn't seem to be a way to specify index-length in alembic?!
    connection = op.get_bind()
    connection.execute("CREATE UNIQUE INDEX ix_item_cw_id ON item (cw_id(25))")

def downgrade():
    # Sorry, no downgrade :-/
    pass

