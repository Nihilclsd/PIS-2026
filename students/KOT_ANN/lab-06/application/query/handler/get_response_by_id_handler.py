import logging

from application.query.get_response_by_id_query import GetResponseByIdQuery
from application.query.dto.response_dto import ResponseDto
from application.port.out.response_repository import ResponseRepository


logger = logging.getLogger(__name__)


class GetResponseByIdHandler:
    """Обработчик запроса GetResponseByIdQuery"""
    
    def __init__(self, response_repository: ResponseRepository):
        self.response_repository = response_repository
    
    def handle(self, query: GetResponseByIdQuery) -> ResponseDto:
        """Возвращает ответ по ID"""
        logger.info(f"Getting response {query.response_id}")
        
        response = self.response_repository.find_by_id(query.response_id)
        if not response:
            return None
        
        return ResponseDto.from_domain(response)