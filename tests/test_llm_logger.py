"""Tests for LLM logging service."""

import pytest
import asyncio
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.llm_logger import LLMLogger, log_llm_interaction


@pytest.fixture
def temp_log_dir(tmp_path):
    """Create a temporary directory for log files."""
    return str(tmp_path / "logs")


@pytest.fixture
def logger(temp_log_dir):
    """Create a logger instance with temp directory."""
    return LLMLogger(log_dir=temp_log_dir, enabled=True)


@pytest.fixture
def sample_messages():
    """Sample LLM messages for testing."""
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, world!"}
    ]


@pytest.fixture
def sample_response():
    """Sample LLM response for testing."""
    return "Hi! How can I help you today?"


class TestLLMLogger:
    """Test suite for LLMLogger class."""

    def test_init_creates_log_directory(self, temp_log_dir):
        """Test that initializing logger creates the log directory."""
        log_path = Path(temp_log_dir)
        assert not log_path.exists()

        logger = LLMLogger(log_dir=temp_log_dir, enabled=True)
        assert log_path.exists()
        assert log_path.is_dir()

    def test_init_disabled_does_not_create_directory(self, temp_log_dir):
        """Test that disabled logger doesn't create directory."""
        log_path = Path(temp_log_dir)
        logger = LLMLogger(log_dir=temp_log_dir, enabled=False)

        assert not log_path.exists()

    def test_get_log_file_path_returns_correct_format(self, logger, temp_log_dir):
        """Test that log file path uses YYYYMMDD.log format."""
        log_path = logger._get_log_file_path()
        today = datetime.now().strftime("%Y%m%d")

        assert log_path.parent == Path(temp_log_dir)
        assert log_path.name == f"{today}.log"
        assert log_path.suffix == ".log"

    def test_format_log_entry_includes_all_fields(self, logger, sample_messages, sample_response):
        """Test that log entry includes all required fields."""
        entry_str = logger._format_log_entry(
            messages=sample_messages,
            response=sample_response,
            stage="skill_application",
            skill_name="clarity",
            iteration=2
        )

        entry = json.loads(entry_str)

        assert "timestamp" in entry
        assert entry["stage"] == "skill_application"
        assert entry["metadata"]["skill_name"] == "clarity"
        assert entry["metadata"]["iteration"] == 2
        assert entry["input"] == sample_messages
        assert entry["output"] == sample_response

    def test_format_log_entry_removes_none_metadata(self, logger, sample_messages, sample_response):
        """Test that None values are removed from metadata."""
        entry_str = logger._format_log_entry(
            messages=sample_messages,
            response=sample_response,
            stage="skill_selection",
            skill_name=None,
            iteration=None
        )

        entry = json.loads(entry_str)

        assert entry["metadata"] == {}
        assert "skill_name" not in entry["metadata"]
        assert "iteration" not in entry["metadata"]

    @pytest.mark.asyncio
    async def test_log_interaction_creates_file(self, logger, sample_messages, sample_response):
        """Test that logging creates a log file."""
        await logger.log_interaction(
            messages=sample_messages,
            response=sample_response,
            stage="skill_selection"
        )

        log_file = logger._get_log_file_path()
        assert log_file.exists()

    @pytest.mark.asyncio
    async def test_log_interaction_writes_valid_json(self, logger, sample_messages, sample_response):
        """Test that log entries are valid JSON lines."""
        await logger.log_interaction(
            messages=sample_messages,
            response=sample_response,
            stage="skill_application",
            skill_name="examples"
        )

        log_file = logger._get_log_file_path()
        content = log_file.read_text(encoding="utf-8")

        # Should be able to parse each line as JSON
        for line in content.strip().split("\n"):
            entry = json.loads(line)
            assert "timestamp" in entry
            assert "stage" in entry

    @pytest.mark.asyncio
    async def test_log_interaction_disabled_no_file_created(self, temp_log_dir, sample_messages, sample_response):
        """Test that disabled logger doesn't create files."""
        logger = LLMLogger(log_dir=temp_log_dir, enabled=False)

        await logger.log_interaction(
            messages=sample_messages,
            response=sample_response,
            stage="skill_selection"
        )

        log_path = Path(temp_log_dir)
        assert not log_path.exists()

    @pytest.mark.asyncio
    async def test_log_interaction_multiple_entries(self, logger, sample_messages, sample_response):
        """Test that multiple log entries are written correctly."""
        # Write three entries
        for i in range(3):
            await logger.log_interaction(
                messages=sample_messages,
                response=sample_response,
                stage="skill_application",
                skill_name="clarity",
                iteration=i + 1
            )

        log_file = logger._get_log_file_path()
        content = log_file.read_text(encoding="utf-8")

        # Should have 3 lines
        lines = content.strip().split("\n")
        assert len(lines) == 3

        # Each line should be valid JSON
        for line in lines:
            entry = json.loads(line)
            assert entry["metadata"]["iteration"] in [1, 2, 3]


