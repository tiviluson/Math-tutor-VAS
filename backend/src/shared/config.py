"""
Centralized configuration management using Pydantic Settings.
"""

import os
from typing import Optional
from functools import lru_cache
from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Configuration
    app_name: str = "AI Geometry Tutor API"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    host: str = Field(default="127.0.0.1", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # LLM Configuration
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")
    llm_model: str = Field(default="gemini-2.0-flash-exp", env="LLM_MODEL")
    llm_temperature: float = Field(default=0.1, env="LLM_TEMPERATURE")
    max_output_tokens: int = Field(default=2048, env="MAX_OUTPUT_TOKENS")
    
    # Session Configuration
    session_timeout_hours: int = Field(default=2, env="SESSION_TIMEOUT_HOURS")
    max_sessions: int = Field(default=100, env="MAX_SESSIONS")
    
    # Asymptote Configuration
    asymptote_texpath: str = Field(default="/usr/bin", env="ASYMPTOTE_TEXPATH")
    asymptote_magickpath: str = Field(default="/usr/bin", env="ASYMPTOTE_MAGICKPATH")
    
    # CORS Configuration
    allowed_origins: list = Field(default=["*"], env="ALLOWED_ORIGINS")
    allow_credentials: bool = Field(default=True, env="ALLOW_CREDENTIALS")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    @validator("google_api_key")
    def validate_api_key(cls, v):
        """Validate that API key is provided."""
        if not v or len(v) < 10:
            raise ValueError("GOOGLE_API_KEY must be provided and valid")
        return v
    
    @validator("llm_temperature")
    def validate_temperature(cls, v):
        """Validate LLM temperature is within valid range."""
        if not 0.0 <= v <= 2.0:
            raise ValueError("LLM temperature must be between 0.0 and 2.0")
        return v
    
    @validator("session_timeout_hours")
    def validate_session_timeout(cls, v):
        """Validate session timeout is reasonable."""
        if not 1 <= v <= 24:
            raise ValueError("Session timeout must be between 1 and 24 hours")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v.upper()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def validate_environment() -> tuple[bool, list[str]]:
    """
    Validate that all required environment variables are set.
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    try:
        settings = get_settings()
        # If we can create settings without errors, validation passed
        return True, []
    except Exception as e:
        errors.append(f"Configuration error: {str(e)}")
        return False, errors


def get_database_url() -> Optional[str]:
    """Get database URL if configured (for future use)."""
    return os.getenv("DATABASE_URL")


def is_production() -> bool:
    """Check if running in production environment."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    return env in ("production", "prod")


def is_development() -> bool:
    """Check if running in development environment."""
    return not is_production()