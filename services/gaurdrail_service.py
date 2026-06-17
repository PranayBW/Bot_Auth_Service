import json

from auth_service.utils.ollama_client import (
    chat_json
)

from auth_service.model.gaurdrail_models import GuardrailResponse

def build_capability_context(capabilities):

    return "\n".join(
        [
            f"{cap['service_code']} : {cap['description']}"
            for cap in capabilities
        ]
    )


class GuardrailService:

    def __init__(
        self,
        capability_service
    ):
        self.capability_service = capability_service

    async def discover_capability(
        self,
        query: str,
        org_id: int
    ) -> GuardrailResponse:

        try:

            capabilities = (
                await self.capability_service
                .get_org_capabilities(org_id)
            )

            if not capabilities:

                return GuardrailResponse(
                    classification="OUT_OF_SCOPE",
                    capability=None,
                    confidence=0.0,
                    message="No capabilities configured for organization",
                    available_capabilities=[]
                )
            print("GUARDRAIL CAPABILITIES:", capabilities)
            capability_context = build_capability_context(
                capabilities
            )

            system_prompt = f"""
You are an HR service classifier.

Available Services:

{capability_context}

Classification Rules:

1. If the query clearly belongs to exactly one available service:
   classification = ALLOWED

2. If the query is related to HR or talent management activities but the target service is unclear:
   classification = NEEDS_CLARIFICATION

3. If the query is unrelated to HR, recruitment, hiring, candidate management, interview management, onboarding, workforce management, or talent management activities:
   classification = OUT_OF_SCOPE

Return ONLY valid JSON.

Allowed Response Formats:

{{
    "classification": "ALLOWED",
    "capability": "<service_code>"
}}

{{
    "classification": "NEEDS_CLARIFICATION",
    "capability": null
}}

{{
    "classification": "OUT_OF_SCOPE",
    "capability": null
}}

Do not return explanations.
Do not return markdown.
Do not return additional text.
Return JSON only.
"""

            data = await chat_json(
                system_prompt=system_prompt,
                user_prompt=query
            )

            print("GUARDRAIL RAW RESPONSE:", data)

            content = (
                data.get("message", {})
                .get("content", "{}")
            )

            result = json.loads(content)

            return GuardrailResponse(
                classification=result.get(
                    "classification",
                    "OUT_OF_SCOPE"
                ),
                capability=result.get(
                    "capability"
                ),
                confidence=float(
                    result.get(
                        "confidence",
                        0.0
                    )
                ),
                available_capabilities=[
                    capability["service_code"]
                    for capability in capabilities
                ]
            )

        except Exception as ex:

            print(
                f"GUARDRAIL ERROR: {ex}"
            )

            return GuardrailResponse(
                classification="OUT_OF_SCOPE",
                capability=None,
                confidence=0.0,
                message=str(ex),
                available_capabilities=[]
            )