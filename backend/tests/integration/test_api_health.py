"""Integration tests for API health endpoints."""


def test_health_check(client):
    """Health check endpoint should return healthy status."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "app" in data
    assert "version" in data


def test_api_docs_available_in_debug(client):
    """API docs should be available in debug mode."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema_available(client):
    """OpenAPI schema should be available."""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    data = response.json()
    assert "openapi" in data
    assert "paths" in data
