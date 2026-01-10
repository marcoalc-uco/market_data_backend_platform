"""FastAPI dependency injection utilities.

This module provides shared dependencies for API endpoints.
Dependencies are injected using FastAPI's Depends() mechanism.

Example usage:
    from market_data_backend_platform.api.dependencies import SettingsDep

    @router.get("/example")
    async def example(settings: SettingsDep):
        return {"app_name": settings.app_name}
"""

from typing import Annotated

from fastapi import Depends

from market_data_backend_platform.core import Settings, get_settings

# Type alias for settings dependency
# Usage: async def endpoint(settings: SettingsDep):
SettingsDep = Annotated[Settings, Depends(get_settings)]
