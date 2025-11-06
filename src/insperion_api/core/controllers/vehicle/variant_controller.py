from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncEngine

from insperion_api.core.constants.error_response import ErrorResponse
from insperion_api.core.models.vehicle import VehicleVariant
from insperion_api.core.schemas.vehicle.variant import (
    AddVehicleVariantRequest,
    UpdateVehicleVariantRequest,
)
from insperion_api.utils.common.custom_http_exception import CustomHTTPException
from insperion_api.utils.database.connections import get_async_engine
from insperion_api.utils.database.session_context_manager import session_context


class VariantController:
    """Handles Vehicle Variant operation"""

    def __init__(
        self,
        engine: AsyncEngine = Depends(get_async_engine),
    ) -> None:
        self.engine = engine

    async def add_variant(self, request: AddVehicleVariantRequest):
        async with session_context(self.engine) as session:
            variant = VehicleVariant(**request.model_dump())
            session.add(variant)
            await session.commit()

            return {"message": "Vehicle variant added successfully"}

    async def update_variant(
        self, variant_id: int, request: UpdateVehicleVariantRequest
    ):
        async with session_context(self.engine) as session:
            existing_variant = await session.get(VehicleVariant, variant_id)
            if not existing_variant:
                raise CustomHTTPException(
                    error_response=ErrorResponse.BRAND_NOT_FOUND
                ).to_http_exception()

            for key, value in request.model_dump(exclude_unset=True):
                setattr(existing_variant, key, value)

            await session.commit()

            return {"message": "Vehicle variant successfully updated"}

    async def get_all_variant(self):
        async with session_context(self.engine) as session:
            variants = await session.scalars(select(VehicleVariant))

            if not variants:
                raise CustomHTTPException(
                    ErrorResponse.BRAND_NOT_FOUND
                ).to_http_exception()

            return variants.all()

    async def delete_variant(self, variant_id: int):
        async with session_context(self.engine) as session:
            deleted_variant_id = await session.execute(
                delete(VehicleVariant)
                .filter(VehicleVariant.id == variant_id)
                .returning(VehicleVariant.id)
            )

            if not deleted_variant_id:
                raise CustomHTTPException(
                    ErrorResponse.BRAND_NOT_FOUND
                ).to_http_exception()

            return {"message": "Vehicle variant successfully deleted"}
