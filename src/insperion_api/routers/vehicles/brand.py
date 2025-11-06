from typing import Annotated

from fastapi import APIRouter, Depends

from insperion_api.core.controllers.vehicle.brand_controller import BrandController
from insperion_api.core.schemas.vehicle.brand import (
    AddVehicleBrandRequest,
    UpdateVehicleBrandRequest,
)

brand_router = APIRouter(prefix="/v1/brand", tags=["brand"])


@brand_router.get("")
async def get_all_brands(controller: Annotated[BrandController, Depends()]):
    return await controller.get_all_brand()


@brand_router.post("")
async def add_brand(
    request: AddVehicleBrandRequest, controller: Annotated[BrandController, Depends()]
):
    return await controller.add_brand(request)


@brand_router.patch("/{brand_id}")
async def update_brand(
    brand_id: int,
    request: UpdateVehicleBrandRequest,
    controller: Annotated[BrandController, Depends()],
):
    return await controller.update_brand(brand_id, request)


@brand_router.delete("/{brand_id}")
async def delete_brand(
    brand_id: int, controller: Annotated[BrandController, Depends()]
):
    return await controller.delete_brand(brand_id)
