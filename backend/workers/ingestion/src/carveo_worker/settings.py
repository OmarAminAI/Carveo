from __future__ import annotations

from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CARVEO_", extra="ignore")

    environment: Literal["development", "test", "production"] = "development"
    crawl4ai_base_url: str = "http://crawl4ai:11235"
    crawl4ai_token: SecretStr = Field(min_length=1)
    crawl4ai_timeout_seconds: float = Field(default=20.0, gt=0, le=60)
    crawl4ai_batch_size: int = Field(default=10, ge=1, le=32)
    fixture_manifest_path: str = "/workspace/infra/fixtures/site/scenarios.json"
