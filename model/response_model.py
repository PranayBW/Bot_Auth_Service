from pydantic import BaseModel
from typing import Optional


class AuthorizationResponse(BaseModel):

    allowed: bool

    intent: Optional[str] = None

    form: Optional[str] = None

    message: Optional[str] = None

    conversation_id: Optional[str] = None

    prompt_id: Optional[str] = None

    run_id: Optional[str] = None

    agent: Optional[str] = None

    semantic_prefill: dict | None = None

    job_description : dict | None = None

class GuardrailResponse(BaseModel):
    allowed: bool
    capability: str | None = None
    confidence: float = 0.0
    reason: str | None = None