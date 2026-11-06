from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEV_JWT_SECRET_KEY = "dev-only-insecure-jwt-secret-change-me-in-production"


class Settings(BaseSettings):
    PROJECT_NAME: str = "Predictive Maintenance and Decision Support System"

    API_V1_PREFIX: str = "/api/v1"

    APP_VERSION: str = "0.1.0"

    # Only these three environment names are allowed.
    ENVIRONMENT: Literal["development", "testing", "production"] = "development"

    # Debug mode is disabled by default.
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    DATABASE_URL: str = "postgresql+psycopg://pm_user:pm_password@127.0.0.1:5433/predictive_maintenance"

    # JWT authentication. Override JWT_SECRET_KEY through the environment
    # outside development; production refuses to start with the dev default.
    JWT_SECRET_KEY: str = DEV_JWT_SECRET_KEY
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720

    @model_validator(mode="after")
    def _reject_dev_secret_in_production(self):
        if self.ENVIRONMENT == "production" and self.JWT_SECRET_KEY == DEV_JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY must be set in production")
        return self


settings = Settings()
