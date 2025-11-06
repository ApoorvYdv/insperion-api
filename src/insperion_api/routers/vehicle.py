from typing import Annotated

from fastapi import APIRouter, Depends

from insperion_api.core.controllers.vehicle_controller import VehicleController
from insperion_api.core.schemas.vehicle_unit import VehicleScanDetails

vehicle_router = APIRouter(prefix="/v1/vehicle", tags=["vehicle"])


@vehicle_router.get("/scan/{unit_id}")
async def fetch_unit_info(
    unit_id: int, controller: Annotated[VehicleController, Depends()]
) -> VehicleScanDetails:
    return await controller.fetch_scan_details(unit_id)
