import pytest
from datetime import datetime
from unittest.mock import Mock

from domain.events.response_events import ResponseClassifiedEvent, ResponseEnrichedEvent
from cqrs.projection.response_projection import ResponseProjection
from cqrs.read_model.response_view import ResponseView


class TestResponseProjection:
    """Тесты для проекции Read Model"""
    
    def setup_method(self):
        self.mock_view_repo = Mock()
        self.mock_form_repo = Mock()
        self.projection = ResponseProjection(
            view_repository=self.mock_view_repo,
            form_repository=self.mock_form_repo
        )
    
    def test_on_response_classified_updates_existing_view(self):
        """Тест: событие классификации обновляет существующий view"""
        existing_view = ResponseView(
            response_id="RESP-123",
            form_id="FORM-42",
            form_title=None,
            answers={},
            rating=None,
            comment=None,
            started_at=datetime.now(),
            submitted_at=datetime.now(),
            filling_time_sec=0,
            ip_address=None,
            country=None,
            city=None,
            device_type=None,
            is_suspect=False,
            quality_score=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.mock_view_repo.find_by_id.return_value = existing_view
        
        event = ResponseClassifiedEvent(
            response_id="RESP-123",
            form_id="FORM-42",
            is_suspect=True,
            quality_score=0.15,
            suspect_reason="too_fast",
            occurred_at=datetime.now()
        )
        
        self.projection.on_response_classified(event)
        
        assert existing_view.is_suspect is True
        assert existing_view.quality_score == 0.15
        self.mock_view_repo.save.assert_called_once_with(existing_view)
    
    def test_on_response_classified_creates_partial_view_if_not_exists(self):
        """Тест: если view не существует, логируется предупреждение"""
        self.mock_view_repo.find_by_id.return_value = None
        
        event = ResponseClassifiedEvent(
            response_id="RESP-123",
            form_id="FORM-42",
            is_suspect=True,
            quality_score=0.15,
            suspect_reason="too_fast",
            occurred_at=datetime.now()
        )
        
        self.projection.on_response_classified(event)
        
        # save не вызывается, только логирование
        self.mock_view_repo.save.assert_not_called()
    
    def test_on_response_enriched_updates_existing_view(self):
        """Тест: событие обогащения обновляет гео и устройство"""
        existing_view = ResponseView(
            response_id="RESP-123",
            form_id="FORM-42",
            form_title=None,
            answers={},
            rating=None,
            comment=None,
            started_at=datetime.now(),
            submitted_at=datetime.now(),
            filling_time_sec=0,
            ip_address="77.88.55.66",
            country=None,
            city=None,
            device_type=None,
            is_suspect=False,
            quality_score=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.mock_view_repo.find_by_id.return_value = existing_view
        
        event = ResponseEnrichedEvent(
            response_id="RESP-123",
            form_id="FORM-42",
            geo_country="Россия",
            geo_city="Москва",
            device_type="MOBILE",
            occurred_at=datetime.now()
        )
        
        self.projection.on_response_enriched(event)
        
        assert existing_view.country == "Россия"
        assert existing_view.city == "Москва"
        assert existing_view.device_type == "MOBILE"
        self.mock_view_repo.save.assert_called_once_with(existing_view)
    
    def test_rebuild_from_scratch_creates_view(self):
        """Тест: перестроение Read Model из Write Model"""
        from domain.models.response import Response
        
        response = Response(
            response_id="RESP-123",
            form_id="FORM-42",
            answers={"name": "Иван", "rating": 5},
            started_at=datetime.now(),
            submitted_at=datetime.now(),
            ip_address="77.88.55.66",
            user_agent="Mozilla/5.0"
        )
        response.classify(quality_score=0.95, is_suspect=False)
        response.enrich_geo("Россия", "Москва")
        response.enrich_device("MOBILE")
        response.calculate_filling_time()
        
        mock_form = Mock()
        mock_form.title = "Тестовая форма"
        self.mock_form_repo.find_by_id.return_value = mock_form
        
        self.projection.rebuild_from_scratch(response)
        
        self.mock_view_repo.save.assert_called_once()
        saved_view = self.mock_view_repo.save.call_args[0][0]
        assert saved_view.response_id == "RESP-123"
        assert saved_view.country == "Россия"
        assert saved_view.quality_score == 0.95