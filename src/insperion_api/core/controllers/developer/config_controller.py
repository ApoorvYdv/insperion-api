import asyncio
from typing import Annotated, Optional

import cachetools
from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncEngine

from insperion_api.core.constants.error_response import ErrorResponse
from insperion_api.core.models.config import Config
from insperion_api.core.schemas.developer.config import (
    AddConfigRequest,
    UpdateConfigRequest,
)
from insperion_api.utils.common.custom_http_exception import CustomHTTPException
from insperion_api.utils.database.connections import get_async_engine
from insperion_api.utils.database.session_context_manager import session_context

config_cache = cachetools.TTLCache(maxsize=200, ttl=60 * 10)
cache_lock = asyncio.Lock()


class ConfigController:
    """
    Manages database configs with caching support.
    """

    def __init__(
        self, engine: Annotated[AsyncEngine, Depends(get_async_engine)]
    ) -> None:
        self.engine = engine

    async def get_configs(self, config_section: Optional[str] = None) -> list[Config]:
        """
        Get configs from cache if not from database
        """
        # Create cache key
        cache_key = f"configs:{config_section}"

        # Try to get from cache
        async with cache_lock:
            if cache_key in config_cache:
                return config_cache[cache_key]

        # Build query
        async with session_context(self.engine) as session:
            query = select(Config)

            if config_section is not None:
                query = query.where(Config.config_section == config_section)

            result = await session.scalars(query)
            configs = list(result.all())

        # Store in cache
        async with cache_lock:
            config_cache[cache_key] = configs

        return configs

    async def add_config(self, request: AddConfigRequest) -> dict:
        """
        Add a new config.
        """
        async with session_context(self.engine) as session:
            # Check if config already exists
            existing_config = await session.scalar(
                select(Config).where(
                    Config.config_section == request.config_section,
                    Config.config_key == request.config_key,
                )
            )

            if existing_config:
                raise CustomHTTPException(
                    ErrorResponse.CONFIG_ALREADY_EXISTS,
                    details={
                        "config_section": request.config_section,
                        "config_key": request.config_key,
                    },
                ).to_http_exception()

            # Create new config
            new_config = Config(**request.model_dump())

            session.add(new_config)
            await session.commit()

        # Clear cache after adding
        await self.refresh_cache()

        return {"message": "Config added successfully"}

    async def update_config(self, config_id: int, request: UpdateConfigRequest) -> dict:
        """
        Update an existing config.

        """
        async with session_context(self.engine) as session:
            # Get existing config
            existing_config = await session.scalar(
                select(Config).where(Config.id == config_id)
            )

            if not existing_config:
                raise CustomHTTPException(
                    ErrorResponse.CONFIG_NOT_FOUND, details={"config_id": config_id}
                ).to_http_exception()

            for key, value in request.model_dump(exclude_unset=True).items():
                setattr(existing_config, key, value)

            await session.commit()

        return {"message": "Config updated successfully"}

    async def delete_config(self, config_id: int) -> dict:
        """
        Delete a config by ID.
        """
        async with session_context(self.engine) as session:
            # Check if config exists
            existing_config_id = await session.execute(
                delete(Config).where(Config.id == config_id).returning(Config.id)
            )

            if not existing_config_id:
                raise CustomHTTPException(
                    ErrorResponse.CONFIG_NOT_FOUND, details={"config_id": config_id}
                ).to_http_exception()

            # Delete config
            await session.commit()

        return {"message": "Config deleted successfully"}

    async def refresh_cache(self) -> dict:
        """
        Refresh cache with fresh config data from database.
        Clears existing cache and repopulates with all configs.
        """
        # Clear existing cache
        async with cache_lock:
            config_cache.clear()

        # Fetch all configs from database
        async with session_context(self.engine) as session:
            result = await session.scalars(select(Config))
            all_configs = list(result.all())

        # Repopulate cache with all configs (no section filter)
        cache_key = "configs:None"
        async with cache_lock:
            config_cache[cache_key] = all_configs

        # Also cache configs grouped by section for faster filtered queries
        configs_by_section = {}
        for config in all_configs:
            section = config.config_section
            if section not in configs_by_section:
                configs_by_section[section] = []
            configs_by_section[section].append(config)

        # Store section-specific caches
        async with cache_lock:
            for section, configs in configs_by_section.items():
                cache_key = f"configs:{section}"
                config_cache[cache_key] = configs

        return {
            "message": "Config cache refreshed successfully",
            "total_configs": len(all_configs),
            "sections_cached": len(configs_by_section),
        }
