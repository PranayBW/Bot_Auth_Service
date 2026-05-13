from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


class Settings(BaseSettings):

    TENANT_ID: str

    BOT_APP_ID: str

    GATEWAY_API_CLIENT_ID: str
    MCP_BASE_URL: str = "http://localhost:8000"


    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
    BYPASS_AUTH: bool = True

settings = Settings()