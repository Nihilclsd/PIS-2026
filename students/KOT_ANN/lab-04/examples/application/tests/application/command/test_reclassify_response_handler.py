import pytest
from unittest.mock import Mock
from datetime import datetime

from domain.models.response import Response
from domain.exceptions.domain_exception import DomainException

from application.command.reclassify_response_command import ReclassifyResponseCommand
from application.command.handler.reclassify_response_handler import ReclassifyResponseHandler


class TestReclassifyResponseHandler:
    """Тесты для ReclassifyResponseHandler"""
    
    def setup_method(self):
        self.mock_response_repository = Mock()
        self.handler = ReclassifyResponseHandler(
            response_repository=self.mock_response_repository
        )
        
        # Создаём тестовый ответ (НЕ классифицируем его в конструкторе!)
        self.response = Response(
            response_id="RESP-123",
            form_id="FORM-42",
            answers={"name": "Иван", "rating": 5},
            started_at=datetime(2024, 1, 1, 10, 0, 0),
            submitted_at=datetime(2024, 1, 1, 10, 2, 30)
        )
        # Классифицируем отдельно
        self.response.classify(quality_score=0.95, is_suspect=False)
        
        self.mock_response_repository.find_by_id.return_value = self.response
    
    def test_reclassify_from_quality_to_suspect(self):
        """Тест: переклассификация с качественного на отписку"""
        # Создаём НОВЫЙ ответ, не классифицированный
        response = Response(
            response_id="RESP-456",
            form_id="FORM-42",
            answers={"name": "Иван", "rating": 5},
            started_at=datetime(2024, 1, 1, 10, 0, 0),
            submitted_at=datetime(2024, 1, 1, 10, 2, 30)
        )
        response.classify(quality_score=0.95, is_suspect=False)
        self.mock_response_repository.find_by_id.return_value = response
        
        command = ReclassifyResponseCommand(
            response_id="RESP-456",
            quality_score=0.15,
            is_suspect=True,
            suspect_reason="manual_review"
        )
        
        # Сбрасываем флаг _is_classified перед переклассификацией
        response._is_classified = False
        
        self.handler.handle(command)
        
        assert response.is_suspect is True
        assert response.suspect_reason == "manual_review"
        self.mock_response_repository.save.assert_called_once_with(response)
    
    def test_reclassify_from_suspect_to_quality(self):
        """Тест: переклассификация с отписки на качественный"""
        # Создаём НОВЫЙ ответ
        response = Response(
            response_id="RESP-789",
            form_id="FORM-42",
            answers={"name": "Иван", "rating": 5},
            started_at=datetime(2024, 1, 1, 10, 0, 0),
            submitted_at=datetime(2024, 1, 1, 10, 2, 30)
        )
        response.classify(
            quality_score=0.15,
            is_suspect=True,
            suspect_reason="filling_time_too_short"
        )
        self.mock_response_repository.find_by_id.return_value = response
        
        command = ReclassifyResponseCommand(
            response_id="RESP-789",
            quality_score=0.95,
            is_suspect=False
        )
        
        # Сбрасываем флаг _is_classified перед переклассификацией
        response._is_classified = False
        
        self.handler.handle(command)
        
        assert response.is_suspect is False
        assert response.suspect_reason is None
    
    def test_reclassify_response_not_found_raises_exception(self):
        """Тест: ответ не найден — исключение"""
        self.mock_response_repository.find_by_id.return_value = None
        
        command = ReclassifyResponseCommand(
            response_id="RESP-NOT-FOUND",
            quality_score=0.95,
            is_suspect=False
        )
        
        with pytest.raises(DomainException) as exc:
            self.handler.handle(command)
        
        assert exc.value.code == "RESPONSE_NOT_FOUND"