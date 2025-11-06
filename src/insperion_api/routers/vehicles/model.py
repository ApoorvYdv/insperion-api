from typing import Annotated

from fastapi import APIRouter, Depends

from insperion_api.core.controllers.vehicle.model_controller import ModelController
from insperion_api.core.schemas.vehicle.model import (
    AddVehicleModelRequest,
    UpdateVehicleModelRequest,
)

model_router = APIRouter(prefix="/v1/model", tags=["model"])


@model_router.get("")
async def get_all_models(controller: Annotated[ModelController, Depends()]):
    return await controller.get_all_model()


@model_router.post("")
async def add_model(
    request: AddVehicleModelRequest, controller: Annotated[ModelController, Depends()]
):
    return await controller.add_model(request)


@model_router.patch("/{model_id}")
async def update_model(
    model_id: int,
    request: UpdateVehicleModelRequest,
    controller: Annotated[ModelController, Depends()],
):
    return await controller.update_model(model_id, request)


@model_router.delete("/{model_id}")
async def delete_model(
    model_id: int, controller: Annotated[ModelController, Depends()]
):
    return await controller.delete_model(model_id)
