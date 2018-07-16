from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '231a1345d050'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.drop_column('characters', 'testing_squad')

    op.add_column('groups', sa.Column('allow_bots', sa.Boolean(), nullable=False))

    op.alter_column('groups', 'fwd_minireport', existing_type=mysql.TINYINT(display_width=1), nullable=False, existing_server_default=sa.text("'0'"))
    op.alter_column('location', 'name', existing_type=mysql.VARCHAR(charset='utf8mb4', length=255), nullable=True)
    op.alter_column('location', 'selectable', existing_type=mysql.TINYINT(display_width=4), nullable=False, existing_server_default=sa.text("'0'"))

    op.alter_column('user_quest', 'pledge', existing_type=mysql.TINYINT(display_width=4), nullable=False, existing_server_default=sa.text("'0'"))
    op.alter_column('user_quest', 'successful', existing_type=mysql.TINYINT(display_width=4), nullable=False, existing_server_default=sa.text("'0'"))
    op.alter_column('users', 'setting_automated_deal_report', existing_type=mysql.TINYINT(display_width=4), nullable=False, existing_server_default=sa.text("'1'"))

    op.alter_column('users', 'setting_automated_hiding', existing_type=mysql.TINYINT(display_width=4), nullable=False, existing_server_default=sa.text("'0'"))
    op.alter_column('users', 'setting_automated_report', existing_type=mysql.TINYINT(display_width=4), nullable=False, existing_server_default=sa.text("'1'"))
    op.alter_column('users', 'setting_automated_sniping', existing_type=mysql.TINYINT(display_width=4), nullable=False, existing_server_default=sa.text("'0'"))
    op.alter_column('users', 'sniping_suspended', existing_type=mysql.TINYINT(display_width=4), nullable=False, existing_server_default=sa.text("'0'"))

def downgrade():
    pass
