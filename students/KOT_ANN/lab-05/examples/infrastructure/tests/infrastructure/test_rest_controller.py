import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import Mock

from main import app
from application.service.response_application_service import ResponseApplicationService


@pytest.fixture
def mock_service():
    service = Mock(spec=ResponseApplicationService)
    return service


@pytest.fixture
def client(mock_service):
    # Переопределяем зависимость
    app.dependency_overrides[ResponseApplicationService] = lambda: mock_service
    return TestClient(app)


class TestResponseController:

    def test_process_response_returns_accepted(self, client, mock_service):
        """Тест: POST /api/responses возвращает 200"""
        response = client.post("/api/responses", json={
            "response_id": "RESP-123",
            "form_id": "FORM-42",
            "answers": {"name": "Иван"},
            "ip_address": "77.88.55.66",
            "user_agent": "Mozilla/5.0",
            "started_at": "2024-01-01T10:00:00",
            "submitted_at": "2024-01-01T10:02:30"
        })
        
        assert response.status_code == 200
        assert response.json()["status"] == "accepted"
        assert response.json()["response_id"] == "RESP-123"

    def test_get_response_returns_dto(self, client, mock_service):
        """Тест: GET /api/responses/{id} возвращает DTO"""
        mock_service.get_response_by_id.return_value = Mock(
            response_id="RESP-123",
            form_id="FORM-42",
            answers={"name": "Иван"},
            is_suspect=False
        )
        
        response = client.get("/api/responses/RESP-123")
        
        assert response.status_code == 200
        assert response.json()["response_id"] == "RESP-123"

    def test_get_response_not_found_returns_404(self, client, mock_service):
        """Тест: GET несуществующего ответа возвращает 404"""
        mock_service.get_response_by_id.return_value = None
        
        response = client.get("/api/responses/RESP-NOT-FOUND")
        
        assert response.status_code == 404

    def test_get_aggregates_returns_dto(self, client, mock_service):
        """Тест: GET /api/responses/aggregates/{form_id} возвращает агрегаты"""
        mock_service.get_aggregates.return_value = Mock(
            form_id="FORM-42",
            total_responses=100,
            quality_rate=80.0
        )
        
        response = client.get("/api/responses/aggregates/FORM-42")
        
        assert response.status_code == 200
        assert response.json()["form_id"] == "FORM-42"
        assert response.json()["total_responses"] == 100

    def test_list_responses_returns_list(self, client, mock_service):
        """Тест: GET /api/responses возвращает список ответов"""
        mock_service.list_responses_by_form.return_value = [
            Mock(response_id="RESP-1"),
            Mock(response_id="RESP-2")
        ]
        
        response = client.get("/api/responses?form_id=FORM-42")
        
        assert response.status_code == 200
        assert len(response.json()) == 2