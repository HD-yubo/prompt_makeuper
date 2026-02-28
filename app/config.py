from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration with environment variable support."""

    # API Server
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)

    # LLM Configuration
    OPENAI_API_KEY: str = Field(..., description="LLM API key")
    OPENAI_BASE_URL: str = Field(default="https://api.openai.com/v1")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini")

    # Optimization Settings
    MAX_ITERATIONS: int = Field(default=3)
    TEMPERATURE: float = Field(default=0.7)

    # Logging Configuration
    LOG_DIR: str = Field(default="logs")
    ENABLE_LOGGING: bool = Field(default=True)
    LOG_LEVEL: str = Field(default="INFO")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


settings = Settings()
