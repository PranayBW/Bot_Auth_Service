from pydantic import BaseModel
from typing import Optional


class AuthorizationRequest(BaseModel):

    userId: str
    aadObjectId: str
    email:str
    displayName:str

    tenantId: Optional[str] = None

    channelId: Optional[str] = None

    conversationId: Optional[str] = None

    serviceUrl: Optional[str] = None

    text: str

