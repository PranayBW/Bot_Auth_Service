import httpx

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse

from auth_service.config.settings import settings


router = APIRouter()


@router.post("/login")
async def login(
    payload: dict,
):
    """Proxy MCP `/login` without requiring any headers."""
    user_email = payload.get("user_email")
    if not user_email:
        raise HTTPException(status_code=400, detail="user_email missing")

    try:
        url = f"{settings.MCP_BASE_URL.rstrip('/')}/login"
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, json={"user_email": user_email})
        content_type = resp.headers.get("content-type", "")
        body = resp.json() if "application/json" in content_type.lower() else resp.text
        return JSONResponse(status_code=resp.status_code, content=body)
    except Exception as ex:
        raise HTTPException(status_code=502, detail=f"MCP login failed: {ex}")


async def _forward(
    *,
    method: str,
    path: str,
    authorization: str,
    params: dict | None = None,
    json: object | None = None,
) -> JSONResponse:
    url = f"{settings.MCP_BASE_URL.rstrip('/')}{path}"
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.request(
            method=method,
            url=url,
            headers={"Authorization": authorization},
            params=params,
            json=json,
        )
    content_type = resp.headers.get("content-type", "")
    body = resp.json() if "application/json" in content_type.lower() else resp.text
    return JSONResponse(status_code=resp.status_code, content=body)


@router.get("/departments")
async def departments(
    authorization: str = Header(None),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    return await _forward(method="GET", path="/departments", authorization=authorization)


@router.get("/roles")
async def roles(
    authorization: str = Header(None),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    return await _forward(method="GET", path="/roles", authorization=authorization)


@router.get("/originators")
async def originators(
    authorization: str = Header(None),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    return await _forward(method="GET", path="/originators", authorization=authorization)


@router.get("/reviewers")
async def reviewers(
    authorization: str = Header(None),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    return await _forward(method="GET", path="/reviewers", authorization=authorization)


@router.get("/approvers")
async def approvers(
    authorization: str = Header(None),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    return await _forward(method="GET", path="/approvers", authorization=authorization)


@router.get("/agents")
async def agents(
    user_email: str,
    intent: str,
    authorization: str = Header(None),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    return await _forward(
        method="GET",
        path="/agents",
        authorization=authorization,
        params={"user_email": user_email, "intent": intent},
    )


@router.get("/job-description")
async def job_description(
    role_id: int,
    department_id: int,
    authorization: str = Header(None),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    return await _forward(
        method="GET",
        path="/job-description",
        authorization=authorization,
        params={"role_id": role_id, "department_id": department_id},
    )


@router.post("/workflow-payload")
async def workflow_payload(
    payload: dict,
    authorization: str = Header(None),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    async def _forward(
    method: str,
    path: str,
    authorization: str,
    json: dict = None,
    ):
        try:
            url = (

            f"{settings.MCP_BASE_URL}"

            f"{path}"
            )

            timeout = httpx.Timeout(

            timeout=None
            )

            async with httpx.AsyncClient(

            timeout=timeout

            ) as client:

                response = await client.request(

                    method=method,

                    url=url,

                    json=json,

                    headers={

                        "Authorization":
                            authorization,

                        "Content-Type":
                            "application/json"
                    }
                )

        # ---------------------------------------------
        # VALIDATE RESPONSE
        # ---------------------------------------------
            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as e:

            raise HTTPException(

                status_code=e.response.status_code,

                detail=e.response.text
            )

        except Exception as e:

            raise HTTPException(

                status_code=500,

                detail=str(e)
            )


    return await _forward(
        method="POST",
        path="/workflow-payload",
        authorization=authorization,
        json=payload,
    )


@router.post("/trigger-jd-workflow")
async def trigger_jd_workflow(
    payload: dict,
    authorization: str = Header(None),
):
    

    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    async def _forward(
    method: str,
    path: str,
    authorization: str,
    json: dict = None,
    ):
        try:

        # ---------------------------------------------
        # MCP URL
        # ---------------------------------------------
            url = (

                f"{settings.MCP_BASE_URL}"

                f"{path}"
            )

            # ---------------------------------------------
            # NO TIMEOUT
            # ---------------------------------------------
            timeout = httpx.Timeout(

                timeout=None
            )

            # ---------------------------------------------
            # ASYNC CLIENT
            # ---------------------------------------------
            async with httpx.AsyncClient(

                timeout=timeout

            ) as client:

                response = await client.request(

                    method=method,

                    url=url,

                    json=json,

                    headers={

                        "Authorization":
                            authorization,

                        "Content-Type":
                            "application/json"
                    }
                )

            # ---------------------------------------------
            # VALIDATE RESPONSE
            # ---------------------------------------------
            response.raise_for_status()

            # ---------------------------------------------
            # RETURN RESPONSE
            # ---------------------------------------------
            return response.json()

        except httpx.HTTPStatusError as e:

            raise HTTPException(

                status_code=e.response.status_code,

                detail=e.response.text
            )

        except Exception as e:

            raise HTTPException(

                status_code=500,

                detail=str(e)
            )
    
    
    return await _forward(
        method="POST",
        path="/trigger-jd-workflow",
        authorization=authorization,
        json=payload,
    )


@router.post("/save-generated-jd")
async def save_generated_jd(
    payload: dict,
    authorization: str = Header(None),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    return await _forward(
        method="POST",
        path="/save-generated-jd",
        authorization=authorization,
        json=payload,
    )


@router.post("/update-generated-jd")
async def update_generated_jd(
    jd_id: int,
    payload: dict,
    authorization: str = Header(None),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    return await _forward(
        method="POST",
        path="/update-generated-jd",
        authorization=authorization,
        params={"jd_id": jd_id},
        json=payload,
    )

