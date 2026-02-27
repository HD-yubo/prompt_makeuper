from openai import AsyncOpenAI
from app.config import settings


class LLMClient:
    """OpenAI-compatible LLM client for async completions."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )

    async def chat(self, messages: list, **kwargs) -> str:
        """
        Simple chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content'
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
