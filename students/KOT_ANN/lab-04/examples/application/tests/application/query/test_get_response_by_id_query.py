import pytest
from application.query.get_response_by_id_query import GetResponseByIdQuery


class TestGetResponseByIdQuery:
    """Тесты для GetResponseByIdQuery"""
    
    def test_create_query_with_valid_response_id(self):
        """Тест: создание запроса с валидным response_id"""
        query = GetResponseByIdQuery(response_id="RESP-123")
        
        assert query.response_id == "RESP-123"
    
    def test_query_immutability(self):
        """Тест: запрос иммутабелен"""
        query = GetResponseByIdQuery(response_id="RESP-123")
        
        with pytest.raises(Exception):
            query.response_id = "NEW-ID"
    
    def test_empty_response_id_raises_error(self):
        """Тест: пустой response_id вызывает ошибку"""
        with pytest.raises(ValueError, match="response_id cannot be empty"):
            GetResponseByIdQuery(response_id="")