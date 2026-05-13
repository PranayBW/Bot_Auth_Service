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
            resp.raise_for_status()
            data = resp.json()
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

    if not data.get("found"):
        raise AgentSelectionError(data.get("message", "No agent found"))

    agents = data.get("agents") or []
    if not agents:
        raise AgentSelectionError("No agent found")

    first = agents[0]
    if isinstance(first, dict) and "agent_name" in first:
        return str(first["agent_name"])

    if isinstance(first, str):
        return first

    raise AgentSelectionError("Unexpected MCP response format")

