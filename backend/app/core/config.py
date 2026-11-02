from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Predictive Maintenance and Decision Support System"

    API_V1_PREFIX: str = "/api/v1"

    APP_VERSION: str = "0.1.0"

    # Only these three environment names are allowed.
    ENVIRONMENT: Literal["development", "testing", "production"] = "development"

    # Debug mode is disabled by default.
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
