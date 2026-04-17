import pytest
from domain.models.aggregate import FormAggregates
from domain.exceptions.domain_exception import DomainException


class TestFormAggregates:
    """Тесты для Value Object FormAggregates"""
    
    def setup_method(self):
        """Подготовка тестовых данных"""
        self.form_id = "FORM-42"
        self.aggregates = FormAggregates(form_id=self.form_id)
    
    def test_initial_values(self):
        """Тест: начальные значения агрегатов"""
        assert self.aggregates.form_id == self.form_id
        assert self.aggregates.total_responses == 0
        assert self.aggregates.quality_responses == 0
        assert self.aggregates.suspect_responses == 0
        assert self.aggregates.average_rating == 0.0
    
    def test_increment_total(self):
        """Тест: increment_total() увеличивает счётчик"""
        self.aggregates.increment_total()
        assert self.aggregates.total_responses == 1
        self.aggregates.increment_total()
        assert self.aggregates.total_responses == 2
    
    def test_increment_quality(self):
        """Тест: increment_quality() увеличивает счётчик качественных ответов"""
        self.aggregates.increment_quality()
        assert self.aggregates.quality_responses == 1
        self.aggregates.increment_quality()
        assert self.aggregates.quality_responses == 2
    
    def test_increment_suspect(self):
        """Тест: increment_suspect() увеличивает счётчик подозрительных ответов"""
        self.aggregates.increment_suspect()
        assert self.aggregates.suspect_responses == 1
        self.aggregates.increment_suspect()
        assert self.aggregates.suspect_responses == 2
    
    def test_add_rating_valid(self):
        """Тест: добавление валидного рейтинга"""
        self.aggregates.increment_total()  # сначала увеличиваем счётчик
        self.aggregates.add_rating(5.0)
        assert self.aggregates.average_rating == 5.0
        
        self.aggregates.increment_total()
        self.aggregates.add_rating(3.0)
        assert self.aggregates.average_rating == 4.0  # (5 + 3) / 2 = 4
    
    def test_add_rating_too_low_raises_exception(self):
        """Тест: добавление рейтинга < 1 вызывает исключение"""
        self.aggregates.increment_total()
        with pytest.raises(DomainException) as exc_info:
            self.aggregates.add_rating(0.5)
        assert exc_info.value.code == "INVALID_RATING"
    
    def test_add_rating_too_high_raises_exception(self):
        """Тест: добавление рейтинга > 5 вызывает исключение"""
        self.aggregates.increment_total()
        with pytest.raises(DomainException) as exc_info:
            self.aggregates.add_rating(5.5)
        assert exc_info.value.code == "INVALID_RATING"
    
    def test_add_rating_without_responses_raises_exception(self):
        """Тест: добавление рейтинга без ответов вызывает исключение"""
        with pytest.raises(DomainException) as exc_info:
            self.aggregates.add_rating(4.0)
        assert exc_info.value.code == "NO_RESPONSES"
    
    def test_update_average_rating_valid(self):
        """Тест: update_average_rating() корректно обновляет средний рейтинг"""
        # Добавляем два ответа с рейтингами 4 и 5
        self.aggregates.increment_total()
        self.aggregates.add_rating(4.0)
        self.aggregates.increment_total()
        self.aggregates.add_rating(5.0)
        assert self.aggregates.average_rating == 4.5
        
        # Добавляем третий ответ через update_average_rating
        self.aggregates.increment_total()
        self.aggregates.update_average_rating(3.0)
        assert self.aggregates.average_rating == 4.0  # (4+5+3)/3 = 4
    
    def test_update_average_rating_without_responses_raises_exception(self):
        """Тест: update_average_rating() без ответов вызывает исключение"""
        with pytest.raises(DomainException) as exc_info:
            self.aggregates.update_average_rating(4.0)
        assert exc_info.value.code == "NO_RESPONSES"
    
    def test_quality_rate_calculation(self):
        """Тест: качественный процент ответов"""
        self.aggregates.increment_total()
        self.aggregates.increment_total()
        self.aggregates.increment_total()
        self.aggregates.increment_quality()
        self.aggregates.increment_quality()
        # 2 качественных из 3 = 66.66%
        assert self.aggregates.quality_rate == pytest.approx(66.66666666666666)
    
    def test_quality_rate_with_zero_responses(self):
        """Тест: quality_rate() при нуле ответов возвращает 0"""
        assert self.aggregates.quality_rate == 0.0
    
    def test_suspect_rate_calculation(self):
        """Тест: процент подозрительных ответов"""
        self.aggregates.increment_total()
        self.aggregates.increment_total()
        self.aggregates.increment_total()
        self.aggregates.increment_total()
        self.aggregates.increment_suspect()
        # 1 подозрительный из 4 = 25%
        assert self.aggregates.suspect_rate == 25.0
    
    def test_suspect_rate_with_zero_responses(self):
        """Тест: suspect_rate() при нуле ответов возвращает 0"""
        assert self.aggregates.suspect_rate == 0.0
    
    def test_to_dict_returns_correct_structure(self):
        """Тест: to_dict() возвращает правильную структуру"""
        self.aggregates.increment_total()
        self.aggregates.increment_total()
        self.aggregates.increment_quality()
        self.aggregates.add_rating(5.0)  # сначала total должен быть > 0
        
        result = self.aggregates.to_dict()
        
        assert result["form_id"] == self.form_id
        assert result["total_responses"] == 2
        assert result["quality_responses"] == 1
        assert result["suspect_responses"] == 0
        assert "average_rating" in result
        assert "quality_rate" in result
        assert "suspect_rate" in result
    
    def test_merge_aggregates_with_add_operator(self):
        """Тест: объединение двух агрегатов через оператор +"""
        agg1 = FormAggregates(form_id=self.form_id)
        agg1.increment_total()
        agg1.increment_total()
        agg1.increment_quality()
        
        agg2 = FormAggregates(form_id=self.form_id)
        agg2.increment_total()
        agg2.increment_suspect()
        
        merged = agg1 + agg2
        
        assert merged.form_id == self.form_id
        assert merged.total_responses == 3
        assert merged.quality_responses == 1
        assert merged.suspect_responses == 1
    
    def test_merge_aggregates_different_forms_raises_exception(self):
        """Тест: объединение агрегатов разных форм вызывает исключение"""
        agg1 = FormAggregates(form_id="FORM-1")
        agg2 = FormAggregates(form_id="FORM-2")
        
        with pytest.raises(DomainException) as exc_info:
            agg1 + agg2
        assert exc_info.value.code == "FORM_ID_MISMATCH"