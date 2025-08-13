"""Add PDF storage fields

Revision ID: 0003_add_pdf_storage
Revises: 0002_expand_policy_fields
Create Date: 2025-08-13 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None

def upgrade():
    """Add PDF storage fields to policies table"""
    with op.batch_alter_table('policies') as batch_op:
        # Add new columns for PDF storage
        batch_op.add_column(sa.Column('pdf_file_path', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('pdf_file_size', sa.Integer(), nullable=True))

def downgrade():
    """Remove PDF storage fields from policies table"""
    with op.batch_alter_table('policies') as batch_op:
        batch_op.drop_column('pdf_file_size')
        batch_op.drop_column('pdf_file_path')
