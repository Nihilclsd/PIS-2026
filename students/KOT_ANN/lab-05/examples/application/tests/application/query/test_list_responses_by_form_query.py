import pytest
from application.query.list_responses_by_form_query import ListResponsesByFormQuery


class TestListResponsesByFormQuery:
    """Тесты для ListResponsesByFormQuery"""
    
    def test_create_query_with_default_values(self):
        """Тест: создание запроса со значениями по умолчанию"""
        query = ListResponsesByFormQuery(form_id="FORM-42")
        
        assert query.form_id == "FORM-42"
        assert query.limit == 100
        assert query.offset == 0
        assert query.include_suspect is None
    
    def test_create_query_with_custom_values(self):
        """Тест: создание запроса с пользовательскими значениями"""
        query = ListResponsesByFormQuery(
            form_id="FORM-42",
            limit=50,
            offset=10,
            include_suspect=False
        )
        
        assert query.form_id == "FORM-42"
        assert query.limit == 50
        assert query.offset == 10
        assert query.include_suspect is False
    
    def test_query_immutability(self):
        """Тест: запрос иммутабелен"""
        query = ListResponsesByFormQuery(form_id="FORM-42")
        
        with pytest.raises(Exception):
            query.limit = 200
    
    def test_empty_form_id_raises_error(self):
        """Тест: пустой form_id вызывает ошибку"""
        with pytest.raises(ValueError, match="form_id cannot be empty"):
            ListResponsesByFormQuery(form_id="")
    
    def test_limit_too_low_raises_error(self):
        """Тест: limit < 1 вызывает ошибку"""
        with pytest.raises(ValueError, match="limit must be between 1 and 1000"):
            ListResponsesByFormQuery(form_id="FORM-42", limit=0)
    
    def test_limit_too_high_raises_error(self):
        """Тест: limit > 1000 вызывает ошибку"""
        with pytest.raises(ValueError, match="limit must be between 1 and 1000"):
            ListResponsesByFormQuery(form_id="FORM-42", limit=1001)
    
    def test_negative_offset_raises_error(self):
        """Тест: offset < 0 вызывает ошибку"""
        with pytest.raises(ValueError, match="offset cannot be negative"):
            ListResponsesByFormQuery(form_id="FORM-42", offset=-1)