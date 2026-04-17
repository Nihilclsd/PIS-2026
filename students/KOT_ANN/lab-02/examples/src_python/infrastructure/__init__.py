"""
Infrastructure Layer — адаптеры и конфигурация.

Содержит:
- Входящие адаптеры (QueueConsumer)
- Исходящие адаптеры (InMemory репозитории, Mock сервисы)
- DI контейнер (DependencyContainer)

Этот слой зависит от Application и Domain.
"""

from infrastructure.config.dependency_injection import DependencyContainer
from infrastructure.adapter.in.queue_consumer import QueueConsumer
from infrastructure.adapter.out.in_memory_form_repository import InMemoryFormRepository
from infrastructure.adapter.out.in_memory_response_repository import InMemoryResponseRepository
from infrastructure.adapter.out.mock_geo_service import MockGeoService
from infrastructure.adapter.out.mock_anti_spam_service import MockAntiSpamService
from infrastructure.adapter.out.mock_notification_service import MockNotificationService

__all__ = [
    "DependencyContainer",
    "QueueConsumer",
    "InMemoryFormRepository",
    "InMemoryResponseRepository",
    "MockGeoService",
    "MockAntiSpamService",
    "MockNotificationService",
]