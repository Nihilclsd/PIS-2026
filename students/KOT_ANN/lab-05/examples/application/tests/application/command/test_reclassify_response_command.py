import pytest
from application.command.reclassify_response_command import ReclassifyResponseCommand


class TestReclassifyResponseCommand:
    """Тесты для ReclassifyResponseCommand"""
    
    def test_create_command_for_quality_response(self):
        """Тест: создание команды для качественного ответа"""
        command = ReclassifyResponseCommand(
            response_id="RESP-123",
            quality_score=0.95,
            is_suspect=False
        )
        
        assert command.response_id == "RESP-123"
        assert command.quality_score == 0.95
        assert command.is_suspect is False
        assert command.suspect_reason is None
    
    def test_create_command_for_suspect_response_with_reason(self):
        """Тест: создание команды для отписки с причиной"""
        command = ReclassifyResponseCommand(
            response_id="RESP-123",
            quality_score=0.15,
            is_suspect=True,
            suspect_reason="filling_time_too_short"
        )
        
        assert command.response_id == "RESP-123"
        assert command.quality_score == 0.15
        assert command.is_suspect is True
        assert command.suspect_reason == "filling_time_too_short"
    
    def test_command_immutability(self):
        """Тест: команда иммутабельна"""
        command = ReclassifyResponseCommand(
            response_id="RESP-123",
            quality_score=0.95,
            is_suspect=False
        )
        
        with pytest.raises(Exception):
            command.response_id = "NEW-ID"
    
    def test_empty_response_id_raises_error(self):
        """Тест: пустой response_id вызывает ошибку"""
        with pytest.raises(ValueError, match="response_id cannot be empty"):
            ReclassifyResponseCommand(
                response_id="",
                quality_score=0.95,
                is_suspect=False
            )
    
    def test_quality_score_too_high_raises_error(self):
        """Тест: quality_score > 1 вызывает ошибку"""
        with pytest.raises(ValueError, match="quality_score must be between 0 and 1"):
            ReclassifyResponseCommand(
                response_id="RESP-123",
                quality_score=1.5,
                is_suspect=False
            )
    
    def test_quality_score_too_low_raises_error(self):
        """Тест: quality_score < 0 вызывает ошибку"""
        with pytest.raises(ValueError, match="quality_score must be between 0 and 1"):
            ReclassifyResponseCommand(
                response_id="RESP-123",
                quality_score=-0.5,
                is_suspect=False
            )
    
    def test_suspect_without_reason_raises_error(self):
        """Тест: is_suspect=True без причины вызывает ошибку"""
        with pytest.raises(ValueError, match="suspect_reason is required when is_suspect=True"):
            ReclassifyResponseCommand(
                response_id="RESP-123",
                quality_score=0.1,
                is_suspect=True,
                suspect_reason=None
            )
    
    def test_suspect_with_empty_reason_raises_error(self):
        """Тест: is_suspect=True с пустой причиной вызывает ошибку"""
        with pytest.raises(ValueError, match="suspect_reason is required when is_suspect=True"):
            ReclassifyResponseCommand(
                response_id="RESP-123",
                quality_score=0.1,
                is_suspect=True,
                suspect_reason=""
            )