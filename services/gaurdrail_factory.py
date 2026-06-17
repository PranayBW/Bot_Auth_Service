from auth_service.services.capability_service import (
    CapabilityService
)

from auth_service.services.gaurdrail_service import (
    GuardrailService
)

from auth_service.config.database import db


def get_guardrail_service():

    capability_service = (
        CapabilityService()
    )

    return GuardrailService(
        capability_service
    )