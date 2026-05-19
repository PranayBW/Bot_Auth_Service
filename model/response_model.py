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
