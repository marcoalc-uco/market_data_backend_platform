# Core module
"""Core module containing configuration, logging, and exceptions.

This module provides the foundational components for the application:
- config: Application settings using pydantic-settings
- logging: Structured logging with structlog
- exceptions: Custom exception hierarchy
"""

from .config import Settings, get_settings, settings

__all__ = ["Settings", "get_settings", "settings"]
