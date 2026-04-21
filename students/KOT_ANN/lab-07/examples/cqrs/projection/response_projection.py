import logging
from typing import Optional

from domain.events.response_events import ResponseClassifiedEvent, ResponseEnrichedEvent
from cqrs.read_model.response_view import ResponseView
from cqrs.read_model.response_view_repository import ResponseViewRepository
from application.port.out.form_schema_repository import FormSchemaRepository


logger = logging.getLogger(__name__)


class ResponseProjection:
    """
    Проекция: обновляет Read Model на основе доменных событий.
    Реализует Event-Driven синхронизацию между Write и Read моделями.
    """
    
    def __init__(
        self,
        view_repository: ResponseViewRepository,
        form_repository: FormSchemaRepository
    ):
        self.view_repository = view_repository
        self.form_repository = form_repository
    
    def on_response_classified(self, event: ResponseClassifiedEvent) -> None:
        """
        Обработчик события ResponseClassifiedEvent.
        Обновляет Read Model при классификации ответа.
        """
        logger.info(f"Projection: updating view for response {event.response_id}")
        
        # Загружаем существующий view или создаём новый
        existing = self.view_repository.find_by_id(event.response_id)
        
        if existing:
            # Обновляем существующий
            existing.is_suspect = event.is_suspect
            existing.quality_score = event.quality_score
            existing.updated_at = event.occurred_at
            self.view_repository.save(existing)
        else:
            # Создаём новый (это может быть partial, если событие пришло раньше других)
            logger.warning(f"ResponseView for {event.response_id} not found, creating partial")
            # В реальном приложении нужно запросить полный ответ из Write Model
    
    def on_response_enriched(self, event: ResponseEnrichedEvent) -> None:
        """
        Обработчик события ResponseEnrichedEvent.
        Обновляет Read Model при обогащении ответа.
        """
        logger.info(f"Projection: enriching view for response {event.response_id}")
        
        existing = self.view_repository.find_by_id(event.response_id)
        
        if existing:
            existing.country = event.geo_country
            existing.city = event.geo_city
            existing.device_type = event.device_type
            existing.updated_at = event.occurred_at
            self.view_repository.save(existing)
        else:
            logger.warning(f"ResponseView for {event.response_id} not found, cannot enrich")
    
    def rebuild_from_scratch(self, response) -> None:
        """
        Перестраивает Read Model из Write Model (для восстановления).
        """
        form = self.form_repository.find_by_id(response.form_id)
        form_title = form.title if form and hasattr(form, 'title') else None
        
        view = ResponseView.from_domain(response, form_title)
        self.view_repository.save(view)
        logger.info(f"ResponseView rebuilt for {response.response_id}")