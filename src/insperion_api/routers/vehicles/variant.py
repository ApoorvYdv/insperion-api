from typing import Annotated

from fastapi import APIRouter, Depends

from insperion_api.core.controllers.vehicle.variant_controller import VariantController
from insperion_api.core.schemas.vehicle.variant import (
    AddVehicleVariantRequest,
    UpdateVehicleVariantRequest,
)

variant_router = APIRouter(prefix="/v1/variant", tags=["variant"])


@variant_router.get("")
async def get_all_variants(controller: Annotated[VariantController, Depends()]):
    return await controller.get_all_variant()


@variant_router.post("")
async def add_variant(
    request: AddVehicleVariantRequest,
    controller: Annotated[VariantController, Depends()],
):
    return await controller.add_variant(request)


@variant_router.patch("/{variant_id}")
async def update_variant(
    variant_id: int,
    request: UpdateVehicleVariantRequest,
    controller: Annotated[VariantController, Depends()],
):
    return await controller.update_variant(variant_id, request)


@variant_router.delete("/{variant_id}")
async def delete_variant(
    variant_id: int, controller: Annotated[VariantController, Depends()]
):
    return await controller.delete_variant(variant_id)
