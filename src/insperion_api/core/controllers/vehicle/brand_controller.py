from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncEngine

from insperion_api.core.constants.error_response import ErrorResponse
from insperion_api.core.models.vehicle import VehicleBrand
from insperion_api.core.schemas.vehicle.brand import (
    AddVehicleBrandRequest,
    UpdateVehicleBrandRequest,
)
from insperion_api.utils.common.custom_http_exception import CustomHTTPException
from insperion_api.utils.database.connections import get_async_engine
from insperion_api.utils.database.session_context_manager import session_context


class BrandController:
    """Handles Vehicle Brand operation"""

    def __init__(
        self,
        engine: AsyncEngine = Depends(get_async_engine),
    ) -> None:
        self.engine = engine

    async def add_brand(self, request: AddVehicleBrandRequest):
        async with session_context(self.engine) as session:
            brand = VehicleBrand(**request.model_dump())
            session.add(brand)
            await session.commit()

            return {"message": "Vehicle brand added successfully"}

    async def update_brand(self, brand_id: int, request: UpdateVehicleBrandRequest):
        async with session_context(self.engine) as session:
            existing_brand = await session.get(VehicleBrand, brand_id)
            if not existing_brand:
                raise CustomHTTPException(
                    error_response=ErrorResponse.BRAND_NOT_FOUND
                ).to_http_exception()

            for key, value in request.model_dump(exclude_unset=True):
                setattr(existing_brand, key, value)

            await session.commit()

            return {"message": "Vehicle brand successfully updated"}

    async def get_all_brand(self):
        async with session_context(self.engine) as session:
            brands = await session.scalars(select(VehicleBrand))

            if not brands:
                raise CustomHTTPException(
                    ErrorResponse.BRAND_NOT_FOUND
                ).to_http_exception()

            return brands.all()

    async def delete_brand(self, brand_id: int):
        async with session_context(self.engine) as session:
            deleted_brand_id = await session.execute(
                delete(VehicleBrand)
                .filter(VehicleBrand.id == brand_id)
                .returning(VehicleBrand.id)
            )

            if not deleted_brand_id:
                raise CustomHTTPException(
                    ErrorResponse.BRAND_NOT_FOUND
                ).to_http_exception()

            return {"message": "Vehicle brand successfully deleted"}
