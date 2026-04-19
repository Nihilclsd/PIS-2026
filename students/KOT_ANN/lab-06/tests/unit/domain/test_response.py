import pytest
from datetime import datetime, timedelta
from domain.models.response import Response
from domain.exceptions.domain_exception import DomainException


class TestResponse:
    """Юнит-тесты для доменной сущности Response"""

    def setup_method(self):
        self.response = Response(
            response_id="RESP-123",
            form_id="FORM-42",
            answers={"name": "Иван", "rating": 5, "comment": "Отлично!"},
            started_at=datetime(2024, 1, 1, 10, 0, 0),
            submitted_at=datetime(2024, 1, 1, 10, 2, 30),
            ip_address="77.88.55.66",
            user_agent="Mozilla/5.0 (iPhone)"
        )

    # ========== Тесты calculate_filling_time ==========

    def test_calculate_filling_time_positive(self):
        filling_time = self.response.calculate_filling_time()
        assert filling_time == 150
        assert self.response.filling_time_sec == 150

    def test_calculate_filling_time_zero(self):
        response = Response(
            response_id="RESP-999",
            form_id="FORM-42",
            answers={},
            started_at=datetime(2024, 1, 1, 10, 0, 0),
            submitted_at=datetime(2024, 1, 1, 10, 0, 0)
        )
        filling_time = response.calculate_filling_time()
        assert filling_time == 0

    def test_calculate_filling_time_negative_raises_exception(self):
        response = Response(
            response_id="RESP-999",
            form_id="FORM-42",
            answers={},
            started_at=datetime(2024, 1, 1, 10, 2, 30),
            submitted_at=datetime(2024, 1, 1, 10, 0, 0)
        )
        with pytest.raises(DomainException) as exc:
            response.calculate_filling_time()
        assert exc.value.code == "NEGATIVE_FILLING_TIME"

    # ========== Тесты enrich_geo ==========

    def test_enrich_geo_sets_country_and_city(self):
        self.response.enrich_geo("Россия", "Москва")
        assert self.response.geo_country == "Россия"
        assert self.response.geo_city == "Москва"

    # ========== Тесты enrich_device ==========

    def test_enrich_device_sets_device_type(self):
        self.response.enrich_device("MOBILE", "iOS", "Safari")
        assert self.response.device_type == "MOBILE"
        assert self.response.device_os == "iOS"
        assert self.response.device_browser == "Safari"

    # ========== Тесты classify ==========

    def test_classify_quality_response(self):
        self.response.classify(quality_score=0.95, is_suspect=False)
        assert self.response.quality_score == 0.95
        assert self.response.is_suspect is False

    def test_classify_suspect_response_with_reason(self):
        self.response.classify(
            quality_score=0.15,
            is_suspect=True,
            suspect_reason="filling_time_too_short"
        )
        assert self.response.is_suspect is True
        assert self.response.suspect_reason == "filling_time_too_short"

    def test_classify_without_suspect_reason_raises_exception(self):
        with pytest.raises(DomainException) as exc:
            self.response.classify(quality_score=0.1, is_suspect=True, suspect_reason=None)
        assert exc.value.code == "MISSING_SUSPECT_REASON"

    def test_classify_with_invalid_quality_score_raises_exception(self):
        with pytest.raises(DomainException) as exc:
            self.response.classify(quality_score=1.5, is_suspect=False)
        assert exc.value.code == "INVALID_QUALITY_SCORE"

    def test_cannot_classify_twice(self):
        self.response.classify(quality_score=0.95, is_suspect=False)
        with pytest.raises(DomainException) as exc:
            self.response.classify(quality_score=0.90, is_suspect=False)
        assert exc.value.code == "ALREADY_CLASSIFIED"

    # ========== Тесты is_quality_response ==========

    def test_is_quality_response_returns_true(self):
        self.response.classify(quality_score=0.95, is_suspect=False)
        assert self.response.is_quality_response() is True

    def test_is_quality_response_before_classification_raises_exception(self):
        with pytest.raises(DomainException) as exc:
            self.response.is_quality_response()
        assert exc.value.code == "NOT_CLASSIFIED"