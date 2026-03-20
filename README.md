# prompt makeuper

A FastAPI service that optimizes user prompts using LLM-powered skill selection and refinement.

> 📖 [中文文档](./README_CN.md)

## How It Works

```
User Input → Skill Selection (LLM) → Skill Application (Template) → Optimized Prompt
```

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
ENABLE_LOGGING=true
```

Supports OpenAI, Azure OpenAI, Ollama, LM Studio, vLLM, and any OpenAI-compatible API.

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/makeup_prompt` | Optimize a prompt |
| `GET` | `/skills` | List available skills |
| `GET` | `/health` | Health check |

**Example:**
```bash
curl -X POST http://localhost:8000/makeup_prompt \
  -H "Content-Type: application/json" \
  -d '{"input_prompt": "write code"}'
```

## Skills

| Skill | Best For |
|-------|----------|
| **clarity** | Unclear or ambiguous prompts |
| **specificity** | Vague or generic requests |
| **structure** | Disorganized prompts |
| **examples** | Prompts needing output format clarification |
| **constraints** | Open-ended tasks needing focus |
| **mental_model** | Complex multi-step tasks |
| **self_verify** | Critical outputs requiring validation |
| **progressive** | Large-scale multi-stage projects |

## Project Structure

```
prompt_makeuper/
├── app/
│   ├── main.py            # FastAPI application
│   ├── config.py          # Configuration
│   ├── models/            # Pydantic schemas
│   └── services/          # LLM client, skill manager, optimizer
│       └── skills/templates/  # YAML skill definitions
├── extensions/            # Chrome extension
├── docs/                  # Additional documentation
├── tests/
└── .env.example
```

## Documentation

- [Quick Start Guide](./docs/QUICKSTART.md)
- [API Documentation](./docs/makeup_prompt_api_documentation.md)

## License

MIT
