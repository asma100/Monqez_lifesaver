"""Add user_id to Volunteer

Revision ID: 03cefe8e8ed8
Revises: 2de4c8485360
Create Date: 2025-07-28 18:20:29.004083

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '03cefe8e8ed8'
down_revision = '2de4c8485360'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('volunteer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key('fk_volunteer_user', 'User', ['user_id'], ['id'])  # 🔧 named constraint

def downgrade():
    with op.batch_alter_table('volunteer', schema=None) as batch_op:
        batch_op.drop_constraint('fk_volunteer_user', type_='foreignkey')  # 🔧 must match the name
        batch_op.drop_column('user_id')
