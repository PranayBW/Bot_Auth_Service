from fastapi import FastAPI
from auth_service.api.authorize import router

app = FastAPI(title="Authorization Service")

app.include_router(router)