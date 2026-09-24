import os
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Information
    PROJECT_NAME: str = "Cold-Start-Aware Hybrid Recommendation Engine with Business Guardrails"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Database URLs
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/coldstart_db")
    SYNC_DATABASE_URL: str = os.getenv("SYNC_DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/coldstart_db")

    # JWT & Auth
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev_insecure_jwt_secret_for_local_only_12345")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Server Info
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", 8000))
    FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", 5173))

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    # Canonical Model Artifact Directories
    MODELS_DIR: str = os.getenv("MODELS_DIR", "models")
    RETAILROCKET_DIR: str = os.getenv("RETAILROCKET_DIR", "models/RetailRocket")
    BIGBASKET_DIR: str = os.getenv("BIGBASKET_DIR", "models/BigBasket")

    # Alternative / Legacy Fallback
    ALT_MODELS_DIR: str = "model"
    ALT_RETAILROCKET_DIR: str = "model/RetailRocket"
    ALT_BIGBASKET_DIR: str = "model/BigBasket"

    def validate_production_security(self):
        """Rejects insecure development defaults when running in production mode."""
        if self.ENVIRONMENT.lower() == "production":
            if "dev_insecure" in self.JWT_SECRET or "change_in_production" in self.JWT_SECRET or len(self.JWT_SECRET) < 32:
                raise ValueError("PRODUCTION SECURITY ERROR: Strong JWT_SECRET environment variable is required in production mode.")
            if "postgres:postgres@" in self.DATABASE_URL or "postgres:postgres@" in self.SYNC_DATABASE_URL:
                raise ValueError("PRODUCTION SECURITY ERROR: Default database credentials detected. Custom DATABASE_URL is required in production.")
            if "*" in self.CORS_ORIGINS:
                raise ValueError("PRODUCTION SECURITY ERROR: Wildcard CORS origin is forbidden in production mode.")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
settings.validate_production_security()
