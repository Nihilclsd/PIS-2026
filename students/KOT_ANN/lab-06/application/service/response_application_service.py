import logging

from application.command.process_response_command import ProcessResponseCommand
from application.command.reclassify_response_command import ReclassifyResponseCommand
from application.command.handler.process_response_handler import ProcessResponseHandler
from application.command.handler.reclassify_response_handler import ReclassifyResponseHandler

from application.query.get_aggregates_query import GetAggregatesQuery
from application.query.get_response_by_id_query import GetResponseByIdQuery
from application.query.list_responses_by_form_query import ListResponsesByFormQuery
from application.query.handler.get_aggregates_handler import GetAggregatesHandler
from application.query.handler.get_response_by_id_handler import GetResponseByIdHandler
from application.query.handler.list_responses_by_form_handler import ListResponsesByFormHandler

from application.query.dto.response_dto import ResponseDto
from application.query.dto.form_aggregates_dto import FormAggregatesDto


logger = logging.getLogger(__name__)


class ResponseApplicationService:
    """Фасад Application слоя. Делегирует вызовы хендлерам."""
    
    def __init__(
        self,
        # Command handlers
        process_response_handler: ProcessResponseHandler,
        reclassify_response_handler: ReclassifyResponseHandler,
        # Query handlers
        get_aggregates_handler: GetAggregatesHandler,
        get_response_by_id_handler: GetResponseByIdHandler,
        list_responses_by_form_handler: ListResponsesByFormHandler
    ):
        self.process_response_handler = process_response_handler
        self.reclassify_response_handler = reclassify_response_handler
        self.get_aggregates_handler = get_aggregates_handler
        self.get_response_by_id_handler = get_response_by_id_handler
        self.list_responses_by_form_handler = list_responses_by_form_handler
    
    # ========== Команды ==========
    
    def process_response(self, command: ProcessResponseCommand) -> None:
        """Обработать ответ"""
        self.process_response_handler.handle(command)
    
    def reclassify_response(self, command: ReclassifyResponseCommand) -> None:
        """Переклассифицировать ответ"""
        self.reclassify_response_handler.handle(command)
    
    # ========== Запросы ==========
    
    def get_aggregates(self, query: GetAggregatesQuery) -> FormAggregatesDto:
        """Получить агрегаты формы"""
        return self.get_aggregates_handler.handle(query)
    
    def get_response_by_id(self, query: GetResponseByIdQuery) -> ResponseDto:
        """Получить ответ по ID"""
        return self.get_response_by_id_handler.handle(query)
    
    def list_responses_by_form(self, query: ListResponsesByFormQuery) -> list:
        """Получить список ответов формы"""
        return self.list_responses_by_form_handler.handle(query)