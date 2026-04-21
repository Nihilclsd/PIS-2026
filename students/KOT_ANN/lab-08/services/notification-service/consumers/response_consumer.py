import json
import logging
import pika
import os

from services.email_service import EmailService
from services.push_service import PushService

logger = logging.getLogger(__name__)


class ResponseConsumer:
    """Consumer для обработки событий из RabbitMQ"""
    
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    EXCHANGE = "response.events"
    QUEUE = "notification.queue"
    ROUTING_KEY = "response.classified"
    
    def __init__(self, email_service: EmailService, push_service: PushService):
        self.email_service = email_service
        self.push_service = push_service
        self._connection = None
        self._channel = None
    
    def connect(self):
        """Устанавливает соединение с RabbitMQ"""
        self._connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.RABBITMQ_HOST)
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
    
    def start_consuming(self):
        """Запускает прослушивание очереди"""
        self.connect()
        
        self._channel.basic_consume(
            queue=self.QUEUE,
            on_message_callback=self.callback,
            auto_ack=True
        )
        
        logger.info("Started consuming messages from RabbitMQ")
        self._channel.start_consuming()
    
    def callback(self, ch, method, properties, body):
        """Обработчик сообщений"""
        try:
            message = json.loads(body)
            event_type = message.get("event_type")
            
            if event_type == "ResponseClassified":
                self._handle_response_classified(message)
                
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
    
    def _handle_response_classified(self, message: dict):
        """Обрабатывает событие ResponseClassified"""
        response_id = message.get("response_id")
        form_id = message.get("form_id")
        form_owner_email = message.get("form_owner_email")
        is_suspect = message.get("is_suspect")
        rating = message.get("rating")
        comment = message.get("comment")
        
        logger.info(f"Processing ResponseClassified for {response_id}")
        
        if not is_suspect and rating and rating <= 2:
            subject = f"Низкая оценка формы {form_id}"
            body = f"Ответ {response_id} получил оценку {rating}/5.\nКомментарий: {comment or 'Нет комментария'}"
            
            self.email_service.send(form_owner_email, subject, body)
            logger.info(f"Sent notification to {form_owner_email}")