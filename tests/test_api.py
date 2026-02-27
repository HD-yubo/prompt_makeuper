import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_skills_endpoint():
    """Test skills listing endpoint."""
    response = client.get("/skills")
    assert response.status_code == 200
    data = response.json()
    assert "skills" in data
    assert isinstance(data["skills"], list)
    expected_skills = ["clarity", "specificity", "structure", "examples", "constraints"]
    assert all(skill in data["skills"] for skill in expected_skills)


def test_makeup_prompt_missing_input():
    """Test makeup prompt endpoint with missing input."""
    response = client.post("/makeup_prompt", json={})
    assert response.status_code == 422  # Validation error
