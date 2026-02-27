from app.services.llm_client import LLMClient
from app.services.skill_manager import SkillManager
from app.config import settings


class PromptOptimizer:
    """Main pipeline for prompt optimization."""

    def __init__(self, llm_client: LLMClient, skill_manager: SkillManager):
        """
        Initialize the optimizer.

        Args:
            llm_client: LLM client for making API calls
            skill_manager: Skill manager for loading skills
        """
        self.llm = llm_client
        self.skills = skill_manager

    async def optimize(self, input_prompt: str) -> dict:
        """
        Main optimization pipeline.

        Args:
            input_prompt: The user's original prompt

        Returns:
            Dict with 'prompt', 'skill', and 'iterations'
        """
        # Stage 1: Select skill
        selected_skill_name = await self._select_skill(input_prompt)
        skill = self.skills.get_skill(selected_skill_name)

        # Stage 2: Apply skill (first iteration)
        optimized = await self._apply_skill(input_prompt, skill)

        # Stage 3: Iterative refinement
        iterations = 1
        for i in range(settings.MAX_ITERATIONS - 1):
            # Ask LLM if further improvement is needed
            needs_more = await self._check_quality(optimized)
            if not needs_more:
                break

            # Refine using same skill
            optimized = await self._apply_skill(optimized, skill)
            iterations += 1

        return {
            "prompt": optimized,
            "skill": selected_skill_name,
            "iterations": iterations
        }

    async def _select_skill(self, prompt: str) -> str:
        """
        Let LLM select the best skill for the prompt.

        Args:
            prompt: The user's input prompt

        Returns:
            The selected skill name
        """
        selection_prompt = self.skills.get_skill_selection_prompt(prompt)
        response = await self.llm.chat([
            {"role": "user", "content": selection_prompt}
        ])
        return response.strip().lower()

    async def _apply_skill(self, prompt: str, skill: dict) -> str:
        """
        Apply a skill's optimization template.

        Args:
            prompt: The prompt to optimize
            skill: The skill definition dict

        Returns:
            The optimized prompt
        """
        optimization_prompt = skill["optimization_prompt"].format(
            input_prompt=prompt
        )
        messages = [
            {"role": "system", "content": skill["system_prompt"]},
            {"role": "user", "content": optimization_prompt}
        ]
        return await self.llm.chat(messages)

    async def _check_quality(self, prompt: str) -> bool:
        """
        Check if prompt needs more refinement.

        Args:
            prompt: The current prompt to evaluate

        Returns:
            True if more refinement needed, False otherwise
        """
        check_prompt = f"""Rate this prompt on clarity and specificity (1-10).

Prompt: {prompt}

Respond with ONLY the number."""
        response = await self.llm.chat([
            {"role": "user", "content": check_prompt}
        ])
        try:
            score = int(response.strip())
            return score < 8  # Continue if score below 8
        except:
            return False
