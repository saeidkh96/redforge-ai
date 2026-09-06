from fastapi.testclient import TestClient
from redforge.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "service": "redforge-ai",
        "status": "healthy",
        "version": "1.0.0",
    }


def test_ready() -> None:
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {
        "service": "redforge-ai",
        "status": "ready",
        "version": "1.0.0",
    }
