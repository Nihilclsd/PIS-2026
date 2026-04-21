import json
import logging
from datetime import datetime
from typing import Optional
import pika

from event_bus.rabbitmq_config import RabbitMQConfig

logger = logging.getLogger(__name__)


class EventPublisher:
    """Публикатор событий в RabbitMQ"""
    
    def __init__(self, rabbitmq_config: RabbitMQConfig):
        self.config = rabbitmq_config
    
    def publish_response_classified(
        self,
        response_id: str,
        form_id: str,
        form_owner_email: str,
        is_suspect: bool,
        quality_score: float,
        rating: Optional[int] = None,
        comment: Optional[str] = None
    ) -> bool:
        """Публикует событие о классификации ответа"""
        try:
            message = {
                "event_type": "ResponseClassified",
                "response_id": response_id,
                "form_id": form_id,
                "form_owner_email": form_owner_email,
                "is_suspect": is_suspect,
                "quality_score": quality_score,
                "rating": rating,
                "comment": comment,
                "timestamp": datetime.now().isoformat()
            }
            
            self.config.get_channel().basic_publish(
                exchange=self.config.EXCHANGE,
                routing_key=self.config.ROUTING_KEY,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # persistent
                    content_type='application/json'
                )
            )
            logger.info(f"Published ResponseClassified event for {response_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False