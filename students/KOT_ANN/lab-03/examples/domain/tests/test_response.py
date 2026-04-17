import pytest
from datetime import datetime, timedelta
from domain.models.response import Response
from domain.exceptions.domain_exception import DomainException


class TestResponse:
    """Тесты для доменной модели Response"""
    
    def setup_method(self):
        """Подготовка тестовых данных"""
        self.response_id = "RESP-12345"
        self.form_id = "FORM-42"
        self.answers = {"name": "Иван", "rating": 5, "comment": "Отлично!"}
        self.started_at = datetime(2024, 11, 8, 10, 0, 0)
        self.submitted_at = datetime(2024, 11, 8, 10, 2, 30)
        self.ip_address = "77.88.55.66"
        self.user_agent = "Mozilla/5.0 (iPhone)"
        
        self.response = Response(
            response_id=self.response_id,
            form_id=self.form_id,
            answers=self.answers,
            started_at=self.started_at,
            submitted_at=self.submitted_at,
            ip_address=self.ip_address,
            user_agent=self.user_agent
        )
    
    # ========== Тесты для calculate_filling_time ==========
    
    def test_calculate_filling_time_positive(self):
        """Тест: время заполнения вычисляется корректно для положительного интервала"""
        filling_time = self.response.calculate_filling_time()
        expected = 150  # 2 минуты 30 секунд
        assert filling_time == expected
        assert self.response.filling_time_sec == expected
    
    def test_calculate_filling_time_zero(self):
        """Тест: время заполнения = 0, если ответ отправлен мгновенно"""
        response = Response(
            response_id="RESP-999",
            form_id="FORM-42",
            answers={},
            started_at=self.started_at,
            submitted_at=self.started_at
        )
        filling_time = response.calculate_filling_time()
        assert filling_time == 0
        assert response.filling_time_sec == 0
    
    def test_calculate_filling_time_negative_raises_exception(self):
        """Тест: отрицательное время заполнения вызывает исключение"""
        response = Response(
            response_id="RESP-999",
            form_id="FORM-42",
            answers={},
            started_at=self.submitted_at,  # start > end
            submitted_at=self.started_at
        )
        with pytest.raises(DomainException) as exc_info:
            response.calculate_filling_time()
        assert exc_info.value.code == "NEGATIVE_FILLING_TIME"
    
    # ========== Тесты для enrich_geo ==========
    
    def test_enrich_geo_sets_country_and_city(self):
        """Тест: обогащение гео-данными устанавливает страну и город"""
        self.response.enrich_geo("Россия", "Москва")
        assert self.response.geo_country == "Россия"
        assert self.response.geo_city == "Москва"
    
    def test_enrich_geo_with_none_values(self):
        """Тест: обогащение гео-данными с None"""
        self.response.enrich_geo(None, None)
        assert self.response.geo_country is None
        assert self.response.geo_city is None
    
    # ========== Тесты для enrich_device ==========
    
    def test_enrich_device_sets_device_type(self):
        """Тест: обогащение данными устройства"""
        self.response.enrich_device("MOBILE", "iOS", "Safari")
        assert self.response.device_type == "MOBILE"
        assert self.response.device_os == "iOS"
        assert self.response.device_browser == "Safari"
    
    def test_enrich_device_without_os_and_browser(self):
        """Тест: обогащение данными устройства только с типом"""
        self.response.enrich_device("DESKTOP")
        assert self.response.device_type == "DESKTOP"
        assert self.response.device_os is None
        assert self.response.device_browser is None
    
    # ========== Тесты для classify ==========
    
    def test_classify_quality_response(self):
        """Тест: классификация качественного ответа"""
        self.response.classify(quality_score=0.95, is_suspect=False)
        assert self.response.quality_score == 0.95
        assert self.response.is_suspect is False
        assert self.response.suspect_reason is None
    
    def test_classify_suspect_response_with_reason(self):
        """Тест: классификация отписки с указанием причины"""
        self.response.classify(
            quality_score=0.15,
            is_suspect=True,
            suspect_reason="filling_time_too_short"
        )
        assert self.response.quality_score == 0.15
        assert self.response.is_suspect is True
        assert self.response.suspect_reason == "filling_time_too_short"
    
    def test_classify_without_suspect_reason_raises_exception(self):
        """Тест: классификация отписки без причины вызывает исключение"""
        with pytest.raises(DomainException) as exc_info:
            self.response.classify(quality_score=0.1, is_suspect=True, suspect_reason=None)
        assert exc_info.value.code == "MISSING_SUSPECT_REASON"
    
    def test_classify_with_invalid_quality_score_too_high(self):
        """Тест: quality_score > 1 вызывает исключение"""
        with pytest.raises(DomainException) as exc_info:
            self.response.classify(quality_score=1.5, is_suspect=False)
        assert exc_info.value.code == "INVALID_QUALITY_SCORE"
    
    def test_classify_with_invalid_quality_score_too_low(self):
        """Тест: quality_score < 0 вызывает исключение"""
        with pytest.raises(DomainException) as exc_info:
            self.response.classify(quality_score=-0.5, is_suspect=False)
        assert exc_info.value.code == "INVALID_QUALITY_SCORE"
    
    def test_cannot_classify_twice(self):
        """Тест: повторная классификация вызывает исключение"""
        self.response.classify(quality_score=0.95, is_suspect=False)
        with pytest.raises(DomainException) as exc_info:
            self.response.classify(quality_score=0.90, is_suspect=False)
        assert exc_info.value.code == "ALREADY_CLASSIFIED"
    
    # ========== Тесты для is_quality_response ==========
    
    def test_is_quality_response_returns_true_for_quality_response(self):
        """Тест: is_quality_response() возвращает True для качественного ответа"""
        self.response.classify(quality_score=0.95, is_suspect=False)
        assert self.response.is_quality_response() is True
    
    def test_is_quality_response_returns_false_for_suspect_response(self):
        """Тест: is_quality_response() возвращает False для отписки"""
        self.response.classify(quality_score=0.15, is_suspect=True, suspect_reason="test")
        assert self.response.is_quality_response() is False
    
    def test_is_quality_response_before_classification_raises_exception(self):
        """Тест: вызов is_quality_response() до классификации вызывает исключение"""
        with pytest.raises(DomainException) as exc_info:
            self.response.is_quality_response()
        assert exc_info.value.code == "NOT_CLASSIFIED"
    
    # ========== Тесты для is_suspect_response ==========
    
    def test_is_suspect_response_returns_true_for_suspect_response(self):
        """Тест: is_suspect_response() возвращает True для отписки"""
        self.response.classify(quality_score=0.15, is_suspect=True, suspect_reason="test")
        assert self.response.is_suspect_response() is True
    
    def test_is_suspect_response_returns_false_for_quality_response(self):
        """Тест: is_suspect_response() возвращает False для качественного ответа"""
        self.response.classify(quality_score=0.95, is_suspect=False)
        assert self.response.is_suspect_response() is False
    
    def test_is_suspect_response_before_classification_raises_exception(self):
        """Тест: вызов is_suspect_response() до классификации вызывает исключение"""
        with pytest.raises(DomainException) as exc_info:
            self.response.is_suspect_response()
        assert exc_info.value.code == "NOT_CLASSIFIED"
    
    # ========== Тесты для is_processed ==========
    
    def test_is_processed_returns_false_before_processing(self):
        """Тест: is_processed() возвращает False до обработки"""
        assert self.response.is_processed() is False
    
    def test_is_processed_returns_true_after_full_processing(self):
        """Тест: is_processed() возвращает True после полной обработки"""
        self.response.calculate_filling_time()
        self.response.classify(quality_score=0.95, is_suspect=False)
        assert self.response.is_processed() is True
    
    # ========== Тесты для to_dict ==========
    
    def test_to_dict_returns_all_fields(self):
        """Тест: to_dict() возвращает словарь со всеми полями"""
        self.response.calculate_filling_time()
        self.response.enrich_geo("Россия", "Москва")
        self.response.enrich_device("MOBILE", "iOS", "Safari")
        self.response.classify(quality_score=0.95, is_suspect=False)
        
        result = self.response.to_dict()
        
        assert result["response_id"] == self.response_id
        assert result["form_id"] == self.form_id
        assert result["answers"] == self.answers
        assert result["geo_country"] == "Россия"
        assert result["geo_city"] == "Москва"
        assert result["device_type"] == "MOBILE"
        assert result["quality_score"] == 0.95
        assert result["is_suspect"] is False