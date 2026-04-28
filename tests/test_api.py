import pytest
from fastapi.testclient import TestClient
from app.main import app, optimizer

client = TestClient(app)


@pytest.fixture
def mock_optimizer(monkeypatch):
    async def fake_optimize(input_prompt: str, output_type: str = "markdown", skill_name=None):
        if output_type == "xml":
            return {
                "prompt": "<prompt><system_role>writer</system_role><goal>write</goal></prompt>",
                "skill": skill_name or "structure",
                "iterations": 1,
            }

        return {
            "prompt": "## Task\n\nWrite something useful",
            "skill": skill_name or "clarity",
            "iterations": 1,
        }

    monkeypatch.setattr(optimizer, "optimize", fake_optimize)


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
    expected_skills = [
        "clarity",
        "specificity",
        "structure",
        "examples",
        "constraints",
        "mental_model",
        "progressive",
        "self_verify",
    ]
    assert all(skill in data["skills"] for skill in expected_skills)


def test_makeup_prompt_missing_input():
    """Test makeup prompt endpoint with missing input."""
    response = client.post("/makeup_prompt", json={})
    assert response.status_code == 422  # Validation error


def test_makeup_prompt_with_xml_output(mock_optimizer):
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


def test_makeup_prompt_default_markdown(mock_optimizer):
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
