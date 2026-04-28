# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run CLI mode
python -m app.cli "write code"
python -m app.cli "write code" --skill structure
python -m app.cli --list-skills
./prompt-makeuper "write code"

# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py
pytest tests/test_optimizer.py

# Run tests with coverage
pytest --cov=app tests/

# Install dependencies
pip install -r requirements.txt
```

## Architecture Overview

This is a **skill-based prompt optimization service** where skills are `SKILL.md` files with YAML frontmatter and markdown sections (not hardcoded classes). The architecture follows a two-stage LLM pipeline:

```
User Prompt → LLM selects best skill → Lazy-load skill body → Apply skill template → Optimized Prompt
```

### Key Architectural Patterns

**1. Skills as SKILL.md Files**
Skills are defined in `app/skills/<skill_name>/SKILL.md` with:
- YAML frontmatter containing `name` and `description`
- `## System Prompt` section for the optimization context
- `## Optimization Prompt` section using the `{input_prompt}` placeholder

Adding a new skill means creating a new `SKILL.md` file in its own directory—no code changes needed.

**2. Two-Stage LLM Pipeline**
The `PromptOptimizer` service orchestrates:
- **Stage 1**: LLM selects the most appropriate skill by analyzing the user's prompt against skill descriptions
- **Stage 2**: The selected skill body is loaded on demand and applied to the prompt

**3. Service Layer Dependency Chain**
```
FastAPI (main.py)
    ↓
PromptOptimizer (optimizer.py)
    ↓
SkillManager (skill_manager.py) + LLMClient (llm_client.py)
    ↓
    SKILL.md files + OpenAI API
```

When modifying the optimization pipeline, follow this dependency order:
1. `LLMClient` — Raw API calls (no business logic)
2. `SkillManager` — Skill loading and selection prompts
3. `PromptOptimizer` — Orchestration and iteration logic
4. `main.py` — FastAPI routes only

**4. Configuration via Environment Variables**
All LLM settings are in `.env`:
- `OPENAI_API_KEY`: API credential
- `OPENAI_BASE_URL`: Supports any OpenAI-compatible endpoint (OpenAI, Azure, Ollama, LM Studio, etc.)
- `OPENAI_MODEL`: Model identifier
- `TEMPERATURE`: LLM temperature

Configuration is loaded via `pydantic-settings` in `app/config.py`. The `Settings` class automatically reads from `.env` file—no manual parsing needed.

### Adding New Skills

To add a new optimization skill:

1. Create `app/skills/your_skill/SKILL.md`:
```markdown
---
name: your_skill
description: What this skill improves
---

## System Prompt

You are an expert at...
Return ONLY the rewritten prompt.

## Optimization Prompt

Original prompt: {input_prompt}

Rewrite this prompt to...
```

2. The skill is immediately available—no code changes required. The LLM will automatically consider it during skill selection.

### Testing Patterns

Tests are split by responsibility:
- `tests/test_api.py`: FastAPI endpoint validation (health, skills, request validation)
- `tests/test_optimizer.py`: Service layer logic (SkillManager, skill loading)

When adding new features, add tests to the appropriate file. API tests use FastAPI's `TestClient`; service tests mock or use real `SkillManager` without LLM calls.

### Important Implementation Details

- **Skill selection uses LLM**: The `PromptOptimizer._select_skill()` method asks the LLM to choose the best skill based on skill descriptions. This means prompt quality affects selection accuracy.
- **Quality check threshold**: Iterative refinement stops when the LLM rates the prompt ≥ 8/10 on clarity/specificity. Adjust `_check_quality()` to change this threshold.
- **Error handling**: LLM client failures raise exceptions to FastAPI, which returns 500 Internal Server Error. For production, consider adding retry logic or fallback skills.
- **Async throughout**: All LLM calls and service methods are async. FastAPI runs them in the event loop without blocking.
