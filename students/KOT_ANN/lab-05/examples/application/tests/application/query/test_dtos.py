import pytest
from datetime import datetime

from domain.models.response import Response
from domain.models.aggregate import FormAggregates

from application.query.dto.response_dto import ResponseDto
from application.query.dto.form_aggregates_dto import FormAggregatesDto


class TestResponseDto:
    """Тесты для ResponseDto"""
    
    def test_from_domain_creates_dto(self):
        """Тест: from_domain() создаёт DTO из доменной сущности"""
        response = Response(
            response_id="RESP-123",  # ← было id, стало response_id
            form_id="FORM-42",
            answers={"name": "Иван", "rating": 5},
            started_at=datetime(2024, 1, 1, 10, 0, 0),
            submitted_at=datetime(2024, 1, 1, 10, 2, 30),
            ip_address="77.88.55.66",
            user_agent="Mozilla/5.0"
        )
        response.enrich_geo("Россия", "Москва")
        response.enrich_device("MOBILE")
        response.calculate_filling_time()
        response.classify(quality_score=0.95, is_suspect=False)
        
        dto = ResponseDto.from_domain(response)
        
        assert dto.response_id == "RESP-123"  # ← было id, стало response_id
        assert dto.form_id == "FORM-42"
        assert dto.answers == {"name": "Иван", "rating": 5}
        assert dto.geo_country == "Россия"
        assert dto.geo_city == "Москва"
        assert dto.device_type == "MOBILE"
        assert dto.filling_time_sec == 150
        assert dto.quality_score == 0.95
        assert dto.is_suspect is False
    
    def test_from_domain_handles_none_values(self):
        """Тест: from_domain() корректно обрабатывает None значения"""
        response = Response(
            response_id="RESP-123",  # ← было id, стало response_id
            form_id="FORM-42",
            answers={},
            started_at=datetime(2024, 1, 1, 10, 0, 0),
            submitted_at=datetime(2024, 1, 1, 10, 2, 30)
        )
        
        dto = ResponseDto.from_domain(response)
        
        assert dto.geo_country is None
        assert dto.device_type is None
        assert dto.quality_score is None
        assert dto.is_suspect is None


class TestFormAggregatesDto:
    """Тесты для FormAggregatesDto"""
    
    def test_from_domain_creates_dto(self):
        """Тест: from_domain() создаёт DTO из доменного VO"""
        aggregates = FormAggregates(
            form_id="FORM-42",
            total_responses=100,
            quality_responses=80,
            suspect_responses=20,
            average_rating=4.2
        )
        
        dto = FormAggregatesDto.from_domain(aggregates)
        
        assert dto.form_id == "FORM-42"
        assert dto.total_responses == 100
        assert dto.quality_responses == 80
        assert dto.suspect_responses == 20
        assert dto.average_rating == 4.2
        assert dto.quality_rate == 80.0
        assert dto.suspect_rate == 20.0
    
    def test_from_domain_returns_none_for_none(self):
        """Тест: from_domain() возвращает None для None"""
        result = FormAggregatesDto.from_domain(None)
        
        assert result is None
    
    def test_from_domain_handles_zero_responses(self):
        """Тест: from_domain() обрабатывает нулевые ответы"""
        aggregates = FormAggregates(form_id="FORM-42")
        
        dto = FormAggregatesDto.from_domain(aggregates)
        
        assert dto.total_responses == 0
        assert dto.quality_rate == 0.0
        assert dto.suspect_rate == 0.0