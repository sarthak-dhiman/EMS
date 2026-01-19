from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

def test_404_not_found_formatted():
    response = client.get("/non-existent-route")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error_type"] == "http_error"
    assert "Not Found" in data["message"]

def test_validation_error_formatted():
    # Hit login with missing fields
    response = client.post("/auth/login", data={})
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error_type"] == "validation_error"
    assert "field" in data["details"][0]
    assert "issue" in data["details"][0]

def test_method_not_allowed_formatted():
    # POST to a GET only route
    response = client.post("/")
    assert response.status_code == 405
    data = response.json()
    assert data["success"] is False
    assert data["error_type"] == "http_error"
    assert "Method Not Allowed" in data["message"]
