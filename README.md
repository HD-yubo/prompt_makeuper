# prompt makeuper

A FastAPI service that optimizes user prompts using LLM-powered skill selection and refinement.

> [中文文档](./README_CN.md)

## How It Works

```
User Prompt -> Flash Model Selects Skill -> Lazy-load Skill Body -> Apply Skill Template -> Optimized Prompt
```

## Quick Start

- 8 predefined skills stored as standard `SKILL.md` files
- Flash-model skill selection with main-model fallback
- Progressive skill loading: index frontmatter at startup, lazy-load full skill content on demand
- OpenAI-compatible endpoints: OpenAI, Azure OpenAI, Ollama, LM Studio, vLLM, and more
- Async FastAPI service with CLI access
- LLM interaction logging for debugging and analysis
- Chrome extension integration

## Installation

```bash
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your API settings, then start the server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Configuration

Key settings in `.env`:

```bash
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# Optional flash model for fast skill selection
# Falls back to OPENAI_* when unset
FLASH_API_KEY=your-flash-api-key-here
FLASH_BASE_URL=https://api.openai.com/v1
FLASH_MODEL=gpt-4o-mini

TEMPERATURE=0.7
ENABLE_LOGGING=true
```

Example local providers:

```bash
# Ollama
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama
OPENAI_MODEL=llama2

# LM Studio
OPENAI_BASE_URL=http://localhost:1234/v1
OPENAI_API_KEY=lm-studio
OPENAI_MODEL=local-model

# vLLM
OPENAI_BASE_URL=http://localhost:8000/v1
OPENAI_API_KEY=empty
OPENAI_MODEL=meta-llama/Llama-2-7b
```

## Command Line Usage

Run prompt optimization without starting the HTTP service:

```bash
python -m app.cli "write code"
python -m app.cli "write code" --output-type xml
python -m app.cli "write code" --skill structure
python -m app.cli --list-skills
python -m app.cli --file prompt.txt
cat prompt.txt | python -m app.cli
python -m app.cli "write code" --json
./prompt-makeuper "write code"
./prompt-makeuper --list-skills
```

CLI defaults to printing only the optimized prompt. Use `--json` to print the full result payload.
Use `--skill <name>` to bypass automatic skill selection and force a specific skill.
Use `--list-skills` or `--help` to inspect available skills with one-line descriptions.

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/makeup_prompt` | Optimize a prompt |
| `GET` | `/skills` | List available skills |
| `GET` | `/health` | Health check |

Example:

```bash
curl -X POST http://localhost:8000/makeup_prompt \
  -H "Content-Type: application/json" \
  -d '{"input_prompt": "write code"}'
```

## Skills

| Skill | Description | Best For |
|-------|-------------|----------|
| **clarity** | Remove ambiguity and reorganize for logical flow | Unclear or confusing prompts |
| **specificity** | Add details, constraints, and context | Vague or generic requests |
| **structure** | Organize with clear sections and formatting | Disorganized prompts |
| **examples** | Include relevant examples to clarify expectations | Prompts requiring specific output formats |
| **constraints** | Define output format and boundaries | Open-ended tasks needing focus |
| **mental_model** | Surface implicit goals and align mental models | Complex multi-step tasks |
| **self_verify** | Add verification checkpoints and error handling | Critical outputs requiring validation |
| **progressive** | Break complex prompts into progressive steps | Large-scale multi-stage projects |

## Project Structure

```
prompt_makeuper/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── cli.py
│   ├── models/
│   ├── services/
│   │   ├── llm_client.py
│   │   ├── skill_manager.py
│   │   ├── skill_parser.py
│   │   └── optimizer.py
│   └── skills/
│       └── <skill>/SKILL.md
├── docs/
├── extensions/
├── tests/
├── prompt-makeuper
├── requirements.txt
├── .env.example
├── README.md
└── README_CN.md
```

## LLM Interaction Logging

The service logs LLM interactions as JSON under `logs/YYYYMMDD.log`.

```json
{
  "timestamp": "2026-03-02T10:30:45.123456",
  "stage": "skill_application",
  "metadata": {
    "skill_name": "clarity",
    "iteration": 1
  },
  "input": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "output": "Optimized prompt text..."
}
```

## Testing

```bash
pytest
pytest --cov=app tests/
```

## Documentation

- [Quick Start Guide](./docs/QUICKSTART.md)
- [API Documentation](./docs/makeup_prompt_api_documentation.md)
- [Embedding Selector Report](./docs/EMBEDDING_SELECTOR_REPORT.md) - historical notes from the previous selector implementation

## License

MIT
