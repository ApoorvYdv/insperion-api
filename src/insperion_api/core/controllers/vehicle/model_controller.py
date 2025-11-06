from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncEngine

from insperion_api.core.constants.error_response import ErrorResponse
from insperion_api.core.models.vehicle import VehicleModel
from insperion_api.core.schemas.vehicle.model import (
    AddVehicleModelRequest,
    UpdateVehicleModelRequest,
)
from insperion_api.utils.common.custom_http_exception import CustomHTTPException
from insperion_api.utils.database.connections import get_async_engine
from insperion_api.utils.database.session_context_manager import session_context


class ModelController:
    """Handles Vehicle Model operation"""

    def __init__(
        self,
        engine: AsyncEngine = Depends(get_async_engine),
    ) -> None:
        self.engine = engine

    async def add_model(self, request: AddVehicleModelRequest):
        async with session_context(self.engine) as session:
            model = VehicleModel(**request.model_dump())
            session.add(model)
            await session.commit()

            return {"message": "Vehicle model added successfully"}

    async def update_model(self, model_id: int, request: UpdateVehicleModelRequest):
        async with session_context(self.engine) as session:
            existing_model = await session.get(VehicleModel, model_id)
            if not existing_model:
                raise CustomHTTPException(
                    error_response=ErrorResponse.MODEL_NOT_FOUND
                ).to_http_exception()

            for key, value in request.model_dump(exclude_unset=True):
                setattr(existing_model, key, value)

            await session.commit()

            return {"message": "Vehicle model successfully updated"}

    async def get_all_model(self):
        async with session_context(self.engine) as session:
            models = await session.scalars(select(VehicleModel))

            if not models:
                raise CustomHTTPException(
                    ErrorResponse.BRAND_NOT_FOUND
                ).to_http_exception()

            return models.all()

    async def delete_model(self, model_id: int):
        async with session_context(self.engine) as session:
            deleted_model_id = await session.execute(
                delete(VehicleModel)
                .filter(VehicleModel.id == model_id)
                .returning(VehicleModel.id)
            )

            if not deleted_model_id:
                raise CustomHTTPException(
                    ErrorResponse.BRAND_NOT_FOUND
                ).to_http_exception()

            return {"message": "Vehicle model successfully deleted"}
