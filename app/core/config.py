from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: str = Field(default="local", validation_alias="APP_ENV")
    database_url: str = Field(validation_alias="DATABASE_URL")

    minio_endpoint: str = Field(validation_alias="MINIO_ENDPOINT")
    minio_access_key: str = Field(validation_alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(validation_alias="MINIO_SECRET_KEY")
    minio_bucket: str = Field(validation_alias="MINIO_BUCKET")

    jwt_secret: str = Field(validation_alias="JWT_SECRET")
    jwt_alg: str = Field(default="HS256", validation_alias="JWT_ALG")


settings = Settings()
