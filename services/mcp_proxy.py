import httpx

from auth_service.config.settings import settings


DEFAULT_TIMEOUT_S = 15


class MCPProxyError(RuntimeError):
    pass


class MCPProxyHTTPError(RuntimeError):
    def __init__(self, status_code: int, detail: object):
        super().__init__(str(detail))
        self.status_code = int(status_code)
        self.detail = detail


async def request_via_proxy(
    *,
    tool_name: str,
    method: str,
    path: str,
    headers: dict[str, str] | None = None,
    params: dict[str, str | int | float | bool | None] | None = None,
    json: object | None = None,
) -> tuple[int, object]:
    """
    Returns: (status_code, parsed_json_or_text)
    """

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


async def login_via_proxy(*, user_email: str) -> dict:
    """
    Proxy for MCP /login.
    """

    status, body = await request_via_proxy(
        tool_name="login",
        method="POST",
        path="/login",
        json={"user_email": user_email},
    )
    print("MCP Proxy Login Response:", status, body)
    if status >= 400:
        detail: object = body
        if isinstance(body, dict) and "detail" in body:
            detail = body["detail"]
        raise MCPProxyHTTPError(status, detail)
    if not isinstance(body, dict):
        raise MCPProxyError("MCP login failed: invalid response")
    return body

async def get_semantic_jd_suggestion(
    query: str,
    token: str
):

    url = (
        f"{settings.MCP_BASE_URL}"
        "/semantic-jd-suggestion"
    )

    headers = {

        "Authorization": token
    }

    payload = {

        "query": query
    }

    async with httpx.AsyncClient(
        timeout=30
    ) as client:

        response = await client.post(

            url,

            json=payload,

            headers=headers
        )

        response.raise_for_status()

        return response.json()

async def query_role_department(
    *,
    prompt: str,
    intent: str,
    token: str
):
    """
    Proxy for MCP /query endpoint.
    """

    url = (
        f"{settings.MCP_BASE_URL}"
        "/query"
    )

    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "intent": intent
    }

    async with httpx.AsyncClient(
        timeout=30
    ) as client:

        response = await client.post(
            url,
            json=payload,
            headers=headers
        )

        response.raise_for_status()

        return response.json()