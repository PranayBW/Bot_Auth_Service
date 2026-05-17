from fastapi import FastAPI
from auth_service.api.authorize import router
from auth_service.api.mcp_proxy import router as mcp_proxy_router

app = FastAPI(title="Authorization Service")

app.include_router(router)
app.include_router(mcp_proxy_router)
