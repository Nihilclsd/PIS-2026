import pytest
from application.query.get_aggregates_query import GetAggregatesQuery


class TestGetAggregatesQuery:
    """Тесты для GetAggregatesQuery"""
    
    def test_create_query_with_valid_form_id(self):
        """Тест: создание запроса с валидным form_id"""
        query = GetAggregatesQuery(form_id="FORM-42")
        
        assert query.form_id == "FORM-42"
    
    def test_query_immutability(self):
        """Тест: запрос иммутабелен"""
        query = GetAggregatesQuery(form_id="FORM-42")
        
        with pytest.raises(Exception):
            query.form_id = "NEW-ID"
    
    def test_empty_form_id_raises_error(self):
        """Тест: пустой form_id вызывает ошибку"""
        with pytest.raises(ValueError, match="form_id cannot be empty"):
            GetAggregatesQuery(form_id="")
    
    def test_whitespace_form_id_raises_error(self):
        """Тест: form_id из пробелов вызывает ошибку"""
        with pytest.raises(ValueError, match="form_id cannot be empty"):
            GetAggregatesQuery(form_id="   ")