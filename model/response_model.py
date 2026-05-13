from pydantic import BaseModel
from typing import Optional


class AuthorizationResponse(BaseModel):

    allowed: bool

    intent: Optional[str] = None

    form: Optional[str] = None

    message: Optional[str] = None
