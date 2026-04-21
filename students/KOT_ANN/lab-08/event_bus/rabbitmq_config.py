import pika
import json
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


class RabbitMQConfig:
    """Конфигурация RabbitMQ"""
    
    EXCHANGE = "response.events"
    QUEUE = "notification.queue"
    ROUTING_KEY = "response.classified"
    
    def __init__(self, host: str = "localhost"):
        self.host = host
        self._connection = None
        self._channel = None
    
    def connect(self):
        """Устанавливает соединение с RabbitMQ"""
        self._connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host)
        )
        self._channel = self._connection.channel()
        self._channel.exchange_declare(
            exchange=self.EXCHANGE,
            exchange_type='topic',
            durable=True
        )
        self._channel.queue_declare(queue=self.QUEUE, durable=True)
        self._channel.queue_bind(
            exchange=self.EXCHANGE,
            queue=self.QUEUE,
            routing_key=self.ROUTING_KEY
        )
        logger.info("Connected to RabbitMQ")
    
    def close(self):
        """Закрывает соединение"""
        if self._connection and self._connection.is_open:
            self._connection.close()
            logger.info("Closed RabbitMQ connection")
    
    def get_channel(self):
        return self._channel