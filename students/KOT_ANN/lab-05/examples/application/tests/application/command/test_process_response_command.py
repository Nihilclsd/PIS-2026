import pytest
from datetime import datetime
from application.command.process_response_command import ProcessResponseCommand


class TestProcessResponseCommand:
    """Тесты для ProcessResponseCommand"""
    
    def setup_method(self):
        self.valid_command_data = {
            "response_id": "RESP-123",
            "form_id": "FORM-42",
            "answers": {"name": "Иван", "rating": 5},
            "ip_address": "77.88.55.66",
            "user_agent": "Mozilla/5.0 (iPhone)",
            "started_at": datetime(2024, 1, 1, 10, 0, 0),
            "submitted_at": datetime(2024, 1, 1, 10, 2, 30)
        }
    
    def test_create_command_with_valid_data(self):
        """Тест: создание команды с валидными данными"""
        command = ProcessResponseCommand(**self.valid_command_data)
        
        assert command.response_id == "RESP-123"
        assert command.form_id == "FORM-42"
        assert command.answers == {"name": "Иван", "rating": 5}
        assert command.ip_address == "77.88.55.66"
        assert command.user_agent == "Mozilla/5.0 (iPhone)"
    
    def test_command_immutability(self):
        """Тест: команда иммутабельна (frozen=True)"""
        command = ProcessResponseCommand(**self.valid_command_data)
        
        with pytest.raises(Exception):
            command.response_id = "NEW-ID"
    
    def test_empty_response_id_raises_error(self):
        """Тест: пустой response_id вызывает ошибку"""
        data = self.valid_command_data.copy()
        data["response_id"] = ""
        
        with pytest.raises(ValueError, match="response_id cannot be empty"):
            ProcessResponseCommand(**data)
    
    def test_whitespace_response_id_raises_error(self):
        """Тест: response_id из пробелов вызывает ошибку"""
        data = self.valid_command_data.copy()
        data["response_id"] = "   "
        
        with pytest.raises(ValueError, match="response_id cannot be empty"):
            ProcessResponseCommand(**data)
    
    def test_empty_form_id_raises_error(self):
        """Тест: пустой form_id вызывает ошибку"""
        data = self.valid_command_data.copy()
        data["form_id"] = ""
        
        with pytest.raises(ValueError, match="form_id cannot be empty"):
            ProcessResponseCommand(**data)
    
    def test_empty_answers_raises_error(self):
        """Тест: пустые answers вызывают ошибку"""
        data = self.valid_command_data.copy()
        data["answers"] = {}
        
        with pytest.raises(ValueError, match="answers cannot be empty"):
            ProcessResponseCommand(**data)
    
    def test_started_at_after_submitted_at_raises_error(self):
        """Тест: started_at после submitted_at вызывает ошибку"""
        data = self.valid_command_data.copy()
        data["started_at"] = datetime(2024, 1, 1, 10, 5, 0)
        data["submitted_at"] = datetime(2024, 1, 1, 10, 0, 0)
        
        with pytest.raises(ValueError, match="started_at cannot be after submitted_at"):
            ProcessResponseCommand(**data)
    
    def test_optional_fields_can_be_none(self):
        """Тест: опциональные поля могут быть None"""
        data = self.valid_command_data.copy()
        data["ip_address"] = None
        data["user_agent"] = None
        
        command = ProcessResponseCommand(**data)
        
        assert command.ip_address is None
        assert command.user_agent is None