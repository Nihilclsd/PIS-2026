import pytest
from datetime import datetime
from unittest.mock import Mock

from domain.models.form import Form, FormField, AntiSpamSettings
from domain.exceptions.domain_exception import DomainException

from application.command.process_response_command import ProcessResponseCommand
from application.command.handler.process_response_handler import ProcessResponseHandler


class TestProcessResponseHandler:
    """Юнит-тесты для ProcessResponseHandler"""

    def setup_method(self):
        self.mock_form_repository = Mock()
        self.mock_response_repository = Mock()
        self.mock_geo_service = Mock()
        self.mock_anti_spam_service = Mock()
        self.mock_notification_service = Mock()

        self.handler = ProcessResponseHandler(
            form_repository=self.mock_form_repository,
            response_repository=self.mock_response_repository,
            geo_service=self.mock_geo_service,
            anti_spam_service=self.mock_anti_spam_service,
            notification_service=self.mock_notification_service
        )

        fields = [
            FormField(name="name", field_type="text", required=True),
            FormField(name="rating", field_type="rating", required=True),
        ]
        self.form = Form(form_id="FORM-42", fields=fields)

        self.command = ProcessResponseCommand(
            response_id="RESP-123",
            form_id="FORM-42",
            answers={"name": "Иван", "rating": 5},
            ip_address="77.88.55.66",
            user_agent="Mozilla/5.0",
            started_at=datetime(2024, 1, 1, 10, 0, 0),
            submitted_at=datetime(2024, 1, 1, 10, 2, 30)
        )

        self.mock_form_repository.find_by_id.return_value = self.form
        self.mock_geo_service.get_location.return_value = ("Россия", "Москва")
        self.mock_anti_spam_service.analyze.return_value = Mock(
            quality_score=0.95,
            is_suspect=False,
            suspect_reason=None
        )

    def test_handle_successful_processing(self):
        self.handler.handle(self.command)

        self.mock_form_repository.find_by_id.assert_called_once_with("FORM-42")
        self.mock_geo_service.get_location.assert_called_once()
        self.mock_anti_spam_service.analyze.assert_called_once()
        self.mock_response_repository.save.assert_called_once()
        self.mock_response_repository.update_aggregates.assert_called_once()

    def test_handle_form_not_found_raises_exception(self):
        self.mock_form_repository.find_by_id.return_value = None

        with pytest.raises(DomainException) as exc:
            self.handler.handle(self.command)
        assert exc.value.code == "FORM_NOT_FOUND"

    def test_handle_geo_service_timeout_continues_without_geo(self):
        self.mock_geo_service.get_location.return_value = (None, None)

        self.handler.handle(self.command)

        self.mock_response_repository.save.assert_called_once()

    def test_handle_anti_spam_classifies_suspect_response(self):
        self.mock_anti_spam_service.analyze.return_value = Mock(
            quality_score=0.15,
            is_suspect=True,
            suspect_reason="filling_time_too_short"
        )

        self.handler.handle(self.command)

        saved_response = self.mock_response_repository.save.call_args[0][0]
        assert saved_response.is_suspect is True

    def test_handle_low_rating_triggers_notification(self):
        command = ProcessResponseCommand(
            response_id="RESP-456",
            form_id="FORM-42",
            answers={"name": "Иван", "rating": 2, "comment": "Плохо"},
            ip_address="77.88.55.66",
            user_agent="Mozilla/5.0",
            started_at=datetime(2024, 1, 1, 10, 0, 0),
            submitted_at=datetime(2024, 1, 1, 10, 2, 30)
        )
        self.mock_form_repository.find_by_id.return_value = self.form
        self.mock_anti_spam_service.analyze.return_value = Mock(
            quality_score=0.95,
            is_suspect=False,
            suspect_reason=None
        )

        self.handler.handle(command)

        self.mock_notification_service.notify_critical_feedback.assert_called_once()