from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Boolean, Index
from infrastructure.config.database import Base


class ResponseModel(Base):
    __tablename__ = "responses"

    response_id = Column(String(64), primary_key=True, index=True)
    form_id = Column(String(64), nullable=False, index=True)
    answers = Column(JSON, nullable=False)
    started_at = Column(DateTime, nullable=False)
    submitted_at = Column(DateTime, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(512), nullable=True)
    geo_country = Column(String(100), nullable=True)
    geo_city = Column(String(100), nullable=True)
    device_type = Column(String(50), nullable=True)
    device_os = Column(String(50), nullable=True)
    device_browser = Column(String(50), nullable=True)
    filling_time_sec = Column(Integer, nullable=True)
    quality_score = Column(Float, nullable=True)
    is_suspect = Column(Boolean, nullable=True)
    suspect_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False)


class FormModel(Base):
    __tablename__ = "forms"

    form_id = Column(String(64), primary_key=True, index=True)
    fields = Column(JSON, nullable=False)
    min_filling_time_sec = Column(Integer, default=30)
    min_comment_length = Column(Integer, default=3)
    block_repeating_chars = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False)


class FormAggregatesModel(Base):
    __tablename__ = "form_aggregates"

    form_id = Column(String(64), primary_key=True, index=True)
    total_responses = Column(Integer, default=0)
    quality_responses = Column(Integer, default=0)
    suspect_responses = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    rating_sum = Column(Float, default=0.0)
    updated_at = Column(DateTime, nullable=False)


class ResponseViewModel(Base):
    """Read Model: денормализованная таблица для быстрых запросов"""
    __tablename__ = "response_views"
    
    response_id = Column(String(64), primary_key=True, index=True)
    form_id = Column(String(64), nullable=False, index=True)
    form_title = Column(String(255), nullable=True)
    answers = Column(JSON, nullable=False)
    rating = Column(Integer, nullable=True)
    comment = Column(String(1000), nullable=True)
    started_at = Column(DateTime, nullable=False)
    submitted_at = Column(DateTime, nullable=False)
    filling_time_sec = Column(Integer, nullable=False)
    ip_address = Column(String(45), nullable=True)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    device_type = Column(String(50), nullable=True)
    is_suspect = Column(Boolean, nullable=False, default=False, index=True)
    quality_score = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)


# Индексы для оптимизации запросов
Index("idx_response_views_form_submitted", ResponseViewModel.form_id, ResponseViewModel.submitted_at)
Index("idx_response_views_rating", ResponseViewModel.form_id, ResponseViewModel.rating)
Index("idx_response_views_suspect", ResponseViewModel.form_id, ResponseViewModel.is_suspect)