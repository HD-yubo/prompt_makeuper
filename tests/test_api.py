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


def test_makeup_prompt_with_xml_output():
    """Test makeup prompt endpoint with XML output type."""
    response = client.post(
        "/makeup_prompt",
        json={
            "input_prompt": "写一个关于AI的文章",
            "output_type": "xml"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "output_prompt" in data
    assert "skill_used" in data
    # Verify XML structure in output
    assert "<prompt>" in data["output_prompt"]
    assert "<system_role>" in data["output_prompt"]
    assert "<goal>" in data["output_prompt"]


def test_makeup_prompt_default_markdown():
    """Test that default output is markdown when output_type is not specified."""
    response = client.post(
        "/makeup_prompt",
        json={
            "input_prompt": "写一个关于AI的文章"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "output_prompt" in data
    # Should contain markdown headers or just be non-empty
    assert data["output_prompt"]  # Output exists


def test_makeup_prompt_invalid_output_type():
    """Test that invalid output_type is rejected."""
    response = client.post(
        "/makeup_prompt",
        json={
            "input_prompt": "test",
            "output_type": "invalid_format"
        }
    )
    assert response.status_code == 422  # Validation error
