from pydantic import BaseModel


class Capability(BaseModel):

    capability_code: str

    capability_name: str

    business_responsibility: str