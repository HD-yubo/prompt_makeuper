# prompt makeuper

A FastAPI service that automatically transforms vague prompts into high-quality, structured prompts using LLM-powered skill selection and iterative refinement.

> 📖 [中文文档](./README_CN.md)

## How It Works

```
User Input → Skill Selection (Embedding / LLM) → Skill Application (Template) → Optimized Prompt
```

The optimizer runs a two-stage pipeline:

1. **Skill Selection** — Semantic similarity (embedding-based, fast & free) matches the input prompt to the most suitable optimization skill. Falls back to LLM-based selection when embeddings are unavailable.
2. **Skill Application** — The selected skill's prompt template rewrites the input into a well-structured, high-quality prompt.

Additional processing steps:
- **Language detection** — Automatically detects the input language (English, Chinese, Japanese, Korean) and instructs the LLM to respond in the same language.
- **Date filtering** — Replaces specific absolute dates with fuzzy expressions to keep prompts timeless.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API key and settings

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Configuration

Key settings in `.env`:

```bash
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1  # Any OpenAI-compatible endpoint
OPENAI_MODEL=gpt-4o-mini
TEMPERATURE=0.7
MAX_ITERATIONS=3
ENABLE_LOGGING=true
LOG_DIR=logs
LOG_LEVEL=INFO
```

Supports OpenAI, Azure OpenAI, Ollama, LM Studio, vLLM, and any OpenAI-compatible API.

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/makeup_prompt` | Optimize a prompt |
| `GET` | `/skills` | List available skills |
| `GET` | `/health` | Health check |

### Request

```json
{
  "input_prompt": "write code",
  "output_type": "markdown"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `input_prompt` | string | ✅ | The prompt to optimize |
| `output_type` | string | ❌ | Output format: `"markdown"` (default) or `"xml"` |

### Response

```json
{
  "output_prompt": "## Task\nWrite a Python function that...",
  "skill_used": "specificity",
  "iterations": 1
}
```

### Example

```bash
# Markdown output (default)
curl -X POST http://localhost:8000/makeup_prompt \
  -H "Content-Type: application/json" \
  -d '{"input_prompt": "write code"}'

# XML output
curl -X POST http://localhost:8000/makeup_prompt \
  -H "Content-Type: application/json" \
  -d '{"input_prompt": "write code", "output_type": "xml"}'
```

## Skills

Skills are YAML-defined templates located in `app/skills/templates/`. Each skill specializes in a different type of prompt improvement.

| Skill | Best For |
|-------|----------|
| **clarity** | Unclear or ambiguous prompts |
| **specificity** | Vague or generic requests |
| **structure** | Disorganized or scattered prompts |
| **examples** | Prompts needing output format clarification |
| **constraints** | Open-ended tasks that need focused boundaries |
| **mental_model** | Complex multi-step tasks |
| **self_verify** | Critical outputs requiring built-in validation |
| **progressive** | Large-scale multi-stage projects |

### Adding a New Skill

Create a new YAML file in `app/skills/templates/`:

```yaml
name: your_skill
description: What this skill improves

system_prompt: |
  You are an expert at...
  Return ONLY the rewritten prompt.

optimization_prompt: |
  Original prompt: {input_prompt}

  Rewrite this prompt to...
```

No code changes required — the skill is immediately available after restart.

## Multi-Language Support

The service automatically detects the input language and responds in the same language:

| Language | Detection |
|----------|-----------|
| English | ASCII characters |
| Chinese (简体中文) | Unicode range `U+4E00–U+9FFF` |
| Japanese (日本語) | Hiragana / Katakana Unicode ranges |
| Korean (한국어) | Hangul Unicode range |

## Project Structure

```
prompt_makeuper/
├── app/
│   ├── main.py                    # FastAPI application & routes
│   ├── config.py                  # Settings via pydantic-settings
│   ├── models/
│   │   └── schemas.py             # Pydantic request/response models
│   ├── services/
│   │   ├── llm_client.py          # OpenAI-compatible API client
│   │   ├── skill_manager.py       # Skill loading & selection prompts
│   │   ├── optimizer.py           # Two-stage optimization pipeline
│   │   ├── embedding_selector.py  # Embedding-based skill selector
│   │   ├── formatter.py           # Output format instructions
│   │   ├── date_filter.py         # Date fuzzing post-processor
│   │   └── llm_logger.py          # Request/response logging
│   └── skills/
│       └── templates/             # YAML skill definitions (8 built-in)
├── extensions/                    # Chrome extension (side panel UI)
├── examples/                      # Usage examples
├── tests/                         # Pytest test suite
├── requirements.txt
└── .env.example
```

## Chrome Extension

A Chrome side-panel extension is included in `extensions/`. It provides a browser UI to call the backend service directly from any web page.

See [extensions/README.md](./extensions/README.md) for installation and usage instructions.

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## License

MIT
