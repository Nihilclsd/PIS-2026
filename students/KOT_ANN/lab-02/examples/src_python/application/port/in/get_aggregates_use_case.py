"""
Входящий порт: получение агрегатов формы.
"""

from abc import ABC, abstractmethod
from typing import Optional


class GetAggregatesUseCase(ABC):
    """Входящий порт: получение статистики по форме"""
    
    @abstractmethod
    def get_aggregates(self, form_id: str):
        """
        Возвращает агрегированные метрики формы.
        
        Args:
            form_id: Идентификатор формы
            
        Returns:
            FormAggregates или None, если форма не найдена
        """
        pass