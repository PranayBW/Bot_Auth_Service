from pydantic import BaseModel

class GuardrailResponse(BaseModel):
    classification: str
    capability: str | None = None
    confidence: float = 0.0