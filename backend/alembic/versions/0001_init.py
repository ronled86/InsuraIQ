"""initial tables

Revision ID: 0001_init
Revises:
Create Date: 2025-08-10 00:00:00

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('policies',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False, index=True),
        sa.Column('owner_name', sa.String(), nullable=False),
        sa.Column('insurer', sa.String(), nullable=False),
        sa.Column('product_type', sa.String(), nullable=False),
        sa.Column('policy_number', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('start_date', sa.String()),
        sa.Column('end_date', sa.String()),
        sa.Column('premium_monthly', sa.Float(), server_default='0'),
        sa.Column('deductible', sa.Float(), server_default='0'),
        sa.Column('coverage_limit', sa.Float(), server_default='0'),
        sa.Column('notes', sa.String(), server_default=''),
        sa.Column('active', sa.Boolean(), server_default=sa.text('1')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_table('compare_history',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False, index=True),
        sa.Column('policy_ids_csv', sa.String(), nullable=False),
        sa.Column('result_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, index=True),
    )

def downgrade():
    op.drop_table('compare_history')
    op.drop_table('policies')