"""LLM interaction logging service with async file I/O."""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from functools import wraps
from typing import Any, Optional
import logging

from app.config import settings


class LLMLogger:
    """Async logger for LLM interactions with daily file rotation."""

    def __init__(self, log_dir: str = None, enabled: bool = None):
        """
        Initialize the LLM logger.

        Args:
            log_dir: Directory for log files (defaults to settings.LOG_DIR)
            enabled: Whether logging is enabled (defaults to settings.ENABLE_LOGGING)
        """
        self.log_dir = Path(log_dir or settings.LOG_DIR)
        self.enabled = enabled if enabled is not None else settings.ENABLE_LOGGING

        if self.enabled:
            self.log_dir.mkdir(parents=True, exist_ok=True)

    def _get_log_file_path(self) -> Path:
        """Get the log file path for today (YYYYMMDD.log)."""
        today = datetime.now().strftime("%Y%m%d")
        return self.log_dir / f"{today}.log"

    def _format_log_entry(
        self,
        messages: list,
        response: str,
        stage: Optional[str] = None,
        skill_name: Optional[str] = None,
        iteration: Optional[int] = None
    ) -> str:
        """
        Format a log entry with timestamp and metadata.

        Args:
            messages: Input messages sent to LLM
            response: Response received from LLM
            stage: Pipeline stage (skill_selection, skill_application, quality_check)
            skill_name: Name of skill being applied
            iteration: Iteration number for refinement loops

        Returns:
            Formatted log entry as string
        """
        timestamp = datetime.now().isoformat()

        entry = {
            "timestamp": timestamp,
            "stage": stage,
            "metadata": {
                "skill_name": skill_name,
                "iteration": iteration
            },
            "input": messages,
            "output": response
        }

        # Remove None values from metadata
        entry["metadata"] = {k: v for k, v in entry["metadata"].items() if v is not None}

        return json.dumps(entry, ensure_ascii=False)

    async def log_interaction(
        self,
        messages: list,
        response: str,
        stage: Optional[str] = None,
        skill_name: Optional[str] = None,
        iteration: Optional[int] = None
    ) -> None:
        """
        Asynchronously log an LLM interaction to today's log file.

        Args:
            messages: Input messages sent to LLM
            response: Response received from LLM
            stage: Pipeline stage identifier
            skill_name: Name of skill being applied
            iteration: Iteration number for refinement loops
        """
        if not self.enabled:
            return

        try:
            log_entry = self._format_log_entry(
                messages, response, stage, skill_name, iteration
            )
            log_file = self._get_log_file_path()

            # Async file write
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: log_file.open("a", encoding="utf-8").write(log_entry + "\n")
            )
        except Exception as e:
            # Don't let logging errors break the application
            logging.warning(f"Failed to write LLM log: {e}")


def log_llm_interaction(func):
    """
    Decorator to log LLM interactions.

    Extracts context parameters (stage, skill_name, iteration) before
    calling the wrapped function, then logs the interaction.

    Usage:
        @log_llm_interaction
        async def chat(self, messages, stage=None, skill_name=None, iteration=None, **kwargs):
            ...
    """
    @wraps(func)
    async def wrapper(self, messages, *args, **kwargs):
        # Extract context parameters before they're consumed
        stage = kwargs.pop("stage", None)
        skill_name = kwargs.pop("skill_name", None)
        iteration = kwargs.pop("iteration", None)

        # Call the original function
        response = await func(self, messages, *args, **kwargs)

        # Log the interaction
        logger = LLMLogger()
        await logger.log_interaction(
            messages=messages,
            response=response,
            stage=stage,
            skill_name=skill_name,
            iteration=iteration
        )

        return response

    return wrapper
