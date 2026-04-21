import logging
from datetime import datetime
from typing import Optional

from domain.models.response import Response
from domain.models.form import Form
from domain.exceptions.domain_exception import DomainException

from application.command.process_response_command import ProcessResponseCommand
from application.port.out.form_schema_repository import FormSchemaRepository
from application.port.out.response_repository import ResponseRepository
from application.port.out.geo_service import GeoService
from application.port.out.anti_spam_service import AntiSpamService, AntiSpamResult
from application.port.out.notification_service import NotificationService


logger = logging.getLogger(__name__)


class ProcessResponseHandler:
    """Обработчик команды ProcessResponseCommand"""
    
    def __init__(
        self,
        form_repository: FormSchemaRepository,
        response_repository: ResponseRepository,
        geo_service: GeoService,
        anti_spam_service: AntiSpamService,
        notification_service: NotificationService
    ):
        self.form_repository = form_repository
        self.response_repository = response_repository
        self.geo_service = geo_service
        self.anti_spam_service = anti_spam_service
        self.notification_service = notification_service
    
    def handle(self, command: ProcessResponseCommand) -> None:
        """Обрабатывает ответ"""
        logger.info(f"Processing response {command.response_id}")
        
        # 1. Получение схемы формы
        form = self.form_repository.find_by_id(command.form_id)
        if not form:
            raise DomainException(
                f"Form {command.form_id} not found",
                code="FORM_NOT_FOUND"
            )
        
        # 2. Создание доменной сущности Response
        response = Response(
            response_id=command.response_id,
            form_id=command.form_id,
            answers=command.answers,
            started_at=command.started_at,
            submitted_at=command.submitted_at,
            ip_address=command.ip_address,
            user_agent=command.user_agent
        )
        
        # 3. Валидация ответа по схеме формы
        form.validate_answers(command.answers)
        
        # 4. Расчёт времени заполнения
        filling_time = response.calculate_filling_time()
        
        # 5. Обогащение гео-данными
        if command.ip_address:
            country, city = self.geo_service.get_location(command.ip_address)
            response.enrich_geo(country, city)
        
        # 6. Парсинг User-Agent (упрощённо)
        device_type = self._parse_user_agent(command.user_agent)
        response.enrich_device(device_type)
        
        # 7. Антиспам-анализ
        anti_spam_result = self.anti_spam_service.analyze(
            answers=command.answers,
            filling_time_sec=filling_time,
            form_settings=form.anti_spam_settings
        )
        
        response.classify(
            quality_score=anti_spam_result.quality_score,
            is_suspect=anti_spam_result.is_suspect,
            suspect_reason=anti_spam_result.suspect_reason
        )
        
        # 8. Сохранение ответа
        self.response_repository.save(response)
        self.response_repository.update_aggregates(command.form_id, response)
        
        # 9. Проверка триггера уведомлений
        if response.is_suspect is False:
            rating_field = form.get_rating_field()
            if rating_field and rating_field in command.answers:
                rating = command.answers[rating_field]
                if rating <= 2:
                    comment = command.answers.get("comment", "")
                    self.notification_service.notify_critical_feedback(
                        form_id=command.form_id,
                        response_id=command.response_id,
                        rating=rating,
                        comment=comment
                    )
        
        logger.info(f"Response {command.response_id} processed successfully")
    
    def _parse_user_agent(self, user_agent: Optional[str]) -> str:
        """Упрощённый парсинг User-Agent"""
        if not user_agent:
            return "UNKNOWN"
        user_agent_lower = user_agent.lower()
        if "mobile" in user_agent_lower or "iphone" in user_agent_lower:
            return "MOBILE"
        if "tablet" in user_agent_lower or "ipad" in user_agent_lower:
            return "TABLET"
        return "DESKTOP"