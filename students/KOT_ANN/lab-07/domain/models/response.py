"""
Доменная сущность: Ответ респондента.
Содержит бизнес-логику, связанную с ответом.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field

from domain.exceptions.domain_exception import DomainException


@dataclass
class Response:
    """Доменная модель ответа на форму"""
    
    response_id: str
    form_id: str
    answers: Dict[str, Any]
    started_at: datetime
    submitted_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Обогащённые данные
    geo_country: Optional[str] = None
    geo_city: Optional[str] = None
    device_type: Optional[str] = None
    device_os: Optional[str] = None
    device_browser: Optional[str] = None
    filling_time_sec: Optional[int] = None
    
    # Результат классификации
    quality_score: Optional[float] = None
    is_suspect: Optional[bool] = None
    suspect_reason: Optional[str] = None
    
    # Флаг: был ли ответ уже обработан
    _is_classified: bool = field(default=False, init=False, repr=False)
    
    def calculate_filling_time(self) -> int:
        """Вычисляет время заполнения формы в секундах"""
        delta = self.submitted_at - self.started_at
        seconds = int(delta.total_seconds())
        # Инвариант: время не может быть отрицательным
        if seconds < 0:
            raise DomainException(
                f"Filling time cannot be negative: {seconds}",
                code="NEGATIVE_FILLING_TIME"
            )
        self.filling_time_sec = seconds
        return seconds
    
    def enrich_geo(self, country: str, city: str) -> None:
        """Обогащает ответ гео-данными"""
        self.geo_country = country
        self.geo_city = city
    
    def enrich_device(self, device_type: str, os: str = None, browser: str = None) -> None:
        """Обогащает ответ данными об устройстве"""
        self.device_type = device_type
        self.device_os = os
        self.device_browser = browser
    
    def classify(
        self, 
        quality_score: float, 
        is_suspect: bool, 
        suspect_reason: Optional[str] = None
    ) -> None:
        """Классифицирует ответ (качественный / отписка)"""
        
        # Инвариант 1: ответ не может быть классифицирован дважды
        if self._is_classified:
            raise DomainException(
                f"Response {self.response_id} already classified",
                code="ALREADY_CLASSIFIED"
            )
        
        # Инвариант 2: quality_score должен быть в диапазоне 0-1
        if not 0 <= quality_score <= 1:
            raise DomainException(
                f"Quality score must be between 0 and 1, got {quality_score}",
                code="INVALID_QUALITY_SCORE"
            )
        
        # Инвариант 3: для отписки должна быть указана причина
        if is_suspect and not suspect_reason:
            raise DomainException(
                "Suspect reason is required when is_suspect=True",
                code="MISSING_SUSPECT_REASON"
            )
        
        self.quality_score = quality_score
        self.is_suspect = is_suspect
        self.suspect_reason = suspect_reason
        self._is_classified = True
    
    def is_quality_response(self) -> bool:
        """Проверяет, является ли ответ качественным"""
        if not self._is_classified:
            raise DomainException(
                f"Response {self.response_id} not classified yet",
                code="NOT_CLASSIFIED"
            )
        return self.is_suspect is False
    
    def is_suspect_response(self) -> bool:
        """Проверяет, является ли ответ подозрительным (отпиской)"""
        if not self._is_classified:
            raise DomainException(
                f"Response {self.response_id} not classified yet",
                code="NOT_CLASSIFIED"
            )
        return self.is_suspect is True
    
    def is_processed(self) -> bool:
        """Проверяет, прошёл ли ответ полную обработку"""
        return (
            self.filling_time_sec is not None
            and self.quality_score is not None
            and self.is_suspect is not None
        )
    
    def to_dict(self) -> dict:
        """Преобразует ответ в словарь для сериализации"""
        return {
            "response_id": self.response_id,
            "form_id": self.form_id,
            "answers": self.answers,
            "started_at": self.started_at.isoformat(),
            "submitted_at": self.submitted_at.isoformat(),
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "geo_country": self.geo_country,
            "geo_city": self.geo_city,
            "device_type": self.device_type,
            "device_os": self.device_os,
            "device_browser": self.device_browser,
            "filling_time_sec": self.filling_time_sec,
            "quality_score": self.quality_score,
            "is_suspect": self.is_suspect,
            "suspect_reason": self.suspect_reason,
        }