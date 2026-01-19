from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Grundkonfiguration
    app_env: str = "local"

    # DB
    database_url: str = "postgresql+psycopg://hausportal:hausportal@localhost:5432/hausportal"

    # JWT
    jwt_secret: str = "CHANGE_ME"
    jwt_alg: str = "HS256"
    access_token_exp_minutes: int = 60

    # MinIO / S3
    minio_endpoint: str = "http://localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "hausportal"
    minio_region: str = "us-east-1"

    # Pydantic Settings
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # wichtig: alte/zusätzliche env vars sollen nicht crashen
    )


settings = Settings()
