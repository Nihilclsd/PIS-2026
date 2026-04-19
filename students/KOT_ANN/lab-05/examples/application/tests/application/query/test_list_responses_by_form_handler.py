import pytest
from unittest.mock import Mock
from datetime import datetime

from domain.models.response import Response

from application.query.list_responses_by_form_query import ListResponsesByFormQuery
from application.query.handler.list_responses_by_form_handler import ListResponsesByFormHandler
from application.query.dto.response_dto import ResponseDto


class TestListResponsesByFormHandler:
    """Тесты для ListResponsesByFormHandler"""
    
    def setup_method(self):
        self.mock_response_repository = Mock()
        self.handler = ListResponsesByFormHandler(
            response_repository=self.mock_response_repository
        )
        
        self.responses = []
        for i in range(3):
            response = Response(
                response_id=f"RESP-{i}",
                form_id="FORM-42",
                answers={"name": f"User{i}", "rating": 5},
                started_at=datetime(2024, 1, 1, 10, 0, 0),
                submitted_at=datetime(2024, 1, 1, 10, 2, 30)
            )
            response.classify(quality_score=0.95, is_suspect=False)
            self.responses.append(response)
        
        self.mock_response_repository.find_by_form_id.return_value = self.responses
    
    def test_handle_returns_list_of_response_dtos(self):
        """Тест: возвращает список DTO с ответами"""
        query = ListResponsesByFormQuery(form_id="FORM-42")
        result = self.handler.handle(query)
        
        assert len(result) == 3
        assert all(isinstance(r, ResponseDto) for r in result)
        assert result[0].response_id == "RESP-0"
        assert result[1].response_id == "RESP-1"
        assert result[2].response_id == "RESP-2"
    
    def test_handle_with_limit_and_offset(self):
        """Тест: запрос с limit и offset"""
        query = ListResponsesByFormQuery(
            form_id="FORM-42",
            limit=10,
            offset=5,
            include_suspect=False
        )
        
        self.handler.handle(query)
        
        self.mock_response_repository.find_by_form_id.assert_called_once_with(
            form_id="FORM-42",
            limit=10,
            offset=5,
            include_suspect=False
        )
    
    def test_handle_returns_empty_list_if_no_responses(self):
        """Тест: возвращает пустой список, если ответов нет"""
        self.mock_response_repository.find_by_form_id.return_value = []
        
        query = ListResponsesByFormQuery(form_id="FORM-42")
        result = self.handler.handle(query)
        
        assert result == []