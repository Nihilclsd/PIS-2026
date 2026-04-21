"""Add response_views table for Read Model

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.create_table(
        'response_views',
        sa.Column('response_id', sa.String(64), primary_key=True, nullable=False),
        sa.Column('form_id', sa.String(64), nullable=False),
        sa.Column('form_title', sa.String(255), nullable=True),
        sa.Column('answers', sa.JSON, nullable=False),
        sa.Column('rating', sa.Integer, nullable=True),
        sa.Column('comment', sa.String(1000), nullable=True),
        sa.Column('started_at', sa.DateTime, nullable=False),
        sa.Column('submitted_at', sa.DateTime, nullable=False),
        sa.Column('filling_time_sec', sa.Integer, nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('device_type', sa.String(50), nullable=True),
        sa.Column('is_suspect', sa.Boolean, nullable=False, default=False),
        sa.Column('quality_score', sa.Float, nullable=False, default=0.0),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
        sa.Index('idx_response_views_form_id', 'form_id'),
        sa.Index('idx_response_views_form_submitted', 'form_id', 'submitted_at'),
        sa.Index('idx_response_views_rating', 'form_id', 'rating'),
        sa.Index('idx_response_views_suspect', 'form_id', 'is_suspect'),
    )


def downgrade() -> None:
    op.drop_table('response_views')