import logging

from domain.exceptions.domain_exception import DomainException

from application.command.reclassify_response_command import ReclassifyResponseCommand
from application.port.out.response_repository import ResponseRepository


logger = logging.getLogger(__name__)


class ReclassifyResponseHandler:
    """Обработчик команды ReclassifyResponseCommand"""
    
    def __init__(self, response_repository: ResponseRepository):
        self.response_repository = response_repository
    
    def handle(self, command: ReclassifyResponseCommand) -> None:
        """Переклассифицирует ответ"""
        logger.info(f"Reclassifying response {command.response_id}")
        
        # 1. Загрузка ответа
        response = self.response_repository.find_by_id(command.response_id)
        if not response:
            raise DomainException(
                f"Response {command.response_id} not found",
                code="RESPONSE_NOT_FOUND"
            )
        
        # 2. Сохранение старого статуса для обновления агрегатов
        old_is_suspect = response.is_suspect
        
        # 3. Переклассификация
        response.classify(
            quality_score=command.quality_score,
            is_suspect=command.is_suspect,
            suspect_reason=command.suspect_reason
        )
        
        # 4. Сохранение
        self.response_repository.save(response)
        
        # 5. Обновление агрегатов (если статус изменился)
        if old_is_suspect != command.is_suspect:
            # TODO: обновить агрегаты формы
            pass
        
        logger.info(f"Response {command.response_id} reclassified successfully")