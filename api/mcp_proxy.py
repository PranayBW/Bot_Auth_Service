from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse

from auth_service.services.agent_tool_map import ToolNotAllowedError
from auth_service.services.mcp_proxy import MCPProxyError, login_via_proxy, request_via_proxy


router = APIRouter()


@router.post("/login")
async def login(
    payload: dict,
    x_agent_name: str = Header(None),
):
    """
    Auth-service route that keeps the same MCP path (/login) but calls MCP internally.

    If no agent context is provided, falls back to SYSTEM agent.
    """

    user_email = payload.get("user_email")
    if not user_email:
        raise HTTPException(status_code=400, detail="user_email missing")

    agent_name = x_agent_name or "SYSTEM"

    try:
        data = await login_via_proxy(user_email=user_email, agent_name=agent_name)
    except ToolNotAllowedError as ex:
        raise HTTPException(status_code=403, detail=str(ex))
    except MCPProxyError as ex:
        raise HTTPException(status_code=502, detail=str(ex))

    return JSONResponse(content=data)


def _agent_name(x_agent_name: str | None) -> str:
    if not x_agent_name:
        raise HTTPException(status_code=400, detail="X-Agent-Name header missing")
    return x_agent_name


@router.get("/departments")
async def departments(
    authorization: str = Header(None),
    x_agent_name: str = Header(None),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        status, body = await request_via_proxy(
            tool_name="get_departments",
            method="GET",
            path="/departments",
            agent_name=_agent_name(x_agent_name),
            headers={"Authorization": authorization},
        )
        return JSONResponse(status_code=status, content=body)
    except ToolNotAllowedError as ex:
        raise HTTPException(status_code=403, detail=str(ex))
    except MCPProxyError as ex:
        raise HTTPException(status_code=502, detail=str(ex))


@router.get("/roles")
async def roles(
    authorization: str = Header(None),
    x_agent_name: str = Header(None),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        status, body = await request_via_proxy(
            tool_name="get_roles",
            method="GET",
            path="/roles",
            agent_name=_agent_name(x_agent_name),
            headers={"Authorization": authorization},
        )
        return JSONResponse(status_code=status, content=body)
    except ToolNotAllowedError as ex:
        raise HTTPException(status_code=403, detail=str(ex))
    except MCPProxyError as ex:
        raise HTTPException(status_code=502, detail=str(ex))


@router.get("/originators")
async def originators(
    authorization: str = Header(None),
    x_agent_name: str = Header(None),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        status, body = await request_via_proxy(
            tool_name="get_originators",
            method="GET",
            path="/originators",
            agent_name=_agent_name(x_agent_name),
            headers={"Authorization": authorization},
        )
        return JSONResponse(status_code=status, content=body)
    except ToolNotAllowedError as ex:
        raise HTTPException(status_code=403, detail=str(ex))
    except MCPProxyError as ex:
        raise HTTPException(status_code=502, detail=str(ex))


@router.get("/reviewers")
async def reviewers(
    authorization: str = Header(None),
    x_agent_name: str = Header(None),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        status, body = await request_via_proxy(
            tool_name="get_reviewers",
            method="GET",
            path="/reviewers",
            agent_name=_agent_name(x_agent_name),
            headers={"Authorization": authorization},
        )
        return JSONResponse(status_code=status, content=body)
    except ToolNotAllowedError as ex:
        raise HTTPException(status_code=403, detail=str(ex))
    except MCPProxyError as ex:
        raise HTTPException(status_code=502, detail=str(ex))


@router.get("/approvers")
async def approvers(
    authorization: str = Header(None),
    x_agent_name: str = Header(None),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        status, body = await request_via_proxy(
            tool_name="get_approvers",
            method="GET",
            path="/approvers",
            agent_name=_agent_name(x_agent_name),
            headers={"Authorization": authorization},
        )
        return JSONResponse(status_code=status, content=body)
    except ToolNotAllowedError as ex:
        raise HTTPException(status_code=403, detail=str(ex))
    except MCPProxyError as ex:
        raise HTTPException(status_code=502, detail=str(ex))


@router.get("/agents")
async def agents(
    user_email: str,
    intent: str,
    authorization: str = Header(None),
    x_agent_name: str = Header(None),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        status, body = await request_via_proxy(
            tool_name="fetch_agents_by_user_and_intent",
            method="GET",
            path="/agents",
            agent_name=_agent_name(x_agent_name),
            headers={"Authorization": authorization},
            params={"user_email": user_email, "intent": intent},
        )
        return JSONResponse(status_code=status, content=body)
    except ToolNotAllowedError as ex:
        raise HTTPException(status_code=403, detail=str(ex))
    except MCPProxyError as ex:
        raise HTTPException(status_code=502, detail=str(ex))


@router.get("/job-description")
async def job_description(
    role_id: int,
    department_id: int,
    authorization: str = Header(None),
    x_agent_name: str = Header(None),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        status, body = await request_via_proxy(
            tool_name="fetch_jd_by_role_and_department",
            method="GET",
            path="/job-description",
            agent_name=_agent_name(x_agent_name),
            headers={"Authorization": authorization},
            params={"role_id": role_id, "department_id": department_id},
        )
        return JSONResponse(status_code=status, content=body)
    except ToolNotAllowedError as ex:
        raise HTTPException(status_code=403, detail=str(ex))
    except MCPProxyError as ex:
        raise HTTPException(status_code=502, detail=str(ex))


@router.post("/workflow-payload")
async def workflow_payload(
    payload: dict,
    authorization: str = Header(None),
    x_agent_name: str = Header(None),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        status, body = await request_via_proxy(
            tool_name="create_workflow_payload",
            method="POST",
            path="/workflow-payload",
            agent_name=_agent_name(x_agent_name),
            headers={"Authorization": authorization},
            json=payload,
        )
        return JSONResponse(status_code=status, content=body)
    except ToolNotAllowedError as ex:
        raise HTTPException(status_code=403, detail=str(ex))
    except MCPProxyError as ex:
        raise HTTPException(status_code=502, detail=str(ex))


@router.post("/trigger-jd-workflow")
async def trigger_jd_workflow(
    payload: dict,
    authorization: str = Header(None),
    x_agent_name: str = Header(None),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        status, body = await request_via_proxy(
            tool_name="trigger_jd_workflow",
            method="POST",
            path="/trigger-jd-workflow",
            agent_name=_agent_name(x_agent_name),
            headers={"Authorization": authorization},
            json=payload,
        )
        return JSONResponse(status_code=status, content=body)
    except ToolNotAllowedError as ex:
        raise HTTPException(status_code=403, detail=str(ex))
    except MCPProxyError as ex:
        raise HTTPException(status_code=502, detail=str(ex))


@router.post("/save-generated-jd")
async def save_generated_jd(
    payload: dict,
    authorization: str = Header(None),
    x_agent_name: str = Header(None),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        status, body = await request_via_proxy(
            tool_name="save_generated_jd",
            method="POST",
            path="/save-generated-jd",
            agent_name=_agent_name(x_agent_name),
            headers={"Authorization": authorization},
            json=payload,
        )
        return JSONResponse(status_code=status, content=body)
    except ToolNotAllowedError as ex:
        raise HTTPException(status_code=403, detail=str(ex))
    except MCPProxyError as ex:
        raise HTTPException(status_code=502, detail=str(ex))


@router.post("/update-generated-jd")
async def update_generated_jd(
    jd_id: int,
    payload: dict,
    authorization: str = Header(None),
    x_agent_name: str = Header(None),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        status, body = await request_via_proxy(
            tool_name="update_generated_jd",
            method="POST",
            path="/update-generated-jd",
            agent_name=_agent_name(x_agent_name),
            headers={"Authorization": authorization},
            params={"jd_id": jd_id},
            json=payload,
        )
        return JSONResponse(status_code=status, content=body)
    except ToolNotAllowedError as ex:
        raise HTTPException(status_code=403, detail=str(ex))
    except MCPProxyError as ex:
        raise HTTPException(status_code=502, detail=str(ex))

