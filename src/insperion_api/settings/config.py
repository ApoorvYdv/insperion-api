import json
from typing import List

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable loading"""

    # Database Configuration
    db_username: str = Field(..., alias="DB_USERNAME")
    db_password: str = Field(..., alias="DB_PASSWORD")
    db_host: str = Field("localhost", alias="DB_HOST")
    db_port: int = Field(5433, alias="DB_PORT")
    db_name: str = Field("insperion_api", alias="DB_NAME")
    db_pool_size: int = Field(10, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(10, alias="DB_MAX_OVERFLOW")

    # AWS Configuration
    aws_region: str = Field("ap-south-1", alias="AWS_REGION")
    aws_access_key_id: str = Field(..., alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(..., alias="AWS_SECRET_ACCESS_KEY")
    cognito_user_pool_id: str = Field("", alias="COGNITO_USER_POOL_ID")
    s3_bucket: str = Field("insperion", alias="S3_BUCKET")

    # Application Configuration
    allowed_origins: List[str] = Field(default_factory=list, alias="ALLOWED_ORIGINS")

    # Yolo model
    yolo_model_path: str = Field(..., alias="YOLO_MODEL_PATH")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        enable_decoding=True,
    )

    @property
    def database_url(self) -> str:
        """Get database connection URL"""
        return (
            f"postgresql://{self.db_username}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @field_validator("db_port")
    def validate_db_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("Database port must be between 1 and 65535")
        return v

    @model_validator(mode="before")
    def parse_allowed_origins(cls, values: dict):
        raw = values.get("ALLOWED_ORIGINS")
        if isinstance(raw, str):
            try:
                values["ALLOWED_ORIGINS"] = json.loads(raw)
            except json.JSONDecodeError:
                values["ALLOWED_ORIGINS"] = [v.strip() for v in raw.split(",")]
        return values


# Create settings instance
settings = Settings()
