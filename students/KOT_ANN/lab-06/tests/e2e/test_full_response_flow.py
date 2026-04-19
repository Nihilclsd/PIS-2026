import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestFullResponseFlow:
    @pytest.mark.xfail(reason="E2E тест требует настройки DI, будет исправлен в Lab #7")
    def test_full_response_flow(self, client):
        response = client.post("/api/responses", json={
            "response_id": "RESP-E2E-001",
            "form_id": "FORM-E2E",
            "answers": {"name": "Тест", "rating": 5},
            "ip_address": "77.88.55.66",
            "user_agent": "Mozilla/5.0",
            "started_at": "2024-01-01T10:00:00",
            "submitted_at": "2024-01-01T10:02:30"
        })
        assert response.status_code == 200
        assert response.json()["status"] == "accepted"
        assert response.json()["response_id"] == "RESP-E2E-001"

    def test_response_not_found_returns_404(self, client):
        response = client.get("/api/responses/RESP-NOT-EXIST")
        assert response.status_code == 404

    def test_health_check_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"