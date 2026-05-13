import httpx

from fastapi import (
    APIRouter,
    Header,
    HTTPException
)

from auth_service.model.request_model import (
    AuthorizationRequest
)

from auth_service.model.response_model import (
    AuthorizationResponse
)

from auth_service.ai.intent_classifier import (
    detect_intent
)

from auth_service.services.permission_service import (
    get_permissions
)

from auth_service.security.aad_validator import (
    validate_aad_token
)

from auth_service.security.microsoft_jwt_validator import (
    validate_microsoft_jwt
)

from auth_service.config.settings import settings


router = APIRouter()

INTENT_FORM_MAP = {
    "JD_CREATE": "JD_CREAT_FORM",
    "JD_FETCH": "JD_FETCH_FORM",
    "UNKOWN_INTENT": "JD_MENU",
}


@router.post(
    "/bot/jd/eligibility",
    response_model=AuthorizationResponse
)
async def authorize_intent(
    req: AuthorizationRequest,
    authorization: str = Header(None),
    x_forwarded_authorization: str = Header(None),
    x_microsoft_appid: str = Header(None)
):
    
    # ------------------------------------------------
    # LOCAL TESTING BYPASS
    # ------------------------------------------------
    if settings.BYPASS_AUTH:
        # Skip all token/header validation for local testing
        # (Optionally you can still sanity-check req.userId here)
        print(req)
        intent = detect_intent(req.text)
        if not intent:
            return AuthorizationResponse(allowed=False, message="Unknown intent")

        user_email = getattr(req, "email", None) or getattr(req, "email", None)
        print(user_email)
        if not user_email:
            return AuthorizationResponse(allowed=False, intent=intent, message="user_email missing")

        # 2) Authenticate user via MCP server (HTTP)
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                mcp_resp = await client.post(
                    f"{settings.MCP_BASE_URL.rstrip('/')}/login",
                    json={"user_email": user_email},
                )
                mcp_resp.raise_for_status()
                mcp_data = mcp_resp.json()
        except Exception as ex:
            return AuthorizationResponse(allowed=False, intent=intent, message=f"MCP auth error: {ex}")

        if not mcp_data.get("authenticated", False):
            return AuthorizationResponse(allowed=False, intent=intent, message="User unauthorized")



        # permissions = get_permissions(req.userId)
        # if intent not in permissions:
        #     return AuthorizationResponse(
        #         allowed=False,
        #         intent=intent,
        #         message="Permission denied",
        #     )

        return AuthorizationResponse(
            allowed=True,
            intent=intent,
            form=INTENT_FORM_MAP.get(intent),
            message="OK",
        )

    # ------------------------------------------------
    # VALIDATE HEADERS
    # ------------------------------------------------

    if not authorization:

        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )

    if not x_forwarded_authorization:

        raise HTTPException(
            status_code=401,
            detail="Microsoft JWT missing"
        )

    # ------------------------------------------------
    # VALIDATE BOT APP ID
    # ------------------------------------------------

    if x_microsoft_appid != settings.BOT_APP_ID:

        raise HTTPException(
            status_code=401,
            detail="Invalid Bot App ID"
        )

    # ------------------------------------------------
    # EXTRACT TOKENS
    # ------------------------------------------------

    aad_token = authorization.replace(
        "Bearer ",
        ""
    )

    microsoft_token = x_forwarded_authorization.replace(
        "Bearer ",
        ""
    )

    # ------------------------------------------------
    # VALIDATE AAD TOKEN
    # ------------------------------------------------

    aad_payload = await validate_aad_token(
        aad_token
    )

    print("AAD TOKEN VALIDATED")

    # ------------------------------------------------
    # AUTHENTICATE USER EMAIL VIA MCP (HTTP)
    # ------------------------------------------------
    user_email = getattr(req, "email", None) or getattr(req, "userEmail", None)
    if not user_email:
        # alternatively: user_email = aad_payload.get("preferred_username") or aad_payload.get("upn")
        raise HTTPException(status_code=400, detail="user_email missing in request")

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            mcp_resp = await client.post(
                f"{settings.MCP_BASE_URL.rstrip('/')}/login",
                json={"user_email": user_email},
            )
    except Exception as ex:
        raise HTTPException(status_code=502, detail=f"MCP server unreachable: {ex}")

    if mcp_resp.status_code != 200:
        raise HTTPException(status_code=401, detail="User unauthorized")

    mcp_data = mcp_resp.json()
    if not mcp_data.get("authenticated", False):
        raise HTTPException(status_code=401, detail="User unauthorized")



    # ------------------------------------------------
    # VALIDATE MICROSOFT JWT
    # ------------------------------------------------

    ms_payload = await validate_microsoft_jwt(
        microsoft_token
    )

    print("MICROSOFT JWT VALIDATED")
    print(ms_payload)

    # ------------------------------------------------
    # DETECT INTENT
    # ------------------------------------------------

    intent = detect_intent(req.text)

    

    if not intent:

        return AuthorizationResponse(
            allowed=False,
            message="Unknown intent"
        )

    # ------------------------------------------------
    # VALIDATE PERMISSIONS
    # ------------------------------------------------


    # ------------------------------------------------
    # SUCCESS
    # ------------------------------------------------

    return AuthorizationResponse(
        allowed=True,
        intent=intent,
        form=INTENT_FORM_MAP.get(intent),
        message="OK"
    )
