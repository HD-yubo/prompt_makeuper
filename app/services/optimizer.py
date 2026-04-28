from app.services.llm_client import LLMClient
from app.services.skill_manager import SkillManager
from app.services.embedding_selector import EmbeddingSkillSelector
from app.services.date_filter import replace_dates_with_fuzzy
def detect_language(text: str) -> str:
    """
    Detect language from input text using Unicode ranges.

    Args:
        text: Input text to analyze

    Returns:
        Language code: 'zh', 'ja', 'ko', 'en'
    """
    counts = {"zh": 0, "ja": 0, "ko": 0, "en": 0}

    for char in text:
        code = ord(char)
        if 0x4e00 <= code <= 0x9fff:  # Chinese
            counts["zh"] += 1
        elif 0x3040 <= code <= 0x309f or 0x30a0 <= code <= 0x30ff:  # Japanese
            counts["ja"] += 1
        elif 0xac00 <= code <= 0xd7af:  # Korean
            counts["ko"] += 1
        elif 0x0000 <= code <= 0x007f:  # ASCII (English)
            counts["en"] += 1

    if max(counts.values()) == 0:
        return "en"
    return max(counts, key=counts.get)


def get_language_instruction(language: str) -> str:
    """
    Get output language instruction for the given language.

    Args:
        language: Language code

    Returns:
        Language instruction string
    """
    instructions = {
        "zh": "Output the optimized prompt in Simplified Chinese (简体中文) only.",
        "ja": "Output the optimized prompt in Japanese (日本語) only.",
        "ko": "Output the optimized prompt in Korean (한국어) only.",
        "en": "Output the optimized prompt in the same language as the input."
    }
    return instructions.get(language, instructions["en"])


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
        # Initialize embedding selector for fast skill selection
        self.embedding_selector = EmbeddingSkillSelector(skill_manager)

    async def optimize(
        self,
        input_prompt: str,
        output_type: str = "markdown",
        skill_name: str | None = None,
    ) -> dict:
        """
        Main optimization pipeline.

        Args:
            input_prompt: The user's original prompt
            output_type: Desired output format ('markdown' or 'xml')
            skill_name: Optional skill name to force, skipping auto-selection

        Returns:
            Dict with 'prompt', 'skill', and 'iterations'
        """
        # Stage 1: Select skill
        selected_skill_name = skill_name or await self._select_skill(input_prompt)
        skill = self.skills.get_skill(selected_skill_name)
        if skill is None:
            raise ValueError(f"Unknown skill: {selected_skill_name}")

        # Stage 2: Apply skill with output format
        optimized = await self._apply_skill(input_prompt, skill, output_type)

        # Stage 3: Post-process to remove specific dates
        final_prompt, replacements_count = replace_dates_with_fuzzy(optimized)

        # Log if dates were found and replaced
        if replacements_count > 0:
            print(f"[DateFilter] Replaced {replacements_count} specific date(s) with fuzzy expressions")

        # Return result immediately without quality check iterations
        return {
            "prompt": final_prompt,
            "skill": selected_skill_name,
            "iterations": 1
        }

    async def _select_skill(self, prompt: str) -> str:
        """
        Select the best skill for the prompt using embeddings with LLM fallback.

        Args:
            prompt: The user's input prompt

        Returns:
            The selected skill name
        """
        # Try embedding selector first (fast, no API cost)
        if self.embedding_selector.is_available():
            selected_skill = self.embedding_selector.select_skill(prompt)
            if selected_skill and selected_skill in self.skills.metadata:
                return selected_skill

        # Fallback to LLM selection if embedding selector fails
        selection_prompt = self.skills.get_skill_selection_prompt(prompt)
        response = await self.llm.chat(
            [{"role": "user", "content": selection_prompt}],
            stage="skill_selection"
        )
        return response.strip().lower()

    async def _apply_skill(self, prompt: str, skill, output_type: str = "markdown") -> str:
        """
        Apply a skill's optimization template with specified output format.

        Args:
            prompt: The prompt to optimize
            skill: The skill definition dict
            output_type: Desired output format ('markdown' or 'xml')

        Returns:
            The optimized prompt
        """
        # Detect input language and generate corresponding output instruction
        language = detect_language(prompt)
        language_instruction = get_language_instruction(language)

        # Get format-specific instructions
        from app.services.formatter import get_format_instructions
        format_instruction = get_format_instructions(output_type)

        optimization_prompt = skill.optimization_prompt.format(
            input_prompt=prompt
        )
        messages = [
            {
                "role": "system",
                "content": skill.system_prompt + "\n\n" + format_instruction + "\n\nIMPORTANT: " + language_instruction
            },
            {"role": "user", "content": optimization_prompt}
        ]
        return await self.llm.chat(messages, stage="skill_application", skill_name=skill.name)

    async def _check_quality(self, prompt: str, iteration: int = None) -> bool:
        """
        Check if prompt needs more refinement.

        Args:
            prompt: The current prompt to evaluate
            iteration: Current iteration number for logging

        Returns:
            True if more refinement needed, False otherwise
        """
        check_prompt = f"""Rate this prompt on clarity and specificity (1-10).

Prompt: {prompt}

Respond with ONLY the number."""
        response = await self.llm.chat(
            [{"role": "user", "content": check_prompt}],
            stage="quality_check",
            iteration=iteration
        )
        try:
            score = int(response.strip())
            return score < 8  # Continue if score below 8
        except:
            return False
