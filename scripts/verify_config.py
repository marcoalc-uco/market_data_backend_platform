"""Verify environment configuration loading.

This script validates that all settings are loaded correctly from .env file.
Run this to verify the unified environment configuration works properly.

Usage:
    python -m market_data_backend_platform.scripts.verify_config
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(src_path))

from market_data_backend_platform.core import settings


def verify_settings() -> bool:
    """Verify all settings are loaded correctly."""
    print("=" * 80)
    print("Environment Configuration Verification")
    print("=" * 80)
    print()

    # Application Settings
    print("Application Settings:")
    print(f"  APP_NAME: {settings.app_name}")
    print(f"  APP_VERSION: {settings.app_version}")
    print(f"  DEBUG: {settings.debug}")
    print()

    # API Settings
    print("API Settings:")
    print(f"  API_PREFIX: {settings.api_prefix}")
    print()

    # Logging Settings
    print("Logging Settings:")
    print(f"  LOG_LEVEL: {settings.log_level}")
    print(f"  LOG_FORMAT: {settings.log_format}")
    print()

    # Database Settings
    print("Database Settings:")
    print(f"  DB_HOST: {settings.db_host}")
    print(f"  DB_PORT: {settings.db_port}")
    print(f"  DB_USER: {settings.db_user}")
    print(
        f"  DB_PASSWORD: {'*' * len(settings.db_password) if settings.db_password else '(not set)'}"
    )
    print(f"  DB_NAME: {settings.db_name}")
    print(f"  DB_POOL_SIZE: {settings.db_pool_size}")
    print(f"  DB_MAX_OVERFLOW: {settings.db_max_overflow}")
    print(
        f"  DATABASE_URL: {settings.database_url.replace(settings.db_password, '***') if settings.db_password else settings.database_url}"
    )
    print()

    # Scheduler Settings
    print("Scheduler Settings:")
    print(f"  SCHEDULER_ENABLED: {settings.scheduler_enabled}")
    print(f"  INGESTION_INTERVAL_MINUTES: {settings.ingestion_interval_minutes}")
    print()

    # Validation
    print("=" * 80)
    print("Validation Results:")
    print("=" * 80)

    errors = []
    warnings = []

    # Check critical settings
    if not settings.db_password:
        errors.append("DB_PASSWORD is not set")
    elif settings.db_password == "your_secure_password_here":
        warnings.append("DB_PASSWORD is still set to the default placeholder value")

    if settings.db_host == "localhost":
        warnings.append(
            "DB_HOST is set to 'localhost' (good for local dev, but Docker will override this)"
        )

    if settings.debug:
        warnings.append("DEBUG is enabled (should be False in production)")

    if settings.scheduler_enabled and settings.ingestion_interval_minutes < 5:
        warnings.append(
            f"Scheduler interval is very short ({settings.ingestion_interval_minutes} minutes)"
        )

    # Print results
    if errors:
        print("\n❌ ERRORS:")
        for error in errors:
            print(f"  - {error}")
        print()
        return False

    if warnings:
        print("\n⚠️  WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")
        print()

    print("✅ All settings loaded successfully!")
    print()
    print("Configuration Summary:")
    print(
        f"  - Application will connect to PostgreSQL at: {settings.db_host}:{settings.db_port}"
    )
    print(f"  - Database name: {settings.db_name}")
    print(f"  - Scheduler: {'ENABLED' if settings.scheduler_enabled else 'DISABLED'}")
    print(f"  - Log level: {settings.log_level}")
    print()

    return True


if __name__ == "__main__":
    success = verify_settings()
    sys.exit(0 if success else 1)
