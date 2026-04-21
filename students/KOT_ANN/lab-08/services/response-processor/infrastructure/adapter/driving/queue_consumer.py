import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from application.command.process_response_command import ProcessResponseCommand
from application.service.response_application_service import ResponseApplicationService


logger = logging.getLogger(__name__)


class QueueConsumer:
    """Входящий адаптер: Consumer очереди сообщений"""

    def __init__(self, service: ResponseApplicationService):
        self.service = service

    def on_message(self, raw_message: str) -> None:
        """
        Обрабатывает сообщение из очереди.
        
        TODO: Полная реализация в Lab #5 (подключение к RabbitMQ/Kafka)
        """
        logger.info("Received message from queue")

        # Парсинг сообщения
        # data = json.loads(raw_message)

        # Создание команды
        # command = ProcessResponseCommand(
        #     response_id=data['response_id'],
        #     form_id=data['form_id'],
        #     answers=data['answers'],
        #     ip_address=data.get('ip_address'),
        #     user_agent=data.get('user_agent'),
        #     started_at=datetime.fromisoformat(data['started_at']),
        #     submitted_at=datetime.fromisoformat(data['submitted_at'])
        # )

        # Вызов use-case
        # self.service.process_response(command)

        raise NotImplementedError("Будет реализовано в Lab #5")