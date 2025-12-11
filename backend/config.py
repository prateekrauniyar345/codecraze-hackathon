"""
Application configuration management.
Loads settings from environment variables with sensible defaults.
"""
from functools import lru_cache
from typing import Union, Optional, List
import os

from pydantic import field_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Tell pydantic-settings to load from .env and ignore unknown env vars
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # <- avoid errors for env vars we don't explicitly model
    )

    # ────────────── Database ──────────────
    DATABASE_URL: str = Field(
        default="postgresql://postgres:hB7fhr,4ds;v@localhost:5432/scholarsense",
        env="DATABASE_URL",
    )

    # ────────────── OpenRouter / LLM provider ──────────────
    OPENROUTER_API_KEY: str = Field(..., env="OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL: str = Field(
        default="https://openrouter.ai/api/v1",
        env="OPENROUTER_BASE_URL",
    )

    # Simpler.Grants.gov API (we support both SIMPLE_GRANTS_API_KEY and SIMPLE_GRANTS)
    SIMPLE_GRANTS_API_KEY: Optional[str] = Field(
        default=None,
        env="SIMPLE_GRANTS_API_KEY",
    )

    @field_validator("SIMPLE_GRANTS_API_KEY", mode="before")
    @classmethod
    def fallback_simple_grants(cls, v: Optional[str]) -> Optional[str]:
        """
        If SIMPLE_GRANTS_API_KEY is not set, fall back to SIMPLE_GRANTS env var.
        This lets you keep using SIMPLE_GRANTS in your .env if you want.
        """
        if v:
            return v
        return os.getenv("SIMPLE_GRANTS") or None

    # ────────────── LLM configuration ──────────────
    LLM_MODEL: str = Field(
        default="openai/gpt-oss-120b",
        env="LLM_MODEL",
    )
    LLM_TIMEOUT: int = Field(
        default=60,
        env="LLM_TIMEOUT",
    )
    LLM_MAX_RETRIES: int = Field(
        default=3,
        env="LLM_MAX_RETRIES",
    )

    # ────────────── JWT Authentication ──────────────
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(
        default="HS256",
        env="ALGORITHM",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=10080,  # 1 week
        env="ACCESS_TOKEN_EXPIRE_MINUTES",
    )

    # ────────────── File Upload ──────────────
    UPLOAD_DIR: str = Field(
        default="./storage/uploads",
        env="UPLOAD_DIR",
    )
    MAX_UPLOAD_SIZE: int = Field(
        default=10_485_760,  # 10MB
        env="MAX_UPLOAD_SIZE",
    )

    # ────────────── Application ──────────────
    DEBUG: bool = Field(
        default=True,
        env="DEBUG",
    )
    ALLOWED_ORIGINS: Union[List[str], str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        env="ALLOWED_ORIGINS",
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        """Parse ALLOWED_ORIGINS from string or list."""
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []

            # Try JSON-style list: '["http://localhost:5173","http://localhost:3000"]'
            if v.startswith("["):
                try:
                    import json
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return parsed
                except Exception:
                    pass

            # Fallback: comma-separated
            return [origin.strip(' "\'') for origin in v.split(",")]

        return v


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
