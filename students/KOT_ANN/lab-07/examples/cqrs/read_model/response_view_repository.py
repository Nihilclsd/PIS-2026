from abc import ABC, abstractmethod
from typing import Optional, List
from cqrs.read_model.response_view import ResponseView


class ResponseViewRepository(ABC):
    """Исходящий порт для Read Model"""
    
    @abstractmethod
    def save(self, view: ResponseView) -> None:
        """Сохраняет или обновляет Read Model"""
        pass
    
    @abstractmethod
    def find_by_id(self, response_id: str) -> Optional[ResponseView]:
        """Находит ответ по ID (денормализованный)"""
        pass
    
    @abstractmethod
    def find_by_form_id(
        self, 
        form_id: str, 
        limit: int = 100, 
        offset: int = 0,
        only_quality: bool = False
    ) -> List[ResponseView]:
        """Находит ответы по форме с пагинацией"""
        pass
    
    @abstractmethod
    def find_low_rating_responses(self, form_id: str, threshold: int = 3) -> List[ResponseView]:
        """Находит ответы с низкой оценкой (для уведомлений)"""
        pass
    
    @abstractmethod
    def get_statistics(self, form_id: str) -> dict:
        """Возвращает статистику по форме (агрегированная)"""
        pass