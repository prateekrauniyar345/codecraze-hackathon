"""
Application configuration management.
Loads settings from environment variables with sensible defaults.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Union
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:hB7fhr,4ds;v@localhost:5432/scholarsense"
    
    # OpenRouter API
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # LLM Configuration
    LLM_MODEL: str = "anthropic/claude-3.5-sonnet"
    LLM_TIMEOUT: int = 60
    LLM_MAX_RETRIES: int = 3
    
    # JWT Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 1 week
    
    # File Upload
    UPLOAD_DIR: str = "./storage/uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    
    # Application
    DEBUG: bool = True
    ALLOWED_ORIGINS: Union[list[str], str] = ["http://localhost:5173", "http://localhost:3000"]
    
    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def parse_origins(cls, v):
        """Parse ALLOWED_ORIGINS from string or list."""
        if isinstance(v, str):
            # Remove brackets and quotes, then split
            v = v.strip('[]"\'')
            return [origin.strip(' "\'') for origin in v.split(',')]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
