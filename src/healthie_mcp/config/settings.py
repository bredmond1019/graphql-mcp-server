"""Configuration management for Healthie MCP server.

This module handles all configuration settings for the Healthie MCP server,
loading values from environment variables with sensible defaults.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional, Any
from pydantic import Field, field_validator, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

from ..exceptions import InvalidConfigurationError
from ..constants import DEFAULT_TIMEOUT_SECONDS, MAX_RETRIES


class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    
    All settings can be overridden using environment variables.
    For example, HEALTHIE_API_URL will override healthie_api_url.
    """
    
    # API Configuration
    healthie_api_url: HttpUrl = Field(
        default="https://staging-api.gethealthie.com/graphql",
        description="Healthie GraphQL API URL",
        alias="HEALTHIE_API_URL"
    )
    
    healthie_api_key: Optional[str] = Field(
        default=None,
        description="Healthie API key for authentication",
        alias="HEALTHIE_API_KEY"
    )
    
    # Directory Configuration
    schema_dir: Path = Field(
        default=Path("./schemas"),
        description="Directory containing GraphQL schema files",
        alias="SCHEMA_DIR"
    )
    
    # Cache Configuration
    cache_enabled: bool = Field(
        default=True,
        description="Whether to enable caching for GraphQL schema",
        alias="CACHE_ENABLED"
    )
    
    cache_duration_hours: int = Field(
        default=24,
        description="How long to cache the schema in hours",
        alias="CACHE_DURATION_HOURS"
    )
    
    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        alias="LOG_LEVEL"
    )
    
    # Network Configuration
    request_timeout: int = Field(
        default=DEFAULT_TIMEOUT_SECONDS,
        description="HTTP request timeout in seconds",
        alias="REQUEST_TIMEOUT"
    )
    
    max_retries: int = Field(
        default=MAX_RETRIES,
        description="Maximum number of retry attempts for failed requests",
        alias="MAX_RETRIES"
    )
    
    # Development Configuration
    debug_mode: bool = Field(
        default=False,
        description="Enable debug mode for development",
        alias="DEBUG_MODE"
    )
    
    @field_validator("healthie_api_key", mode="before")
    @classmethod
    def validate_api_key(cls, v: Any) -> Optional[str]:
        """Validate API key - convert empty strings to None.
        
        Args:
            v: The API key value
            
        Returns:
            The validated API key or None
        """
        if v is None:
            return None
        if isinstance(v, str) and v.strip() == "":
            return None
        return v
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the allowed values.
        
        Args:
            v: The log level string
            
        Returns:
            The validated log level in uppercase
            
        Raises:
            InvalidConfigurationError: If log level is invalid
        """
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        normalized = v.upper()
        if normalized not in allowed_levels:
            raise InvalidConfigurationError(
                "log_level",
                v,
                f"Must be one of {allowed_levels}"
            )
        return normalized
    
    @field_validator("healthie_api_url")
    @classmethod
    def validate_api_url(cls, v: Any) -> HttpUrl:
        """Validate API URL is not empty.
        
        Args:
            v: The API URL
            
        Returns:
            The validated URL
            
        Raises:
            InvalidConfigurationError: If URL is empty
        """
        if isinstance(v, str) and v.strip() == "":
            raise InvalidConfigurationError(
                "healthie_api_url",
                v,
                "API URL cannot be empty"
            )
        return v
    
    @field_validator("schema_dir", mode="before")
    @classmethod
    def validate_schema_dir(cls, v: Any) -> Path:
        """Convert string to Path and validate.
        
        Args:
            v: The schema directory path
            
        Returns:
            Path object for the schema directory
        """
        if isinstance(v, str):
            return Path(v)
        return v
    
    @field_validator("cache_duration_hours")
    @classmethod
    def validate_cache_duration(cls, v: int) -> int:
        """Validate cache duration is positive.
        
        Args:
            v: Cache duration in hours
            
        Returns:
            The validated cache duration
            
        Raises:
            InvalidConfigurationError: If duration is not positive
        """
        if v <= 0:
            raise InvalidConfigurationError(
                "cache_duration_hours",
                v,
                "Cache duration must be positive"
            )
        return v
    
    @field_validator("request_timeout")
    @classmethod
    def validate_request_timeout(cls, v: int) -> int:
        """Validate request timeout is positive.
        
        Args:
            v: Request timeout in seconds
            
        Returns:
            The validated timeout
            
        Raises:
            InvalidConfigurationError: If timeout is not positive
        """
        if v <= 0:
            raise InvalidConfigurationError(
                "request_timeout",
                v,
                "Request timeout must be positive"
            )
        return v
    
    @field_validator("max_retries")
    @classmethod
    def validate_max_retries(cls, v: int) -> int:
        """Validate max retries is non-negative.
        
        Args:
            v: Maximum number of retries
            
        Returns:
            The validated retry count
            
        Raises:
            InvalidConfigurationError: If retries is negative
        """
        if v < 0:
            raise InvalidConfigurationError(
                "max_retries",
                v,
                "Max retries cannot be negative"
            )
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="",
        populate_by_name=True,  # Allow using field names for initialization
    )
    
    def is_production(self) -> bool:
        """Check if running in production mode.
        
        Returns:
            True if in production (not debug mode), False otherwise
        """
        return not self.debug_mode
    
    def get_schema_file_path(self) -> Path:
        """Get the full path to the schema file.
        
        Returns:
            Path to the GraphQL schema file
        """
        from ..constants import SCHEMA_FILE_NAME
        return self.schema_dir / SCHEMA_FILE_NAME


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached).
    
    This function returns a cached instance of the settings,
    ensuring that environment variables are only read once.
    
    Returns:
        The application settings instance
    """
    return Settings()


def clear_settings_cache() -> None:
    """Clear the settings cache.
    
    This should only be used in tests or when settings need to be reloaded.
    """
    get_settings.cache_clear()