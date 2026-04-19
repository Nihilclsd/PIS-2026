import pytest
from unittest.mock import patch, Mock
from infrastructure.adapter.out.real_geo_service import RealGeoService


class TestRealGeoService:

    @patch("infrastructure.adapter.out.real_geo_service.requests")
    def test_get_location_success(self, mock_requests):
        """Тест: успешное получение гео-данных"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "country": "Россия",
            "city": "Москва"
        }
        mock_requests.get.return_value = mock_response
        
        service = RealGeoService()
        country, city = service.get_location("77.88.55.66")
        
        assert country == "Россия"
        assert city == "Москва"

    @patch("infrastructure.adapter.out.real_geo_service.requests")
    def test_get_location_timeout_returns_none(self, mock_requests):
        """Тест: таймаут гео-сервиса возвращает None"""
        mock_requests.get.side_effect = TimeoutError()
        
        service = RealGeoService()
        country, city = service.get_location("77.88.55.66")
        
        assert country is None
        assert city is None

    def test_get_location_localhost_returns_none(self):
        """Тест: localhost возвращает None"""
        service = RealGeoService()
        country, city = service.get_location("127.0.0.1")
        
        assert country is None
        assert city is None

    def test_get_location_empty_ip_returns_none(self):
        """Тест: пустой IP возвращает None"""
        service = RealGeoService()
        country, city = service.get_location(None)
        
        assert country is None
        assert city is None