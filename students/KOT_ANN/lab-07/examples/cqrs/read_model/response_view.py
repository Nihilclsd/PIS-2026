from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ResponseView:
    """Read Model: денормализованное представление ответа для быстрых запросов"""
    
    response_id: str
    form_id: str
    form_title: Optional[str]  # денормализовано из Form
    answers: dict
    rating: Optional[int]  # денормализовано из answers
    comment: Optional[str]  # денормализовано из answers
    started_at: datetime
    submitted_at: datetime
    filling_time_sec: int
    ip_address: Optional[str]
    country: Optional[str]  # денормализовано из гео
    city: Optional[str]  # денормализовано из гео
    device_type: Optional[str]
    is_suspect: bool
    quality_score: float
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_domain(cls, response, form_title: Optional[str] = None) -> "ResponseView":
        """Создаёт Read Model из доменного агрегата"""
        rating = response.answers.get("rating") if response.answers else None
        comment = response.answers.get("comment") if response.answers else None
        
        return cls(
            response_id=response.response_id,
            form_id=response.form_id,
            form_title=form_title,
            answers=response.answers,
            rating=rating,
            comment=comment,
            started_at=response.started_at,
            submitted_at=response.submitted_at,
            filling_time_sec=response.filling_time_sec or 0,
            ip_address=response.ip_address,
            country=response.geo_country,
            city=response.geo_city,
            device_type=response.device_type,
            is_suspect=response.is_suspect or False,
            quality_score=response.quality_score or 0.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )