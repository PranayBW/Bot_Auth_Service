from fastapi import FastAPI
from auth_service.api.authorize import router
from auth_service.api.mcp_proxy import router as mcp_proxy_router
from auth_service.memory.db import autoinit_schema, close_pool

app = FastAPI(title="Authorization Service")

app.include_router(router)
app.include_router(mcp_proxy_router)


@app.on_event("startup")
async def _startup() -> None:
    await autoinit_schema()


@app.on_event("shutdown")
async def _shutdown() -> None:
    await close_pool()
