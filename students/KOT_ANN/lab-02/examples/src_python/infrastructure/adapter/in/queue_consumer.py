"""
Входящий адаптер: Consumer очереди сообщений.
Забирает сообщения из очереди и вызывает входящий порт.
"""

import json
import logging
from datetime import datetime

from application.port.in.process_response_use_case import ProcessResponseUseCase, ProcessResponseCommand


logger = logging.getLogger(__name__)


class QueueConsumer:
    """
    Адаптер для RabbitMQ/Kafka.
    
    Забирает сообщения из очереди и преобразует их в вызов
    входящего порта ProcessResponseUseCase.
    """
    
    def __init__(self, processor: ProcessResponseUseCase):
        self.processor = processor
    
    def on_message(self, raw_message: str) -> None:
        """
        Обработчик сообщения из очереди.
        
        TODO: Полная реализация в Lab #5 (подключение к RabbitMQ)
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
        # self.processor.process(command)
        
        raise NotImplementedError("Будет реализовано в Lab #5")
    