"""Expand policy fields for comprehensive insurance data

Revision ID: 0002
Revises: 0001_init
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001_init'
branch_labels = None
depends_on = None


def upgrade():
    # Add remaining new columns to policies table that don't already exist
    with op.batch_alter_table('policies', schema=None) as batch_op:
        # Additional policy information that may be missing
        try:
            batch_op.add_column(sa.Column('renewal_date', sa.Date(), nullable=True))
        except:
            pass  # Column already exists
        try:
            batch_op.add_column(sa.Column('group_number', sa.String(100), nullable=True))
        except:
            pass  # Column already exists
        try:
            batch_op.add_column(sa.Column('employer_name', sa.String(255), nullable=True))
        except:
            pass  # Column already exists


def downgrade():
    # Remove the added columns that were successfully added
    with op.batch_alter_table('policies', schema=None) as batch_op:
        try:
            batch_op.drop_column('employer_name')
        except:
            pass
        try:
            batch_op.drop_column('group_number')
        except:
            pass
        try:
            batch_op.drop_column('renewal_date')
        except:
            pass
