"""Integration tests for application entrypoint and general API routes."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data
    assert data["docs"] == "/docs"


def test_root_redirects_to_swagger_docs(client: TestClient) -> None:
    """Test that visiting root '/' redirects to Swagger UI (/docs)."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/docs"


def test_openapi_docs_available(client: TestClient) -> None:
    """Test Swagger docs availability."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "Swagger UI" in response.text
