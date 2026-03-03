import pytest
from app.services.skill_manager import SkillManager
from pathlib import Path


def test_skill_manager_initialization():
    """Test that SkillManager loads all skills."""
    skills_dir = Path("app/skills/templates")
    manager = SkillManager(skills_dir)

    skills = manager.list_skills()
    expected_skills = ["clarity", "specificity", "structure", "examples", "constraints"]

    assert len(skills) >= 5  # At least these core skills exist
    assert all(skill in skills for skill in expected_skills)


def test_skill_manager_get_skill():
    """Test retrieving individual skills."""
    skills_dir = Path("app/skills/templates")
    manager = SkillManager(skills_dir)

    clarity_skill = manager.get_skill("clarity")
    assert clarity_skill is not None
    assert clarity_skill["name"] == "clarity"
    assert "description" in clarity_skill
    assert "system_prompt" in clarity_skill
    assert "optimization_prompt" in clarity_skill


def test_skill_manager_get_nonexistent_skill():
    """Test retrieving a non-existent skill."""
    skills_dir = Path("app/skills/templates")
    manager = SkillManager(skills_dir)

    result = manager.get_skill("nonexistent")
    assert result is None


def test_skill_selection_prompt_generation():
    """Test that skill selection prompt is generated correctly."""
    skills_dir = Path("app/skills/templates")
    manager = SkillManager(skills_dir)

    prompt = manager.get_skill_selection_prompt("write code")
    assert "write code" in prompt
    assert "clarity" in prompt
    assert "specificity" in prompt
