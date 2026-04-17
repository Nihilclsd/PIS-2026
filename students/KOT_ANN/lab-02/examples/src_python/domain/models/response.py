"""
Доменная сущность: Ответ респондента.
Содержит бизнес-логику, связанную с ответом.
"""

from typing import Dict, Any, Optional
from datetime import datetime


class Response:
    """Доменная модель ответа на форму"""
    
    def __init__(
        self,
        response_id: str,
        form_id: str,
        answers: Dict[str, Any],
        started_at: datetime,
        submitted_at: datetime,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        self.id = response_id
        self.form_id = form_id
        self.answers = answers
        self.started_at = started_at
        self.submitted_at = submitted_at
        self.ip_address = ip_address
        self.user_agent = user_agent
        
        # Обогащённые данные (заполняются позже)
        self.geo_country: Optional[str] = None
        self.geo_city: Optional[str] = None
        self.device_type: Optional[str] = None
        self.filling_time_sec: Optional[int] = None
        self.quality_score: Optional[float] = None
        self.is_suspect: Optional[bool] = None
        self.suspect_reason: Optional[str] = None
    
    def calculate_filling_time(self) -> int:
        """Вычисляет время заполнения формы в секундах"""
        delta = self.submitted_at - self.started_at
        return int(delta.total_seconds())
    
    def enrich_geo(self, country: str, city: str) -> None:
        """Обогащает ответ гео-данными"""
        self.geo_country = country
        self.geo_city = city
    
    def enrich_device(self, device_type: str) -> None:
        """Обогащает ответ данными об устройстве"""
        self.device_type = device_type
    
    def classify(
        self, 
        quality_score: float, 
        is_suspect: bool, 
        suspect_reason: Optional[str] = None
    ) -> None:
        """Классифицирует ответ (качественный / отписка)"""
        self.quality_score = quality_score
        self.is_suspect = is_suspect
        self.suspect_reason = suspect_reason
    
    def is_quality_response(self) -> bool:
        """Проверяет, является ли ответ качественным"""
        return self.is_suspect is False