"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Any

from pydantic import PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ============================================
    # APPLICATION
    # ============================================
    app_name: str = "HealthEquiRoute"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # ============================================
    # DATABASE
    # ============================================
    postgres_user: str = "healthequiroute"
    postgres_password: str = "devpassword123"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "healthequiroute"
    database_url: PostgresDsn | None = None

    @field_validator("database_url", mode="before")
    @classmethod
    def assemble_db_url(cls, v: str | None, info: Any) -> str:
        if v:
            return v
        data = info.data
        return str(
            PostgresDsn.build(
                scheme="postgresql",
                username=data.get("postgres_user"),
                password=data.get("postgres_password"),
                host=data.get("postgres_host"),
                port=data.get("postgres_port"),
                path=data.get("postgres_db"),
            )
        )

    # ============================================
    # REDIS
    # ============================================
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str | None = None
    redis_url: RedisDsn | None = None

    @field_validator("redis_url", mode="before")
    @classmethod
    def assemble_redis_url(cls, v: str | None, info: Any) -> str:
        if v:
            return v
        data = info.data
        password = data.get("redis_password")
        if password:
            return f"redis://:{password}@{data.get('redis_host')}:{data.get('redis_port')}/0"
        return f"redis://{data.get('redis_host')}:{data.get('redis_port')}/0"

    # ============================================
    # JWT AUTHENTICATION
    # ============================================
    jwt_secret_key: str = "CHANGE_THIS_IN_PRODUCTION_MIN_32_CHARS_REQUIRED"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # ============================================
    # GOOGLE OAUTH 2.0
    # ============================================
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str = "http://localhost:3000/auth/google/callback"

    # ============================================
    # CORS
    # ============================================
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.strip("[]").split(",")]
        return v

    # ============================================
    # BACKEND SERVER
    # ============================================
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # ============================================
    # CELERY
    # ============================================
    celery_broker_url: str | None = None
    celery_result_backend: str | None = None

    @field_validator("celery_broker_url", mode="before")
    @classmethod
    def assemble_celery_broker(cls, v: str | None, info: Any) -> str:
        if v:
            return v
        data = info.data
        host = data.get("redis_host", "localhost")
        port = data.get("redis_port", 6379)
        password = data.get("redis_password")
        if password:
            return f"redis://:{password}@{host}:{port}/1"
        return f"redis://{host}:{port}/1"

    @field_validator("celery_result_backend", mode="before")
    @classmethod
    def assemble_celery_backend(cls, v: str | None, info: Any) -> str:
        if v:
            return v
        data = info.data
        host = data.get("redis_host", "localhost")
        port = data.get("redis_port", 6379)
        password = data.get("redis_password")
        if password:
            return f"redis://:{password}@{host}:{port}/2"
        return f"redis://{host}:{port}/2"

    # ============================================
    # DEX ENGINE DEFAULTS
    # ============================================
    dex_clinical_weight: float = 0.40
    dex_social_weight: float = 0.35
    dex_accessibility_weight: float = 0.25
    dex_model_version: str = "v1.0"

    # ============================================
    # FEATURE FLAGS
    # ============================================
    enable_ml_features: bool = False
    enable_llm_features: bool = False

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def sync_database_url(self) -> str:
        """Return synchronous database URL for Alembic."""
        return str(self.database_url)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
