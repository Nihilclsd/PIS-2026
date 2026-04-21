import logging

from application.query.list_responses_by_form_query import ListResponsesByFormQuery
from application.query.dto.response_dto import ResponseDto
from application.port.out.response_repository import ResponseRepository


logger = logging.getLogger(__name__)


class ListResponsesByFormHandler:
    """Обработчик запроса ListResponsesByFormQuery"""
    
    def __init__(self, response_repository: ResponseRepository):
        self.response_repository = response_repository
    
    def handle(self, query: ListResponsesByFormQuery) -> list:
        """Возвращает список ответов формы"""
        logger.info(f"Listing responses for form {query.form_id}")
        
        responses = self.response_repository.find_by_form_id(
            form_id=query.form_id,
            limit=query.limit,
            offset=query.offset,
            include_suspect=query.include_suspect
        )
        
        return [ResponseDto.from_domain(r) for r in responses]