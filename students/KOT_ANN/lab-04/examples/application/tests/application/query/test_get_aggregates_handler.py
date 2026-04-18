import pytest
from unittest.mock import Mock

from domain.models.aggregate import FormAggregates

from application.query.get_aggregates_query import GetAggregatesQuery
from application.query.handler.get_aggregates_handler import GetAggregatesHandler
from application.query.dto.form_aggregates_dto import FormAggregatesDto


class TestGetAggregatesHandler:
    """Тесты для GetAggregatesHandler"""
    
    def setup_method(self):
        self.mock_response_repository = Mock()
        self.handler = GetAggregatesHandler(
            response_repository=self.mock_response_repository
        )
        
        self.aggregates = FormAggregates(
            form_id="FORM-42",
            total_responses=100,
            quality_responses=80,
            suspect_responses=20,
            average_rating=4.2
        )
    
    def test_handle_returns_aggregates_dto(self):
        """Тест: возвращает DTO с агрегатами"""
        self.mock_response_repository.get_aggregates.return_value = self.aggregates
        
        query = GetAggregatesQuery(form_id="FORM-42")
        result = self.handler.handle(query)
        
        assert isinstance(result, FormAggregatesDto)
        assert result.form_id == "FORM-42"
        assert result.total_responses == 100
        assert result.quality_responses == 80
        assert result.suspect_responses == 20
        assert result.average_rating == 4.2
    
    def test_handle_returns_none_if_no_aggregates(self):
        """Тест: возвращает None, если агрегаты не найдены"""
        self.mock_response_repository.get_aggregates.return_value = None
        
        query = GetAggregatesQuery(form_id="FORM-UNKNOWN")
        result = self.handler.handle(query)
        
        assert result is None
    
    def test_handler_calls_repository_with_correct_form_id(self):
        """Тест: хендлер вызывает репозиторий с правильным form_id"""
        query = GetAggregatesQuery(form_id="FORM-42")
        self.handler.handle(query)
        
        self.mock_response_repository.get_aggregates.assert_called_once_with("FORM-42")