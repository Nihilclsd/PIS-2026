from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class ResponseDto:
    """Read DTO: Ответ респондента"""
    
    response_id: str
    form_id: str
    answers: Dict[str, Any]
    started_at: datetime
    submitted_at: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    geo_country: Optional[str]
    geo_city: Optional[str]
    device_type: Optional[str]
    filling_time_sec: Optional[int]
    quality_score: Optional[float]
    is_suspect: Optional[bool]
    suspect_reason: Optional[str]
    
    @classmethod
    def from_domain(cls, response) -> "ResponseDto":
        """Создаёт DTO из доменной сущности Response"""
        return cls(
            response_id=response.response_id,  # ← было response.id, исправлено
            form_id=response.form_id,
            answers=response.answers,
            started_at=response.started_at,
            submitted_at=response.submitted_at,
            ip_address=response.ip_address,
            user_agent=response.user_agent,
            geo_country=response.geo_country,
            geo_city=response.geo_city,
            device_type=response.device_type,
            filling_time_sec=response.filling_time_sec,
            quality_score=response.quality_score,
            is_suspect=response.is_suspect,
            suspect_reason=response.suspect_reason,
        )