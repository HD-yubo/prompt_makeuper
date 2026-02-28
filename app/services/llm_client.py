from openai import AsyncOpenAI
from app.config import settings
from app.services.llm_logger import log_llm_interaction


class LLMClient:
    """OpenAI-compatible LLM client for async completions."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )

    @log_llm_interaction
    async def chat(self, messages: list, stage: str = None, skill_name: str = None, iteration: int = None, **kwargs) -> str:
        """
        Simple chat completion with optional logging context.

        Args:
            messages: List of message dicts with 'role' and 'content'
            stage: Pipeline stage for logging (skill_selection, skill_application, quality_check)
            skill_name: Name of skill being applied
            iteration: Iteration number for refinement loops
            **kwargs: Additional arguments for the completion

        Returns:
            The assistant's response content
        """
        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            temperature=settings.TEMPERATURE,
            **kwargs
        )
        return response.choices[0].message.content
