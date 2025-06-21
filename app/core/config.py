"""Application configuration settings."""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    # Application settings
    DEBUG: bool = Field(default=False, description="Debug mode")
    HOST: str = Field(default="0.0.0.0", description="Host to bind to")
    PORT: int = Field(default=8000, description="Port to bind to")
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1", "0.0.0.0"],
        description="Allowed hosts for CORS"
    )
    
    # Security settings
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT tokens"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access token expiration time in minutes"
    )
    
    # Google Cloud settings
    GOOGLE_CLOUD_PROJECT: Optional[str] = Field(
        default=None,
        description="Google Cloud Project ID"
    )
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = Field(
        default=None,
        description="Path to Google Cloud service account key file"
    )
    
    # Gemini AI settings
    GEMINI_API_KEY: Optional[str] = Field(
        default=None,
        description="Google Gemini API key"
    )
    GEMINI_MODEL: str = Field(
        default="gemini-pro",
        description="Gemini model to use for code generation"
    )
    
    # Database settings (for future MongoDB integration)
    DATABASE_URL: Optional[str] = Field(
        default=None,
        description="Database connection URL"
    )
    
    # Redis settings (for caching and task queue)
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    
    # File storage settings
    WORKFLOWS_STORAGE_PATH: str = Field(
        default="./generated_workflows",
        description="Path to store generated workflow files"
    )
    
    # Logging settings
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level"
    )
    LOG_FORMAT: str = Field(
        default="json",
        description="Logging format (json or console)"
    )
    
    # API settings
    API_V1_PREFIX: str = Field(
        default="/api/v1",
        description="API v1 prefix"
    )
    MAX_WORKFLOW_SIZE: int = Field(
        default=1024 * 1024,  # 1MB
        description="Maximum workflow file size in bytes"
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Create workflows storage directory if it doesn't exist
        os.makedirs(self.WORKFLOWS_STORAGE_PATH, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
