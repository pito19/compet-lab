from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_openapi_schema_is_generated():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "/api/competitions" in schema["paths"]
    assert "/api/auth/login" in schema["paths"]


def test_protected_endpoint_requires_authentication():
    response = client.get("/api/competitions")
    assert response.status_code == 401
    # Regression test: 401/403 used to return FastAPI's default
    # {"detail": ...} shape while domain errors (404/409/422) used
    # application/problem+json -- two formats for one API. Both now
    # go through the same StarletteHTTPException handler.
    assert response.headers["content-type"] == "application/problem+json"
    body = response.json()
    assert body["status"] == 401
    assert "detail" in body and "type" in body and "title" in body


def test_unknown_route_returns_problem_json_404():
    response = client.get("/api/this-route-does-not-exist")
    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"
