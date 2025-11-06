from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query

from insperion_api.core.controllers.developer.config_controller import ConfigController
from insperion_api.core.schemas.developer.config import (
    AddConfigRequest,
    UpdateConfigRequest,
)

config_router = APIRouter(prefix="/v1/config", tags=["config"])


@config_router.get("")
async def get_configs(
    controller: Annotated[ConfigController, Depends()],
    config_section: Optional[str] = Query(
        None, description="Filter by configuration section"
    ),
):
    return await controller.get_configs(config_section)


@config_router.post("")
async def add_config(
    request: AddConfigRequest, controller: Annotated[ConfigController, Depends()]
) -> dict:
    return await controller.add_config(request)


@config_router.patch("/{config_id}")
async def update_config(
    config_id: int,
    request: UpdateConfigRequest,
    controller: Annotated[ConfigController, Depends()],
) -> dict:
    return await controller.update_config(config_id, request)


@config_router.delete("/{config_id}")
async def delete_config(
    config_id: int, controller: Annotated[ConfigController, Depends()]
) -> dict:
    return await controller.delete_config(config_id)
