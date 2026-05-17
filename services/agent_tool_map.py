class ToolNotAllowedError(RuntimeError):
    pass


# Tool identifiers are plain strings. Start minimal and expand as more tools are proxied.
AGENT_TOOL_MAP: dict[str, set[str]] = {
    "JD_AGENT": {
        "login",
        "get_departments",
        "get_roles",
        "get_originators",
        "get_reviewers",
        "get_approvers",
        "fetch_agents_by_user_and_intent",
        "fetch_jd_by_role_and_department",
        "create_workflow_payload",
        "trigger_jd_workflow",
        "save_generated_jd",
        "update_generated_jd",
    },
}


def assert_tool_allowed(agent_name: str, tool_name: str) -> None:
    allowed_tools = AGENT_TOOL_MAP.get(agent_name)
    if not allowed_tools:
        raise ToolNotAllowedError(f"No tools configured for agent: {agent_name}")
    if tool_name not in allowed_tools:
        raise ToolNotAllowedError(f"Tool '{tool_name}' not allowed for agent '{agent_name}'")
