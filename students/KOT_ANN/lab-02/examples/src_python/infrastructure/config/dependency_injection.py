"""
Dependency Injection контейнер.
Связывает порты (интерфейсы) с адаптерами (реализациями).
"""

from application.service.response_processor import ResponseProcessor
from application.port.in.process_response_use_case import ProcessResponseUseCase
from application.port.in.get_aggregates_use_case import GetAggregatesUseCase
from application.port.out.form_schema_repository import FormSchemaRepository
from application.port.out.response_repository import ResponseRepository
from application.port.out.geo_service import GeoService
from application.port.out.anti_spam_service import AntiSpamService
from application.port.out.notification_service import NotificationService

from infrastructure.adapter.out.in_memory_form_repository import InMemoryFormRepository
from infrastructure.adapter.out.in_memory_response_repository import InMemoryResponseRepository
from infrastructure.adapter.out.mock_geo_service import MockGeoService
from infrastructure.adapter.out.mock_anti_spam_service import MockAntiSpamService
from infrastructure.adapter.out.mock_notification_service import MockNotificationService


class DependencyContainer:
    """
    Контейнер зависимостей.
    
    Создаёт и связывает все компоненты системы.
    Следует принципу Dependency Inversion: Application слой не создаёт
    зависимости сам, а получает их извне.
    """
    
    def __init__(self):
        # 1. Создаём исходящие адаптеры (инфраструктура)
        self.form_repository: FormSchemaRepository = InMemoryFormRepository()
        self.response_repository: ResponseRepository = InMemoryResponseRepository()
        self.geo_service: GeoService = MockGeoService()
        self.anti_spam_service: AntiSpamService = MockAntiSpamService()
        self.notification_service: NotificationService = MockNotificationService()
        
        # 2. Создаём Application сервис, внедряя зависимости
        self._response_processor = ResponseProcessor(
            form_repository=self.form_repository,
            response_repository=self.response_repository,
            geo_service=self.geo_service,
            anti_spam_service=self.anti_spam_service,
            notification_service=self.notification_service
        )
    
    def get_process_response_use_case(self) -> ProcessResponseUseCase:
        """Возвращает реализацию входящего порта ProcessResponseUseCase"""
        return self._response_processor
    
    def get_get_aggregates_use_case(self) -> GetAggregatesUseCase:
        """Возвращает реализацию входящего порта GetAggregatesUseCase"""
        return self._response_processor
    
    def get_queue_consumer(self):
        """Возвращает Consumer для очереди"""
        from infrastructure.adapter.in.queue_consumer import QueueConsumer
        return QueueConsumer(self.get_process_response_use_case())