import httpx

from auth_service.config.settings import settings


class AgentSelectionError(RuntimeError):
    pass


async def select_agents_by_user_and_intent(
    user_email: str,
    intent: str,
) -> dict:
    """
    Calls MCP server over HTTP to resolve which agent(s) a user can access
    for a given intent.

    Expected MCP response shape (example):
      - {"found": true, "count": 1, "agents": [{"agent_name": "JD_AGENT"}]}
      - {"found": false, "message": "..."}
    """

    url = f"{settings.MCP_BASE_URL.rstrip('/')}/fetch-agents-by-user-and-intent"
    payload = {
        "user_email": user_email,
        "intent": intent,
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload)

            content_type = resp.headers.get("content-type", "")
            if "application/json" in content_type.lower():
                body: object = resp.json()
            else:
                body = resp.text

            if resp.status_code >= 400:
                if isinstance(body, dict) and "detail" in body:
                    raise AgentSelectionError(str(body["detail"]))
                raise AgentSelectionError(str(body))

            if not isinstance(body, dict):
                raise AgentSelectionError("Unexpected MCP response format")

            data = body
    except Exception as ex:
        raise AgentSelectionError(f"MCP agent selection failed: {ex}") from ex

    return data


async def select_primary_agent_by_user_and_intent(
    user_email: str,
    intent: str,
) -> str:
    """
    Convenience wrapper that returns a single agent name.
    Raises AgentSelectionError if none is found.
    """

    data = await select_agents_by_user_and_intent(
        user_email=user_email,
        intent=intent,
    )
    print("MCP Agent Selection Response:", data)
    if not data.get("data").get("found"):
        if "detail" in data and data.get("detail"):
            raise AgentSelectionError(str(data.get("detail")))
        raise AgentSelectionError(str(data.get("message", "No agent found")))

    agents = data.get("data").get("agents") or []
    if not agents:
        raise AgentSelectionError("No agent found")

    first = agents[0]
    if isinstance(first, dict) and "agent_name" in first:
        return str(first["agent_name"])

    if isinstance(first, str):
        return first

    raise AgentSelectionError("Unexpected MCP response format")

