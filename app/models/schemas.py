from pydantic import BaseModel, Field


class MakeupRequest(BaseModel):
    """Request model for prompt optimization."""

    input_prompt: str = Field(..., min_length=1, description="The prompt to optimize")


class MakeupResponse(BaseModel):
    """Response model for optimized prompt."""

    output_prompt: str = Field(..., description="The optimized prompt")
    skill_used: str = Field(..., description="Which skill was applied")
    iterations: int = Field(..., description="Number of refinement iterations")
