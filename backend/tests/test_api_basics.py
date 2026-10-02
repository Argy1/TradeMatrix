from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)


def test_health_reports_degraded_without_a_database() -> None:
    # conftest.py empties DATABASE_URL, so the check must say so instead of pretending.
    response = client.get("/health")
    assert response.status_code == 503
    assert response.json() == {"status": "degraded", "database": "not_configured"}


def test_unknown_route_uses_the_error_shape() -> None:
    response = client.get("/v1/does-not-exist")
    assert response.status_code == 404
    assert response.json() == {"error": {"code": "not_found", "message": "Not Found"}}


def test_cors_allows_only_configured_origins() -> None:
    allowed = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:3000"
    other = client.get("/health", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in other.headers


def test_openapi_schema_is_served() -> None:
    schema = client.get("/openapi.json").json()
    assert schema["info"]["title"] == "TradeMatrix AI API"
    assert "/health" in schema["paths"]
