import httpx

from auth_service.config.settings import settings
from auth_service.services.agent_tool_map import assert_tool_allowed


DEFAULT_TIMEOUT_S = 15


class MCPProxyError(RuntimeError):
    pass


async def request_via_proxy(
    *,
    tool_name: str,
    method: str,
    path: str,
    agent_name: str,
    headers: dict[str, str] | None = None,
    params: dict[str, str | int | float | bool | None] | None = None,
    json: object | None = None,
) -> tuple[int, object]:
    """
    Agent-aware proxy for MCP REST endpoints.

    Returns: (status_code, parsed_json_or_text)
    """

    assert_tool_allowed(agent_name, tool_name)

    url = f"{settings.MCP_BASE_URL.rstrip('/')}{path}"
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT_S) as client:
            resp = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json,
            )

        content_type = resp.headers.get("content-type", "")
        if "application/json" in content_type.lower():
            body: object = resp.json()
        else:
            body = resp.text

        return resp.status_code, body
    except Exception as ex:
        raise MCPProxyError(f"MCP request failed: {ex}") from ex


async def login_via_proxy(*, user_email: str, agent_name: str) -> dict:
    """
    Agent-aware proxy for MCP /login.

    - Enforces agent->tool policy before calling MCP.
    - Keeps upstream endpoint unchanged (calls MCP_BASE_URL + /login internally).
    """

    status, body = await request_via_proxy(
        tool_name="login",
        method="POST",
        path="/login",
        agent_name=agent_name,
        json={"user_email": user_email},
    )
    if status >= 400:
        raise MCPProxyError(f"MCP login failed: {body}")
    if not isinstance(body, dict):
        raise MCPProxyError("MCP login failed: invalid response")
    return body

