from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CARVEO_", env_file=".env", extra="ignore")

    environment: Literal["development", "test", "production"] = "development"
    database_url: str = "postgresql+psycopg://carveo:carveo@localhost:5432/carveo"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    log_level: str = "INFO"

    @model_validator(mode="after")
    def validate_production(self) -> "Settings":
        if self.environment == "production":
            if "carveo:carveo" in self.database_url:
                raise ValueError("Production DATABASE_URL must not use development credentials")
            if "*" in self.cors_origins:
                raise ValueError("Production CORS origins must be explicit")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
