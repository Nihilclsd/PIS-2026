import logging

from application.query.get_aggregates_query import GetAggregatesQuery
from application.query.dto.form_aggregates_dto import FormAggregatesDto
from application.port.out.response_repository import ResponseRepository


logger = logging.getLogger(__name__)


class GetAggregatesHandler:
    """Обработчик запроса GetAggregatesQuery"""
    
    def __init__(self, response_repository: ResponseRepository):
        self.response_repository = response_repository
    
    def handle(self, query: GetAggregatesQuery) -> FormAggregatesDto:
        """Возвращает агрегаты формы"""
        logger.info(f"Getting aggregates for form {query.form_id}")
        
        aggregates = self.response_repository.get_aggregates(query.form_id)
        
        return FormAggregatesDto.from_domain(aggregates)