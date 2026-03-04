from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.schemas import MakeupRequest, MakeupResponse
from app.services.optimizer import PromptOptimizer
from app.services.llm_client import LLMClient
from app.services.skill_manager import SkillManager
from pathlib import Path

app = FastAPI(
    title="prompt makeuper Service",
    description="LLM-powered prompt optimization with skill-based refinement"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
llm_client = LLMClient()
skill_manager = SkillManager(Path("app/skills/templates"))
optimizer = PromptOptimizer(llm_client, skill_manager)


@app.post("/makeup_prompt", response_model=MakeupResponse)
async def makeup_prompt(request: MakeupRequest) -> MakeupResponse:
    """
    Optimize a prompt using LLM-powered skill selection and refinement.

    This endpoint analyzes the input prompt, selects the most appropriate
    optimization skill, and applies iterative refinement to produce an
    improved version in the specified output format.
    """
    result = await optimizer.optimize(
        request.input_prompt,
        output_type=request.output_type.value
    )
    return MakeupResponse(
        output_prompt=result["prompt"],
        skill_used=result["skill"],
        iterations=result["iterations"]
    )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/skills")
async def list_skills():
    """List available optimization skills."""
    return {"skills": skill_manager.list_skills()}
