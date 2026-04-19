"""
Value Object: Агрегированные метрики формы.
"""


from typing import Optional
from dataclasses import dataclass, field

from domain.exceptions.domain_exception import DomainException


@dataclass
class FormAggregates:
    """Value Object: Агрегированные метрики формы"""
    
    form_id: str
    total_responses: int = 0
    quality_responses: int = 0
    suspect_responses: int = 0
    average_rating: float = 0.0
    _rating_sum: float = field(default=0.0, repr=False)
    
    def increment_total(self) -> None:
        """Увеличивает счётчик всех ответов"""
        self.total_responses += 1
    
    def increment_quality(self) -> None:
        """Увеличивает счётчик качественных ответов"""
        self.quality_responses += 1
    
    def increment_suspect(self) -> None:
        """Увеличивает счётчик подозрительных ответов"""
        self.suspect_responses += 1
    
    def add_rating(self, rating: float) -> None:
        """Добавляет новую оценку и пересчитывает среднее"""
        # Инвариант: рейтинг должен быть в диапазоне 1-5
        if rating < 1 or rating > 5:
            raise DomainException(
                f"Rating must be between 1 and 5, got {rating}",
                code="INVALID_RATING"
            )
        
        # Инвариант: нельзя добавить рейтинг, если нет ответов
        if self.total_responses == 0:
            raise DomainException(
                "Cannot add rating when total_responses is 0",
                code="NO_RESPONSES"
            )
        
        self._rating_sum += rating
        self.average_rating = self._rating_sum / self.total_responses
    
    def update_average_rating(self, new_rating: float) -> None:
        """Обновляет средний рейтинг (альтернативный метод)"""
        # Инвариант: рейтинг должен быть в диапазоне 1-5
        if new_rating < 1 or new_rating > 5:
            raise DomainException(
                f"Rating must be between 1 and 5, got {new_rating}",
                code="INVALID_RATING"
            )
        
        # Инвариант: нельзя обновить рейтинг, если нет ответов
        if self.total_responses == 0:
            raise DomainException(
                "Cannot update average rating when total_responses is 0",
                code="NO_RESPONSES"
            )
        
        # Пересчёт суммы из среднего (приближённый)
        self._rating_sum = self.average_rating * (self.total_responses - 1) + new_rating
        self.average_rating = self._rating_sum / self.total_responses
    
    @property
    def quality_rate(self) -> float:
        """Доля качественных ответов в процентах"""
        if self.total_responses == 0:
            return 0.0
        return (self.quality_responses / self.total_responses) * 100
    
    @property
    def suspect_rate(self) -> float:
        """Доля подозрительных ответов в процентах"""
        if self.total_responses == 0:
            return 0.0
        return (self.suspect_responses / self.total_responses) * 100
    
    def to_dict(self) -> dict:
        """Преобразует агрегаты в словарь для сериализации"""
        return {
            "form_id": self.form_id,
            "total_responses": self.total_responses,
            "quality_responses": self.quality_responses,
            "suspect_responses": self.suspect_responses,
            "average_rating": self.average_rating,
            "quality_rate": self.quality_rate,
            "suspect_rate": self.suspect_rate,
        }
    
    def __add__(self, other: "FormAggregates") -> "FormAggregates":
        """Объединение двух агрегатов (для композитных отчётов)"""
        if self.form_id != other.form_id:
            raise DomainException(
                f"Cannot merge aggregates for different forms: {self.form_id} vs {other.form_id}",
                code="FORM_ID_MISMATCH"
            )
        
        total = self.total_responses + other.total_responses
        quality = self.quality_responses + other.quality_responses
        suspect = self.suspect_responses + other.suspect_responses
        rating_sum = self._rating_sum + other._rating_sum
        
        result = FormAggregates(
            form_id=self.form_id,
            total_responses=total,
            quality_responses=quality,
            suspect_responses=suspect,
            average_rating=rating_sum / total if total > 0 else 0.0,
            _rating_sum=rating_sum
        )
        return result