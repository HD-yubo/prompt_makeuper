# prompt makeuper Service

A FastAPI-based service that enhances user-provided prompts using LLM-powered analysis and refinement. The service uses a skill-based architecture where predefined `SKILL.md` files guide the optimization process.

## Architecture

```
User Input → Skill Selection → Skill Application → Optimized Prompt
                (LLM)                (Template)
```

## Features

- **8 Predefined Skills**: Stored as standard `SKILL.md` files for easier interoperability
- **Intelligent LLM-Powered Skill Selection**: Automatically chooses the best optimization strategy
- **Two-Round Optimization Process**: Fast and efficient (skill selection + single application)
- **Progressive Skill Loading**: Index frontmatter at startup, lazy-load full skill content on demand
- **Comprehensive LLM Interaction Logging**: Debug and analyze all LLM interactions
- **OpenAI-Compatible**: Works with OpenAI, Azure OpenAI, Ollama, LM Studio, and more
- **FastAPI Best Practices**: Async/await, Pydantic validation, clean architecture
- **Chrome Extension**: Browser integration for seamless prompt optimization

## Installation

1. Clone the repository:
```bash
cd prompt_makeuper
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API key and settings
```

## Configuration

Edit `.env` with your settings:

```bash
# API Server Configuration
API_HOST=0.0.0.0      # Host to bind to
API_PORT=8000         # Port to listen on

# LLM Configuration
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# Optimization Settings
TEMPERATURE=0.7

# Logging Configuration
LOG_DIR=logs          # Log directory
ENABLE_LOGGING=true   # Enable/disable logging
LOG_LEVEL=INFO        # Log level (DEBUG, INFO, WARNING, ERROR)
```

### LLM Provider Examples

The service supports any OpenAI-compatible API endpoint. Here are examples for different providers:

