from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Prompt(BaseModel):
    """Model for a user prompt."""
    text: str = Field(..., max_length=300)
    topic: Optional[str] = None
    sub_concepts: Optional[List[str]] = None
    visual_metaphors: Optional[List[str]] = None


class PromptClassification(BaseModel):
    """Model for classified prompt."""
    is_valid: bool
    topic: str
    confidence: float = Field(ge=0.0, le=1.0)
    reason: Optional[str] = None


class PromptResponse(BaseModel):
    """Response model for prompt processing."""
    prompt_id: str
    prompt: Prompt
    classification: PromptClassification
    scene_plan: Optional[Dict[str, Any]] = None