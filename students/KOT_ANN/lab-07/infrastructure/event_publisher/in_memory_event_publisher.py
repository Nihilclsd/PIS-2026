import logging
from typing import List, Callable
from dataclasses import dataclass
from domain.events.response_events import ResponseClassifiedEvent, ResponseEnrichedEvent

logger = logging.getLogger(__name__)


class InMemoryEventPublisher:
    """In-memory реализация публикации событий"""

    def __init__(self):
        self._handlers: List[Callable] = []

    def subscribe(self, handler: Callable) -> None:
        """Подписывает обработчик на события"""
        self._handlers.append(handler)
        logger.info(f"Subscribed handler {handler.__name__}")

    def publish_classified(self, event: ResponseClassifiedEvent) -> None:
        """Публикует событие классификации"""
        logger.info(f"Publishing ResponseClassifiedEvent: {event.response_id}")
        for handler in self._handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Handler failed: {e}")

    def publish_enriched(self, event: ResponseEnrichedEvent) -> None:
        """Публикует событие обогащения"""
        logger.info(f"Publishing ResponseEnrichedEvent: {event.response_id}")
        for handler in self._handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Handler failed: {e}")