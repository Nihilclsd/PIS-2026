"""Initial migration - create responses, forms, form_aggregates tables

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'responses',
        sa.Column('response_id', sa.String(64), primary_key=True, nullable=False),
        sa.Column('form_id', sa.String(64), nullable=False),
        sa.Column('answers', sa.JSON, nullable=False),
        sa.Column('started_at', sa.DateTime, nullable=False),
        sa.Column('submitted_at', sa.DateTime, nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(512), nullable=True),
        sa.Column('geo_country', sa.String(100), nullable=True),
        sa.Column('geo_city', sa.String(100), nullable=True),
        sa.Column('device_type', sa.String(50), nullable=True),
        sa.Column('device_os', sa.String(50), nullable=True),
        sa.Column('device_browser', sa.String(50), nullable=True),
        sa.Column('filling_time_sec', sa.Integer, nullable=True),
        sa.Column('quality_score', sa.Float, nullable=True),
        sa.Column('is_suspect', sa.Boolean, nullable=True),
        sa.Column('suspect_reason', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Index('idx_responses_form_id', 'form_id'),
        sa.Index('idx_responses_is_suspect', 'is_suspect'),
    )

    op.create_table(
        'forms',
        sa.Column('form_id', sa.String(64), primary_key=True, nullable=False),
        sa.Column('fields', sa.JSON, nullable=False),
        sa.Column('min_filling_time_sec', sa.Integer, default=30),
        sa.Column('min_comment_length', sa.Integer, default=3),
        sa.Column('block_repeating_chars', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )

    op.create_table(
        'form_aggregates',
        sa.Column('form_id', sa.String(64), primary_key=True, nullable=False),
        sa.Column('total_responses', sa.Integer, default=0),
        sa.Column('quality_responses', sa.Integer, default=0),
        sa.Column('suspect_responses', sa.Integer, default=0),
        sa.Column('average_rating', sa.Float, default=0.0),
        sa.Column('rating_sum', sa.Float, default=0.0),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    op.drop_table('form_aggregates')
    op.drop_table('forms')
    op.drop_table('responses')