import pytest
from unittest.mock import Mock
from datetime import datetime

from application.service.response_application_service import ResponseApplicationService
from application.command.process_response_command import ProcessResponseCommand
from application.command.reclassify_response_command import ReclassifyResponseCommand
from application.query.get_aggregates_query import GetAggregatesQuery
from application.query.get_response_by_id_query import GetResponseByIdQuery
from application.query.list_responses_by_form_query import ListResponsesByFormQuery
from application.query.dto.response_dto import ResponseDto
from application.query.dto.form_aggregates_dto import FormAggregatesDto


class TestResponseApplicationService:
    """Тесты для ResponseApplicationService (фасада)"""
    
    def setup_method(self):
        self.mock_process_handler = Mock()
        self.mock_reclassify_handler = Mock()
        self.mock_get_aggregates_handler = Mock()
        self.mock_get_response_handler = Mock()
        self.mock_list_responses_handler = Mock()
        
        self.service = ResponseApplicationService(
            process_response_handler=self.mock_process_handler,
            reclassify_response_handler=self.mock_reclassify_handler,
            get_aggregates_handler=self.mock_get_aggregates_handler,
            get_response_by_id_handler=self.mock_get_response_handler,
            list_responses_by_form_handler=self.mock_list_responses_handler
        )
    
    def test_process_response_delegates_to_handler(self):
        """Тест: process_response() делегирует хендлеру"""
        command = ProcessResponseCommand(
            response_id="RESP-123",
            form_id="FORM-42",
            answers={"name": "Иван"},
            ip_address=None,
            user_agent=None,
            started_at=datetime(2024, 1, 1, 10, 0, 0),
            submitted_at=datetime(2024, 1, 1, 10, 2, 30)
        )
        
        self.service.process_response(command)
        
        self.mock_process_handler.handle.assert_called_once_with(command)
    
    def test_reclassify_response_delegates_to_handler(self):
        """Тест: reclassify_response() делегирует хендлеру"""
        command = ReclassifyResponseCommand(
            response_id="RESP-123",
            quality_score=0.95,
            is_suspect=False
        )
        
        self.service.reclassify_response(command)
        
        self.mock_reclassify_handler.handle.assert_called_once_with(command)
    
    def test_get_aggregates_delegates_to_handler(self):
        """Тест: get_aggregates() делегирует хендлеру"""
        query = GetAggregatesQuery(form_id="FORM-42")
        expected_result = FormAggregatesDto(
            form_id="FORM-42",
            total_responses=100,
            quality_responses=80,
            suspect_responses=20,
            average_rating=4.2,
            quality_rate=80.0,
            suspect_rate=20.0
        )
        self.mock_get_aggregates_handler.handle.return_value = expected_result
        
        result = self.service.get_aggregates(query)
        
        self.mock_get_aggregates_handler.handle.assert_called_once_with(query)
        assert result == expected_result
    
    def test_get_response_by_id_delegates_to_handler(self):
        """Тест: get_response_by_id() делегирует хендлеру"""
        query = GetResponseByIdQuery(response_id="RESP-123")
        expected_result = ResponseDto(
            response_id="RESP-123",
            form_id="FORM-42",
            answers={},
            started_at=datetime(2024, 1, 1, 10, 0, 0),
            submitted_at=datetime(2024, 1, 1, 10, 2, 30),
            ip_address=None,
            user_agent=None,
            geo_country=None,
            geo_city=None,
            device_type=None,
            filling_time_sec=None,
            quality_score=None,
            is_suspect=None,
            suspect_reason=None
        )
        self.mock_get_response_handler.handle.return_value = expected_result
        
        result = self.service.get_response_by_id(query)
        
        self.mock_get_response_handler.handle.assert_called_once_with(query)
        assert result == expected_result
    
    def test_list_responses_by_form_delegates_to_handler(self):
        """Тест: list_responses_by_form() делегирует хендлеру"""
        query = ListResponsesByFormQuery(form_id="FORM-42")
        expected_result = []
        self.mock_list_responses_handler.handle.return_value = expected_result
        
        result = self.service.list_responses_by_form(query)
        
        self.mock_list_responses_handler.handle.assert_called_once_with(query)
        assert result == expected_result