#### OpenAI (Default)
```bash
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

#### Azure OpenAI
```bash
OPENAI_BASE_URL=https://your-resource.openai.azure.com/openai/deployments/your-deployment
OPENAI_API_KEY=your-azure-api-key
OPENAI_MODEL=gpt-4
```

#### Ollama (Local Models)
```bash
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama  # Required but not used by Ollama
OPENAI_MODEL=llama2
```

#### LM Studio (Local Models)
```bash
OPENAI_BASE_URL=http://localhost:1234/v1
OPENAI_API_KEY=lm-studio  # Required but not used
OPENAI_MODEL=local-model
```

#### vLLM (Local/Cloud)
```bash
OPENAI_BASE_URL=http://localhost:8000/v1
OPENAI_API_KEY=empty
OPENAI_MODEL=meta-llama/Llama-2-7b
```

#### Together AI
```bash
OPENAI_BASE_URL=https://api.together.xyz/v1
OPENAI_API_KEY=your-together-api-key
OPENAI_MODEL=mistralai/Mixtral-8x7B-Instruct-v0.1
```

#### Anthropic (via OpenAI-compatible proxy)
```bash
# Use a proxy like Anthropic's Bedrock integration or third-party
OPENAI_BASE_URL=https://your-proxy.example.com/v1
OPENAI_API_KEY=your-proxy-key
OPENAI_MODEL=claude-3-opus
```

## Running the Service

Start the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## Command Line Usage

Run prompt optimization without starting the HTTP service:

```bash
python -m app.cli "写一个关于AI的文章"
python -m app.cli "写一个关于AI的文章" --output-type xml
python -m app.cli "写一个关于AI的文章" --skill structure
python -m app.cli --list-skills
python -m app.cli --file prompt.txt
cat prompt.txt | python -m app.cli
python -m app.cli "写一个关于AI的文章" --json
```

Short wrapper command:

```bash
./prompt-makeuper "写一个关于AI的文章"
./prompt-makeuper --list-skills
```

CLI defaults to printing only the optimized prompt. Use `--json` to print the full result payload.
Use `--skill <name>` to bypass automatic skill selection and force a specific skill.
Use `--list-skills` to print all available skills and exit.

## API Endpoints

### POST /makeup_prompt
Optimize a prompt using LLM-powered skill selection and refinement.

**Request:**
```json
{
  "input_prompt": "write code"
}
```

**Response:**
```json
{
  "output_prompt": "Write a Python function that...",
  "skill_used": "specificity",
  "iterations": 1
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

### GET /skills
List available optimization skills.

**Response:**
```json
{
  "skills": ["clarity", "specificity", "structure", "examples", "constraints", "mental_model", "progressive", "self_verify"]
}
```

## Testing

Run tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app tests/
```

## Project Structure

```
prompt_makeuper/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   ├── services/
│   │   ├── llm_client.py       # OpenAI client
│   │   ├── skill_manager.py    # Skill indexing and lazy loading
│   │   ├── skill_parser.py     # SKILL.md parser
│   │   ├── embedding_selector.py # Embedding-based skill selection
│   │   └── optimizer.py        # Optimization pipeline
│   └── skills/
│       ├── clarity/
│       │   └── SKILL.md
│       └── ...                 # One directory per skill
├── docs/                       # Documentation
│   ├── QUICKSTART.md           # Quick start guide
│   ├── makeup_prompt_api_documentation.md  # API documentation
│   └── EMBEDDING_SELECTOR_REPORT.md        # Embedding selector report
├── examples/                   # Example scripts
│   └── demo_embedding_selector.py          # Embedding selector demo
├── tests/                      # Test suite
├── extensions/                 # Chrome extension
├── requirements.txt
├── .env.example
└── README.md
```

## Skills

### Foundation Skills

| Skill | Description | Best For |
|-------|-------------|----------|
| **clarity** | Remove ambiguity and reorganize for logical flow | Unclear or confusing prompts |
| **specificity** | Add details, constraints, and context | Vague or generic requests |
| **structure** | Organize with clear sections and formatting | Disorganized prompts |

### Intermediate Skills

| Skill | Description | Best For |
|-------|-------------|----------|
| **examples** | Include relevant examples to clarify expectations | Prompts requiring specific output formats |
| **constraints** | Define output format and boundaries | Open-ended tasks needing focus |

### Advanced Skills

| Skill | Description | Best For |
|-------|-------------|----------|
| **mental_model** | Surface implicit goals and align mental models | Complex multi-step tasks |
| **self_verify** | Add verification checkpoints and error handling | Critical outputs requiring validation |
| **progressive** | Break complex prompts into progressive steps | Large-scale multi-stage projects |

## LLM Interaction Logging

The service automatically logs all LLM interactions for debugging and analysis.

### Log Format

Logs are stored as JSON in `logs/YYYYMMDD.log`:

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

### Configuration

```bash
# .env
ENABLE_LOGGING=true    # Enable/disable logging
LOG_DIR=logs          # Log directory
LOG_LEVEL=INFO        # Log level (DEBUG, INFO, WARNING, ERROR)
```

### Viewing Logs

```bash
# View today's logs
cat logs/$(date +%Y%m%d).log | jq

# Search for specific skill
cat logs/20260302.log | jq 'select(.metadata.skill_name == "clarity")'

# Count skill usage
cat logs/*.log | jq -r '.metadata.skill_name' | sort | uniq -c
```

## Documentation

- **[Quick Start Guide](./docs/QUICKSTART.md)** - Get up and running in 3 steps
- **[API Documentation](./docs/makeup_prompt_api_documentation.md)** - Complete API reference and architecture
- **[Embedding Selector Report](./docs/EMBEDDING_SELECTOR_REPORT.md)** - Implementation details and performance analysis

## Examples

Run the embedding selector demo:
```bash
# Demo embedding-based skill selection
python3 examples/demo_embedding_selector.py

# Test caching functionality
python3 examples/demo_embedding_selector.py --cache
```

## Usage Examples

### Example 1: Clarifying a Vague Request

**Input:** "write code"

**Output with clarity skill:**
```markdown
## Task
Write a Python script

## Requirements
- Purpose: [specify what the code should do]
- Language: Python 3.9+
- Output: Console application
- Error handling: Include basic error handling
```

### Example 2: Adding Specificity

**Input:** "make a website"

**Output with specificity skill:**
```markdown
## Project: Web Application Development

## Context
Create a [type of website] for [target audience]

## Technical Requirements
- Framework: [React/Vue/Plain HTML]
- Styling: [CSS framework of choice]
- Backend: [API requirements]
- Database: [if needed]

## Features
1. [Feature 1]
2. [Feature 2]
3. [Feature 3]
```

### Example 3: Adding Mental Model Alignment

**Input:** "fix the bug"

**Output with mental_model skill:**
```markdown
## Intent
**Diagnose and resolve** the software issue affecting [specific functionality]

## Assumptions
- The bug is reproducible
- Access to error logs and stack traces is available
- Testing environment is set up
- Root cause is within the application code (not external dependencies)

## Success Criteria
- Bug is fixed without introducing new issues
- Fix is tested and verified
- Documentation is updated if needed
- Code review is completed
```

## License

MIT
