"""Add extracted_posts column to linkedin_analysis

Revision ID: 002_add_linkedin_posts
Revises: 001_initial_schema
Create Date: 2026-08-01

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_add_linkedin_posts'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'linkedin_analysis',
        sa.Column('extracted_posts', sa.JSON(), nullable=True, server_default='[]')
    )


def downgrade() -> None:
    op.drop_column('linkedin_analysis', 'extracted_posts')