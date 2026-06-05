from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


class Settings(BaseSettings):

    TENANT_ID: str

    BOT_APP_ID: str

    GATEWAY_API_CLIENT_ID: str
    MCP_BASE_URL: str = "http://localhost:8000"
    DATABASE_URL: str = "postgresql://postgres:root@localhost:5432/gpm"
    AGENT_MEMORY_AUTOINIT: bool = False
    OLLAMA_ENABLED: bool = True
    OLLAMA_BASE_URL: str = "http://106.51.106.43:11435"
    OLLAMA_MODEL: str = "qwen2.5:7b"
    OLLAMA_FALLBACK_MODEL: str = "mistral:latest"
    OLLAMA_TIMEOUT_SECONDS: float = 20.0


    model_config = SettingsConfigDict(
        env_file=(".env", "auth_service/.env"),
        extra="ignore"
    )
    BYPASS_AUTH: bool = True

settings = Settings()
