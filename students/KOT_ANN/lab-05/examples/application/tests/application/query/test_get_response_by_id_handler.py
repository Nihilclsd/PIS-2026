import pytest
from unittest.mock import Mock
from datetime import datetime

from domain.models.response import Response

from application.query.get_response_by_id_query import GetResponseByIdQuery
from application.query.handler.get_response_by_id_handler import GetResponseByIdHandler
from application.query.dto.response_dto import ResponseDto


class TestGetResponseByIdHandler:
    """Тесты для GetResponseByIdHandler"""
    
    def setup_method(self):
        self.mock_response_repository = Mock()
        self.handler = GetResponseByIdHandler(
            response_repository=self.mock_response_repository
        )
        
        self.response = Response(
            response_id="RESP-123",
            form_id="FORM-42",
            answers={"name": "Иван", "rating": 5},
            started_at=datetime(2024, 1, 1, 10, 0, 0),
            submitted_at=datetime(2024, 1, 1, 10, 2, 30),
            ip_address="77.88.55.66",
            user_agent="Mozilla/5.0"
        )
        self.response.classify(quality_score=0.95, is_suspect=False)
    
    def test_handle_returns_response_dto(self):
        """Тест: возвращает DTO с ответом"""
        self.mock_response_repository.find_by_id.return_value = self.response
        
        query = GetResponseByIdQuery(response_id="RESP-123")
        result = self.handler.handle(query)
        
        assert isinstance(result, ResponseDto)
        assert result.response_id == "RESP-123"
        assert result.form_id == "FORM-42"
        assert result.answers == {"name": "Иван", "rating": 5}
        assert result.is_suspect is False
    
    def test_handle_returns_none_if_response_not_found(self):
        """Тест: возвращает None, если ответ не найден"""
        self.mock_response_repository.find_by_id.return_value = None
        
        query = GetResponseByIdQuery(response_id="RESP-NOT-FOUND")
        result = self.handler.handle(query)
        
        assert result is None
    
    def test_handler_calls_repository_with_correct_response_id(self):
        """Тест: хендлер вызывает репозиторий с правильным response_id"""
        query = GetResponseByIdQuery(response_id="RESP-123")
        self.handler.handle(query)
        
        self.mock_response_repository.find_by_id.assert_called_once_with("RESP-123")