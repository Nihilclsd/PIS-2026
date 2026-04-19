import pytest
from domain.models.aggregate import FormAggregates
from domain.exceptions.domain_exception import DomainException


class TestFormAggregates:
    """Юнит-тесты для Value Object FormAggregates"""

    def setup_method(self):
        self.aggregates = FormAggregates(form_id="FORM-42")

    def test_initial_values(self):
        assert self.aggregates.total_responses == 0
        assert self.aggregates.quality_responses == 0
        assert self.aggregates.suspect_responses == 0

    def test_increment_total(self):
        self.aggregates.increment_total()
        assert self.aggregates.total_responses == 1

    def test_increment_quality(self):
        self.aggregates.increment_quality()
        assert self.aggregates.quality_responses == 1

    def test_increment_suspect(self):
        self.aggregates.increment_suspect()
        assert self.aggregates.suspect_responses == 1

    def test_add_rating_valid(self):
        self.aggregates.increment_total()
        self.aggregates.add_rating(5.0)
        assert self.aggregates.average_rating == 5.0

    def test_add_rating_too_low_raises_exception(self):
        self.aggregates.increment_total()
        with pytest.raises(DomainException) as exc:
            self.aggregates.add_rating(0.5)
        assert exc.value.code == "INVALID_RATING"

    def test_add_rating_without_responses_raises_exception(self):
        with pytest.raises(DomainException) as exc:
            self.aggregates.add_rating(4.0)
        assert exc.value.code == "NO_RESPONSES"

    def test_quality_rate_calculation(self):
        self.aggregates.increment_total()
        self.aggregates.increment_total()
        self.aggregates.increment_quality()
        assert self.aggregates.quality_rate == 50.0

    def test_suspect_rate_calculation(self):
        self.aggregates.increment_total()
        self.aggregates.increment_total()
        self.aggregates.increment_suspect()
        assert self.aggregates.suspect_rate == 50.0