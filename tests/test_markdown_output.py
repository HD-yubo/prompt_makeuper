"""Tests for markdown output format in skill templates."""

import pytest
import re
from pathlib import Path
from app.services.skill_manager import SkillManager


@pytest.fixture
def skill_manager():
    """Create a SkillManager instance."""
    skills_dir = Path("app/skills/templates")
    return SkillManager(skills_dir)


class TestMarkdownOutputFormat:
    """Test suite for markdown format requirements in skill templates."""

    def test_all_templates_have_markdown_requirement(self, skill_manager):
        """Test that all skill templates explicitly require markdown output."""
        skill_names = skill_manager.list_skills()

        for skill_name in skill_names:
            skill = skill_manager.get_skill(skill_name)
            system_prompt = skill["system_prompt"]
            assert "markdown" in system_prompt.lower(), \
                f"Skill '{skill_name}' system_prompt should explicitly mention markdown"

    def test_all_templates_have_format_requirements_section(self, skill_manager):
        """Test that all templates have a 'Format Requirements' section."""
        skill_names = skill_manager.list_skills()

        for skill_name in skill_names:
            skill = skill_manager.get_skill(skill_name)
            system_prompt = skill["system_prompt"]
            assert "format requirements" in system_prompt.lower() or \
                   "format" in system_prompt.lower(), \
                f"Skill '{skill_name}' should have format requirements in system_prompt"

    def test_clarity_template_markdown_elements(self, skill_manager):
        """Test that clarity template specifies appropriate markdown elements."""
        skill = skill_manager.get_skill("clarity")
        system_prompt = skill["system_prompt"]

        # Check for specific markdown elements
        assert "##" in system_prompt or "#" in system_prompt, \
            "Clarity template should mention headers"
        assert "**" in system_prompt, \
            "Clarity template should mention bold text"
        assert "bullet" in system_prompt.lower() or "-" in system_prompt, \
            "Clarity template should mention bullet points"

    def test_structure_template_markdown_elements(self, skill_manager):
        """Test that structure template specifies section headers."""
        skill = skill_manager.get_skill("structure")
        system_prompt = skill["system_prompt"]

        # Structure should emphasize section headers
        assert "##" in system_prompt, \
            "Structure template should mention ## headers for main sections"
        assert "###" in system_prompt, \
            "Structure template should mention ### for subsections"
        assert any(section in system_prompt for section in ["Context", "Task", "Requirements", "Output"]), \
            "Structure template should mention standard section names"

    def test_examples_template_code_blocks(self, skill_manager):
        """Test that examples template specifies code blocks."""
        skill = skill_manager.get_skill("examples")
        system_prompt = skill["system_prompt"]

        # Examples should use code blocks
        assert "```" in system_prompt or "code block" in system_prompt.lower(), \
            "Examples template should require code blocks (```) for examples"
        assert "**" in system_prompt, \
            "Examples template should use bold for labels"

    def test_specificity_template_sections(self, skill_manager):
        """Test that specificity template mentions appropriate sections."""
        skill = skill_manager.get_skill("specificity")
        system_prompt = skill["system_prompt"]

        assert "## Context" in system_prompt or "Context" in system_prompt, \
            "Specificity template should mention Context section"
        assert "## Requirements" in system_prompt or "Requirements" in system_prompt, \
            "Specificity template should mention Requirements section"

    def test_constraints_template_format_specs(self, skill_manager):
        """Test that constraints template mentions output format specifications."""
        skill = skill_manager.get_skill("constraints")
        system_prompt = skill["system_prompt"]

        assert "## Constraints" in system_prompt or "Constraints" in system_prompt, \
            "Constraints template should mention Constraints section"
        assert "**" in system_prompt, \
            "Constraints template should use bold for constraint categories"
        assert "```" in system_prompt or "code block" in system_prompt.lower(), \
            "Constraints template should mention code blocks for format examples"

    def test_all_templates_explicitly_request_markdown(self, skill_manager):
        """Test that all templates explicitly say 'MUST be valid markdown' or similar."""
        skill_names = skill_manager.list_skills()

        for skill_name in skill_names:
            skill = skill_manager.get_skill(skill_name)
            system_prompt = skill["system_prompt"]
            # Check for strong markdown requirement language
            assert any(phrase in system_prompt for phrase in [
                "MUST be valid markdown",
                "must be valid markdown",
                "MUST be in markdown format",
                "must be in markdown format",
                "Output MUST be valid markdown"
            ]), f"Skill '{skill_name}' should explicitly require valid markdown output"

    def test_all_templates_maintain_original_intent(self, skill_manager):
        """Test that all templates include instruction to maintain original intent."""
        skill_names = skill_manager.list_skills()

        for skill_name in skill_names:
            skill = skill_manager.get_skill(skill_name)
            system_prompt = skill["system_prompt"]
            assert "original intent" in system_prompt.lower() or \
                   "maintain" in system_prompt.lower(), \
                f"Skill '{skill_name}' should maintain original intent"

    def test_all_templates_request_no_explanations(self, skill_manager):
        """Test that all templates request output without explanations."""
        skill_names = skill_manager.list_skills()

        for skill_name in skill_names:
            skill = skill_manager.get_skill(skill_name)
            system_prompt = skill["system_prompt"]
            assert "no explanations" in system_prompt.lower() or \
                   "ONLY the" in system_prompt or \
                   "return only" in system_prompt.lower(), \
                f"Skill '{skill_name}' should request output without explanations"


class TestMarkdownOutputValidation:
    """Test suite for validating actual markdown output."""

    def test_output_contains_markdown_elements(self):
        """Test that we can detect markdown elements in output."""
        # This is a utility test showing how to validate markdown

        def has_markdown_elements(text: str) -> bool:
            """Check if text contains common markdown elements."""
            markdown_patterns = [
                r"^#{1,6}\s",  # Headers
                r"\*\*.*?\*\*",  # Bold
                r"\*.*?\*",  # Italic
                r"^-\s",  # Bullet lists
                r"^\d+\.\s",  # Numbered lists
                r"```",  # Code blocks
                r"\[.*?\]\(.*?\)",  # Links
            ]
            return any(re.search(pattern, text, re.MULTILINE) for pattern in markdown_patterns)

        # Test with markdown content
        markdown_text = """## Task

Write a function that:
- **Accepts** a string input
- **Returns** the reversed string

```python
def reverse(s):
    return s[::-1]
```
"""
        assert has_markdown_elements(markdown_text), "Should detect markdown in formatted text"

        # Test with plain text
        plain_text = "Write a function that reverses a string."
        assert not has_markdown_elements(plain_text), "Should not detect markdown in plain text"
