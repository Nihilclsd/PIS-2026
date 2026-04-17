from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class ProcessResponseCommand:
    """DTO для команды обработки ответа"""
    
    def __init__(
        self,
        response_id: str,
        form_id: str,
        answers: Dict[str, Any],
        ip_address: Optional[str],
        user_agent: Optional[str],
        started_at: datetime,
        submitted_at: datetime
    ):
        self.response_id = response_id
        self.form_id = form_id
        self.answers = answers
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.started_at = started_at
        self.submitted_at = submitted_at


class ProcessResponseUseCase(ABC):
    """Входящий порт: обработка ответа"""
    
    @abstractmethod
    def process(self, command: ProcessResponseCommand) -> None:
        """Обрабатывает ответ"""
        pass