import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
from dataclasses import dataclass

from domain.models.response import Response
from domain.models.form import Form, FormField, AntiSpamSettings
from domain.exceptions.domain_exception import DomainException

from application.command.process_response_command import ProcessResponseCommand
from application.command.handler.process_response_handler import ProcessResponseHandler


@dataclass
class MockAntiSpamResult:
    quality_score: float
    is_suspect: bool
    suspect_reason: str = None


class TestProcessResponseHandler:
    """Тесты для ProcessResponseHandler"""
    
    def setup_method(self):
        # Создаём моки
        self.mock_form_repository = Mock()
        self.mock_response_repository = Mock()
        self.mock_geo_service = Mock()
        self.mock_anti_spam_service = Mock()
        self.mock_notification_service = Mock()
        
        # Создаём хендлер
        self.handler = ProcessResponseHandler(
            form_repository=self.mock_form_repository,
            response_repository=self.mock_response_repository,
            geo_service=self.mock_geo_service,
            anti_spam_service=self.mock_anti_spam_service,
            notification_service=self.mock_notification_service
        )
        
        # Создаём тестовую форму
        fields = [
            FormField(name="name", field_type="text", required=True),
            FormField(name="rating", field_type="rating", required=True),
            FormField(name="comment", field_type="text", required=False),
        ]
        self.form = Form(
            form_id="FORM-42",
            fields=fields,
            anti_spam_settings=AntiSpamSettings()
        )
        
        # Создаём команду
        self.command = ProcessResponseCommand(
            response_id="RESP-123",
            form_id="FORM-42",
            answers={"name": "Иван", "rating": 5, "comment": "Отлично!"},
            ip_address="77.88.55.66",
            user_agent="Mozilla/5.0 (iPhone)",
            started_at=datetime(2024, 1, 1, 10, 0, 0),
            submitted_at=datetime(2024, 1, 1, 10, 2, 30)
        )
        
        # Настройка моков
        self.mock_form_repository.find_by_id.return_value = self.form
        self.mock_geo_service.get_location.return_value = ("Россия", "Москва")
        self.mock_anti_spam_service.analyze.return_value = MockAntiSpamResult(
            quality_score=0.95,
            is_suspect=False
        )
    
    def test_handle_successful_processing(self):
        """Тест: успешная обработка ответа"""
        self.handler.handle(self.command)
        
        # Проверяем, что форма была найдена
        self.mock_form_repository.find_by_id.assert_called_once_with("FORM-42")
        
        # Проверяем, что гео-сервис был вызван
        self.mock_geo_service.get_location.assert_called_once_with("77.88.55.66")
        
        # Проверяем, что антиспам был вызван
        self.mock_anti_spam_service.analyze.assert_called_once()
        
        # Проверяем, что ответ был сохранён
        self.mock_response_repository.save.assert_called_once()
        self.mock_response_repository.update_aggregates.assert_called_once()
    
    def test_handle_form_not_found_raises_exception(self):
        """Тест: форма не найдена — исключение"""
        self.mock_form_repository.find_by_id.return_value = None
        
        with pytest.raises(DomainException) as exc:
            self.handler.handle(self.command)
        
        assert exc.value.code == "FORM_NOT_FOUND"
    
    def test_handle_geo_service_timeout_continues_without_geo(self):
        """Тест: гео-сервис недоступен — продолжаем без гео"""
        self.mock_geo_service.get_location.return_value = (None, None)
        
        self.handler.handle(self.command)
        
        # Проверяем, что сохранение всё равно произошло
        self.mock_response_repository.save.assert_called_once()
    
    def test_handle_anti_spam_classifies_suspect_response(self):
        """Тест: антиспам классифицирует отписку"""
        self.mock_anti_spam_service.analyze.return_value = MockAntiSpamResult(
            quality_score=0.15,
            is_suspect=True,
            suspect_reason="filling_time_too_short"
        )
        
        self.handler.handle(self.command)
        
        saved_response = self.mock_response_repository.save.call_args[0][0]
        assert saved_response.is_suspect is True
        assert saved_response.suspect_reason == "filling_time_too_short"
    
    def test_handle_low_rating_triggers_notification(self):
        """Тест: низкая оценка вызывает уведомление"""
        command = ProcessResponseCommand(
            response_id="RESP-456",
            form_id="FORM-42",
            answers={"name": "Иван", "rating": 2, "comment": "Плохо"},
            ip_address="77.88.55.66",
            user_agent="Mozilla/5.0",
            started_at=datetime(2024, 1, 1, 10, 0, 0),
            submitted_at=datetime(2024, 1, 1, 10, 2, 30)
        )
        
        self.mock_anti_spam_service.analyze.return_value = MockAntiSpamResult(
            quality_score=0.95,
            is_suspect=False
        )
        
        self.handler.handle(command)
        
        self.mock_notification_service.notify_critical_feedback.assert_called_once()
    
    def test_handle_high_rating_no_notification(self):
        """Тест: высокая оценка не вызывает уведомление"""
        self.handler.handle(self.command)
        
        self.mock_notification_service.notify_critical_feedback.assert_not_called()