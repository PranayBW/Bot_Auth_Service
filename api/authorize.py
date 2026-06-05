from fastapi import (
    APIRouter,
    Header,
    HTTPException
)
from fastapi.responses import JSONResponse
import json
import re

from auth_service.model.request_model import (
    AuthorizationRequest
)

from auth_service.model.response_model import (
    AuthorizationResponse
)

from auth_service.ai.intent_classifier import (
    detect_intent
)
from auth_service.ai.ollama_intent_classifier import (
    detect_intent_with_ollama,
)
from auth_service.ai.intent_registry import (
    UNKNOWN_INTENT,
    get_clear_patterns,
    get_form_for_intent,
    has_domain_signal,
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
    MCPProxyHTTPError,
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

def _should_use_ollama_for_intent(text: str, intent: str) -> bool:
    if not settings.OLLAMA_ENABLED:
        return False

    if intent == UNKNOWN_INTENT:
        return has_domain_signal(text)

    text_lower = text.lower().strip()
    if any(re.search(pattern, text_lower) for pattern in get_clear_patterns()):
        return False

    words = re.findall(r"[a-zA-Z0-9]+", text_lower)

    return len(words) >= 4 and has_domain_signal(text)


async def _detect_intent_with_fallback(text: str) -> str:
    intent = detect_intent(text)

    if _should_use_ollama_for_intent(text, intent):
        ollama_intent = await detect_intent_with_ollama(text)
        if ollama_intent != UNKNOWN_INTENT:
            print("OLLAMA DETECTED INTENT:", ollama_intent)
            return ollama_intent

    return intent


def _unauthorized_payload(*, intent: str | None) -> dict:
    form = get_form_for_intent(intent)
    return {
        "allowed": False,
        "intent": intent,
        "form": form,
        "message": None,
        "conversation_id": None,
        "prompt_id": None,
        "run_id": None,
        "semantic_prefill": {
            "enabled": False,
            "role": None,
            "department": None,
            "jd_id": None,
        },
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
        intent = await _detect_intent_with_fallback(req.text)
        
        print("DETECTED INTENT:", intent)
        if not intent:
            return AuthorizationResponse(allowed=False, message="Unknown intent")

        user_email = getattr(req, "email", None) or getattr(req, "userEmail", None)
        print(user_email)
        if not user_email:
            return AuthorizationResponse(allowed=False, intent=intent, message="user_email missing")

        if intent == UNKNOWN_INTENT:
            return AuthorizationResponse(
                allowed=True,
                intent=intent,
                form=get_form_for_intent(intent),
                message="OK",
            )

        try:
            mcp_data = await login_via_proxy(user_email=user_email)
            print("MCP PROXY LOGIN DATA:", mcp_data)
            if not mcp_data.get("authenticated", False):
                payload = _unauthorized_payload(intent=intent)
                payload["message"] = "User unauthorized"
                return JSONResponse(status_code=401, content=payload)

            agent_name = await select_primary_agent_by_user_and_intent(
                user_email=user_email,
                intent=intent,
            )
            print("SELECTED AGENT:", agent_name)
            access_token = mcp_data.get("access_token")
            final_response = {
                "allowed": True,
                "intent": intent,
                "form": get_form_for_intent(intent),
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

        except AgentSelectionError as ex:
            # Surface MCP-provided message as-is (FastAPI wraps it under {"detail": ...}).
            raise HTTPException(status_code=401, detail=str(ex))
        except MCPProxyHTTPError as ex:
            if ex.status_code == 401:
                payload = _unauthorized_payload(intent=intent)
                payload["message"] = ex.detail
                return JSONResponse(status_code=401, content=payload)
            raise HTTPException(status_code=ex.status_code, detail=ex.detail)
        except MCPProxyError as ex:
            raise HTTPException(status_code=502, detail=str(ex))


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

    intent = await _detect_intent_with_fallback(req.text)

    if not intent:
        return AuthorizationResponse(
            allowed=False,
            message="Unknown intent"
        )

    # ------------------------------------------------
    # UNKNOWN INTENT: RETURN MENU (NO AGENT REQUIRED)
    # ------------------------------------------------

    if intent == UNKNOWN_INTENT:
        return AuthorizationResponse(
            allowed=True,
            intent=intent,
            form=get_form_for_intent(intent),
            message="OK",
        )

    # ------------------------------------------------
    # RESOLVE AGENT + MCP LOGIN VIA PROXY
    # ------------------------------------------------

    try:
        mcp_data = await login_via_proxy(user_email=user_email)
        if (
            not mcp_data.get("success", True)
            or not mcp_data.get("data", {}).get("authenticated", False)
        ):
            payload = _unauthorized_payload(intent=intent)
            payload["message"] = "User unauthorized"
            return JSONResponse(status_code=401, content=payload)

        agent_name = await select_primary_agent_by_user_and_intent(
            user_email=user_email,
            intent=intent,
        )
        print("SELECTED AGENT:", agent_name)
        access_token = mcp_data.get("data", {}).get("access_token")
    except AgentSelectionError as ex:
        payload = _unauthorized_payload(intent=intent)
        payload["message"] = str(ex)
        return JSONResponse(status_code=401, content=payload)
    except ToolNotAllowedError as ex:
        raise HTTPException(status_code=403, detail=str(ex))
    except MCPProxyHTTPError as ex:
        if ex.status_code == 401:
            payload = _unauthorized_payload(intent=intent)
            payload["message"] = ex.detail
            return JSONResponse(status_code=401, content=payload)
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)
    except MCPProxyError as ex:
        raise HTTPException(status_code=502, detail=str(ex))

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
    role_dept_response = await query_role_department(
        prompt=req.text,
        intent=intent, 
        token=access_token
    )

    try:
        role_id = int(role_dept_response.get("role", {}).get("record").get("id"))
        print("ROLE ID:", role_id)
    except (TypeError, ValueError, AttributeError):
        role_id = None
    try:
        department_id = int(role_dept_response.get("department", {}).get("record").get("id"))
        print("DEPARTMENT ID:", department_id)
    except (TypeError, ValueError, AttributeError):
        department_id = None

    await finish_run(run_id=run_id, status="succeeded")

    final_response = {
        "allowed": True,
        "intent": intent,
        "form": get_form_for_intent(intent),
        "message": "OK",
        "conversation_id": str(conversation_id),
        "prompt_id": str(prompt_id),
        "run_id": str(run_id),
        "agent": agent_name
    }

    try:
        jd_exist = await job_description(role_id, department_id, access_token)
        json_jd = json.loads(jd_exist.body)
        if json_jd.get("data", {}).get("found"):
            final_response["job_description"] = json_jd.get("data", {}).get("data")
    except Exception as ex:
        print(f"Error fetching existing job description: {ex}")

    final_response["semantic_prefill"] = role_dept_response

    # =========================================================
    # RETURN FINAL RESPONSE
    # =========================================================
    return final_response
