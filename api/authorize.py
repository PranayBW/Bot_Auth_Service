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
from auth_service.services.agent_selector import (
    AgentSelectionError,
    select_primary_agent_by_user_and_intent,
)
from auth_service.services.agent_tool_map import (
    ToolNotAllowedError,
)
from auth_service.services.mcp_proxy import (
    MCPProxyError,
    login_via_proxy,
)
from auth_service.memory.store import (
    create_prompt,
    create_run,
    finish_run,
    get_or_create_conversation,
)
from auth_service.services.mcp_proxy import (
    get_semantic_jd_suggestion,
)


router = APIRouter()

INTENT_FORM_MAP = {
    "JD_CREATE": "JD_CREAT_FORM",
    "JD_FETCH": "JD_FETCH_FORM",
    "UNKOWN_INTENT": "JD_MENU",
}


@router.post(
    "/bot/jd/eligibility",
    response_model=AuthorizationResponse,
)
async def authorize_intent(
    req: AuthorizationRequest,
    authorization: str = Header(None),
    x_forwarded_authorization: str = Header(None),
    x_microsoft_appid: str = Header(None),
):
    # ------------------------------------------------
    # LOCAL TESTING BYPASS
    # ------------------------------------------------
    if settings.BYPASS_AUTH:
        # Skip all token/header validation for local testing
        # (Optionally you can still sanity-check req.userId here)
        print(req)
        intent = detect_intent(req.text)
        print("DETECTED INTENT:", intent)
        if not intent:
            return AuthorizationResponse(allowed=False, message="Unknown intent")

        user_email = getattr(req, "email", None) or getattr(req, "userEmail", None)
        print(user_email)
        if not user_email:
            return AuthorizationResponse(allowed=False, intent=intent, message="user_email missing")

        if intent == "UNKOWN_INTENT":
            return AuthorizationResponse(
                allowed=True,
                intent=intent,
                form=INTENT_FORM_MAP.get(intent, "JD_MENU"),
                message="OK",
            )

        try:
            agent_name = await select_primary_agent_by_user_and_intent(
                user_email=user_email,
                intent=intent,
            )
            print("SELECTED AGENT:", agent_name)

            mcp_data = await login_via_proxy(user_email=user_email, agent_name=agent_name)
            print("MCP PROXY LOGIN DATA:", mcp_data)
            access_token = mcp_data.get("access_token")
            final_response = {
                "allowed": True,
                "intent": intent,
                "form": INTENT_FORM_MAP.get(intent),
                "message": "OK",
                "agent": agent_name,
            }

            # =========================================================
            # SEMANTIC PREFILL FOR FETCH
            # =========================================================
            if intent == "JD_FETCH":
                try:
                    # -------------------------------------------------
                    # CALL MCP SERVER FOR SEMANTIC SUGGESTION
                    # -------------------------------------------------
                    semantic_result = await get_semantic_jd_suggestion(
                        query=req.text,
                        token=access_token,
                    )

                    print(
                        "SEMANTIC SUGGESTION RESULT:",
                        semantic_result
                    )

                    # -------------------------------------------------
                    # ADD PREFILL DATA
                    # -------------------------------------------------
                    final_response["semantic_prefill"] = {
                        "enabled": semantic_result.get(
                            "found",
                            False
                        ),
                        "role": semantic_result.get(
                            "suggested_role"
                        ),
                        "department": semantic_result.get(
                            "suggested_department"
                        ),
                        "jd_id": semantic_result.get(
                            "jd_id"
                        )
                    }
                except Exception as e:
                    print(
                        "Semantic Prefill Error:",
                        str(e)
                    )

                    final_response["semantic_prefill"] = {
                        "enabled": False
                    }

            # =========================================================
            # RETURN RESPONSE
            # =========================================================
            return final_response

        except (AgentSelectionError, ToolNotAllowedError, MCPProxyError) as ex:
            return AuthorizationResponse(allowed=False, intent=intent, message=str(ex))


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

    user_email = getattr(req, "email", None) or getattr(req, "userEmail", None)
    if not user_email:
        # alternatively: user_email = aad_payload.get("preferred_username") or aad_payload.get("upn")
        raise HTTPException(status_code=400, detail="user_email missing in request")



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
    # UNKNOWN INTENT: RETURN MENU (NO AGENT REQUIRED)
    # ------------------------------------------------

    if intent == "UNKOWN_INTENT":
        return AuthorizationResponse(
            allowed=True,
            intent=intent,
            form=INTENT_FORM_MAP.get(intent, "JD_MENU"),
            message="OK",
        )

    # ------------------------------------------------
    # RESOLVE AGENT + MCP LOGIN VIA PROXY
    # ------------------------------------------------

    try:
        agent_name = await select_primary_agent_by_user_and_intent(
            user_email=user_email,
            intent=intent,
        )
        print("SELECTED AGENT:", agent_name)
        mcp_data = await login_via_proxy(user_email=user_email, agent_name=agent_name)
    except AgentSelectionError as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except ToolNotAllowedError as ex:
        raise HTTPException(status_code=403, detail=str(ex))
    except MCPProxyError as ex:
        raise HTTPException(status_code=502, detail=str(ex))

    if not mcp_data.get("authenticated", False):
        raise HTTPException(status_code=401, detail="User unauthorized")

    # ------------------------------------------------
    # AGENT MEMORY - START RUN
    # ------------------------------------------------

    conversation_id = await get_or_create_conversation(
        user_key=user_email,
        external_conversation_id=req.conversationId,
        channel_id=req.channelId,
    )
    prompt_id = await create_prompt(
        conversation_id=conversation_id,
        prompt_text=req.text,
    )
    run_id = await create_run(
        conversation_id=conversation_id,
        prompt_id=prompt_id,
        intent=intent,
        agent=agent_name,
    )

    # ------------------------------------------------
    # VALIDATE PERMISSIONS
    # ------------------------------------------------


    # ------------------------------------------------
    # SUCCESS
    # ------------------------------------------------

    await finish_run(run_id=run_id, status="succeeded")

    final_response = {

    "allowed": True,

    "intent": intent,

    "form": INTENT_FORM_MAP.get(intent),

    "message": "OK",

    "conversation_id": str(conversation_id),

    "prompt_id": str(prompt_id),

    "run_id": str(run_id),

    "agent": agent_name
    }


# =========================================================
# SEMANTIC PREFILL FOR JD_FETCH
# =========================================================
    if intent == "JD_FETCH":

        try:

            access_token = mcp_data.get(
                "access_token"
            )

            semantic_result = await (
                get_semantic_jd_suggestion(

                    query=req.text,

                    token=access_token
                )
            )

            print(
                "SEMANTIC SUGGESTION RESULT:",
                semantic_result
            )

            final_response["semantic_prefill"] = {

                "enabled": semantic_result.get(
                    "found",
                    False
                ),

                "role": semantic_result.get(
                    "suggested_role"
                ),

                "department": semantic_result.get(
                    "suggested_department"
                ),

                "jd_id": semantic_result.get(
                    "jd_id"
                )
            }

        except Exception as e:

            print(
                "Semantic Prefill Error:",
                str(e)
            )

            final_response["semantic_prefill"] = {

                "enabled": False
            }


    # =========================================================
    # RETURN FINAL RESPONSE
    # =========================================================
    return final_response