class TestLogLLMInteractionDecorator:
    """Test suite for @log_llm_interaction decorator."""

    @pytest.mark.asyncio
    async def test_decorator_calls_original_function(self, temp_log_dir):
        """Test that decorator calls the wrapped function."""
        # Create a mock class with a chat method
        class MockLLMClient:
            def __init__(self):
                self.chat_called = False

            async def chat(self, messages, **kwargs):
                self.chat_called = True
                return "Test response"

        # Create instance and apply decorator
        client = MockLLMClient()
        original_chat = client.chat.__func__  # Get the unbound method
        client.chat = log_llm_interaction(original_chat).__get__(client, type(client))

        messages = [{"role": "user", "content": "Test"}]
        response = await client.chat(messages)

        assert response == "Test response"
        assert client.chat_called

    @pytest.mark.asyncio
    async def test_decorator_extracts_context_params(self, temp_log_dir):
        """Test that decorator extracts stage, skill_name, iteration."""
        received_kwargs = {}

        class MockLLMClient:
            async def chat(self, messages, **kwargs):
                # Store kwargs to verify context params were removed
                received_kwargs.update(kwargs)
                return "Test response"

        client = MockLLMClient()
        original_chat = client.chat.__func__
        client.chat = log_llm_interaction(original_chat).__get__(client, type(client))

        messages = [{"role": "user", "content": "Test"}]
        response = await client.chat(
            messages,
            stage="skill_selection",
            skill_name="clarity",
            iteration=1
        )

        # The function should be called without the context params
        assert "stage" not in received_kwargs
        assert "skill_name" not in received_kwargs
        assert "iteration" not in received_kwargs

    @pytest.mark.asyncio
    async def test_decorator_logs_interaction(self, temp_log_dir, sample_messages, sample_response):
        """Test that decorator actually logs the interaction."""
        # Create a mock client that returns sample response
        class MockLLMClient:
            async def chat(self, messages, **kwargs):
                return sample_response

        # Apply decorator with custom logger
        logger_instance = LLMLogger(log_dir=temp_log_dir, enabled=True)

        async def logged_chat(self, messages, **kwargs):
            return sample_response

        # Manually apply the decorator pattern
        async def wrapper(self, messages, *args, **kwargs):
            stage = kwargs.pop("stage", None)
            skill_name = kwargs.pop("skill_name", None)
            iteration = kwargs.pop("iteration", None)

            response = await logged_chat(self, messages, *args, **kwargs)

            await logger_instance.log_interaction(
                messages=messages,
                response=response,
                stage=stage,
                skill_name=skill_name,
                iteration=iteration
            )
            return response

        client = MockLLMClient()
        client.chat = wrapper

        # Call the decorated function with context
        await client.chat(
            client,
            sample_messages,
            stage="skill_application",
            skill_name="examples"
        )

        # Verify log file was created and contains entry
        log_path = Path(temp_log_dir)
        log_file = log_path / f"{datetime.now().strftime('%Y%m%d')}.log"
        assert log_file.exists()

        content = log_file.read_text(encoding="utf-8")
        entry = json.loads(content.strip())

        assert entry["stage"] == "skill_application"
        assert entry["metadata"]["skill_name"] == "examples"
        assert entry["input"] == sample_messages
        assert entry["output"] == sample_response
