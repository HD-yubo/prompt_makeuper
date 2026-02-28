# Prompt Makeover Service

A FastAPI-based service that enhances user-provided prompts using LLM-powered analysis and refinement. The service uses a skill-based architecture where predefined prompt patterns guide the optimization process.

## Architecture

```
User Input → Skill Selection → Skill Application → Iterative Refinement → Optimized Prompt
                (LLM)                (Template)              (LLM)
```

## Features

- **5 Predefined Skills**: clarity, specificity, structure, examples, constraints
- **Two-Stage LLM Pipeline**: Select skill → Apply iterative refinement
- **OpenAI-Compatible**: Works with OpenAI, Azure OpenAI, and local models
- **FastAPI Best Practices**: Async/await, Pydantic validation, clean architecture

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
# LLM Configuration
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# Optimization Settings
MAX_ITERATIONS=3
TEMPERATURE=0.7
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
  "iterations": 2
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
  "skills": ["clarity", "specificity", "structure", "examples", "constraints"]
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
│   │   ├── skill_manager.py    # Skill management
│   │   └── optimizer.py        # Optimization pipeline
│   └── skills/
│       └── templates/          # YAML skill definitions
├── tests/                      # Test suite
├── requirements.txt
├── .env.example
└── README.md
```

## Skills

| Skill | Description |
|-------|-------------|
| **clarity** | Remove ambiguity and reorganize for logical flow |
| **specificity** | Add details, constraints, and context |
| **structure** | Organize with clear sections and formatting |
| **examples** | Include relevant examples to clarify expectations |
| **constraints** | Define output format and boundaries |

## License

MIT
