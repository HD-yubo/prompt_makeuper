from typing import List, Dict, Optional
import yaml
from pathlib import Path


class SkillManager:
    """Manages loading and selection of optimization skills."""

    def __init__(self, skills_dir: Path):
        """
        Initialize the skill manager.

        Args:
            skills_dir: Path to directory containing skill YAML files
        """
        self.skills_dir = skills_dir
        self.skills = self._load_skills()

    def _load_skills(self) -> Dict[str, dict]:
        """Load all skill definitions from YAML files."""
        skills = {}
        for skill_file in self.skills_dir.glob("*.yaml"):
            with open(skill_file, encoding="utf-8") as f:
                skill_data = yaml.safe_load(f)
                skills[skill_data["name"]] = skill_data
        return skills

    def get_skill(self, name: str) -> Optional[dict]:
        """
        Get a specific skill by name.

        Args:
            name: The skill name to retrieve

        Returns:
            Skill dict or None if not found
        """
        return self.skills.get(name)

    def list_skills(self) -> List[str]:
        """
        List all available skill names.

        Returns:
            List of skill names
        """
        return list(self.skills.keys())

    def get_skill_selection_prompt(self, user_prompt: str) -> str:
        """
        Generate prompt for LLM to select appropriate skill.

        Args:
            user_prompt: The user's input prompt to analyze

        Returns:
            A prompt string for skill selection
        """
        skill_descriptions = "\n".join([
            f"- {name}: {skill['description']}"
            for name, skill in self.skills.items()
        ])
        return f"""Analyze the user's prompt and select the most appropriate optimization skill from:

{skill_descriptions}

Respond with ONLY the skill name (e.g., "clarity", "specificity", "structure", "examples", "constraints").
If multiple skills are equally applicable, choose the most critical one.

User prompt: {user_prompt}

Selected skill:"""
