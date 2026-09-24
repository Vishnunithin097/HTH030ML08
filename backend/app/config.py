import os
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Information
    PROJECT_NAME: str = "Cold-Start-Aware Hybrid Recommendation Engine with Business Guardrails"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database URLs
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/coldstart_db"
    SYNC_DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/coldstart_db"

    # JWT & Auth
    JWT_SECRET: str = "production_ready_jwt_secret_key_change_in_production_env"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Server Info
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 5173

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

    # Model Artifact Directories
    MODELS_DIR: str = os.getenv("MODELS_DIR", "models")
    RETAILROCKET_DIR: str = os.getenv("RETAILROCKET_DIR", "models/RetailRocket")
    BIGBASKET_DIR: str = os.getenv("BIGBASKET_DIR", "models/BigBasket")

    # Fallback / Alternative Directory Names
    ALT_MODELS_DIR: str = "model"
    ALT_RETAILROCKET_DIR: str = "model/RetailRocket"
    ALT_BIGBASKET_DIR: str = "model/BigBasket"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
