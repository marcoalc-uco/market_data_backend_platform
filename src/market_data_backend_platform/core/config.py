"""Application configuration using pydantic-settings.

This module provides centralized configuration management for the application.
Settings are loaded from environment variables and .env files.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        app_name: Name of the application.
        app_version: Current version of the application.
        debug: Enable debug mode (more verbose logging, etc.).
        api_prefix: URL prefix for all API routes.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_format: Log output format ("json" for production, "console" for dev).
        db_host: PostgreSQL host address.
        db_port: PostgreSQL port (1-65535).
        db_user: PostgreSQL username.
        db_password: PostgreSQL password (hidden from repr).
        db_name: PostgreSQL database name.
        db_pool_size: Connection pool size.
        db_max_overflow: Maximum overflow connections.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "Market Data Backend Platform"
    app_version: str = "0.1.0"
    debug: bool = False

    # API
    api_prefix: str = "/api/v1"

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_format: Literal["json", "console"] = "console"

    # Database - PostgreSQL
    db_host: str = Field(
        default="localhost",
        description="PostgreSQL host address",
    )
    db_port: int = Field(
        default=5432,
        ge=1,
        le=65535,
        description="PostgreSQL port number",
    )
    db_user: str = Field(
        default="postgres",
        description="PostgreSQL username",
    )
    db_password: str = Field(
        default="",
        repr=False,  # Hide password in logs/repr
        description="PostgreSQL password",
    )
    db_name: str = Field(
        default="market_data",
        description="PostgreSQL database name",
    )

    # Connection pool settings
    db_pool_size: int = Field(
        default=5,
        ge=1,
        description="Database connection pool size",
    )
    db_max_overflow: int = Field(
        default=10,
        ge=0,
        description="Maximum overflow connections beyond pool size",
    )

    @computed_field
    def database_url(self) -> str:
        """Compute full PostgreSQL connection URL from individual fields.

        Returns:
            str: PostgreSQL connection string in format:
                 postgresql://user:password@host:port/database
        """
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Uses lru_cache to ensure only one Settings instance is created,
    avoiding multiple reads of environment variables.

    Returns:
        Settings: Cached application settings.
    """
    return Settings()


# Convenience instance for direct import
settings = get_settings()
