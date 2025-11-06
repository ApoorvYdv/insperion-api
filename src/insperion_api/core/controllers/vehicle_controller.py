from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine

from insperion_api.core.constants.error_response import ErrorResponse
from insperion_api.core.models.vehicle import VehicleUnit, VehicleVariant
from insperion_api.core.schemas.vehicle_unit import VehicleScanDetails
from insperion_api.modules.database_configs.inspection_config import InspectionConfig
from insperion_api.utils.common.custom_http_exception import CustomHTTPException
from insperion_api.utils.database.connections import get_async_engine
from insperion_api.utils.database.session_context_manager import session_context


class VehicleController:
    def __init__(
        self,
        inspection_config: Annotated[InspectionConfig, Depends()],
        engine: AsyncEngine = Depends(get_async_engine),
    ) -> None:
        self.engine = engine
        self.inspection_config = inspection_config

    async def fetch_unit_info(self, unit_id: int) -> VehicleScanDetails:
        vehicle_unit_info: dict = {
            "vehicle_unit": {
                "vin": "MA3ECDHE3SD123456",
                "psn": "SMILER2024A56789",
                "chassis_no": "BMW3100SD123456",
                "manufacturing_year": 2024,
                "color": "Pearl Arctic White",
            },
            "variant_info": {
                "variant_name": "Wagon R 1.0 LXI CNG",
                "engine_type": "K10C",
                "transmission": "Manual",
                "fuel_type": "CNG",
                "price": 625000,
                "features": {
                    "airbags": 2,
                    "abs": True,
                    "power_steering": True,
                    "ac": True,
                    "power_windows": True,
                    "central_locking": True,
                    "music_system": False,
                },
            },
            "model_info": {
                "model_name": "Wagon R",
                "year_launched": 2019,
                "body_type": "Hatchback",
                "seating_capacity": 5,
            },
            "brand_info": {
                "name": "Maruti Suzuki",
                "country": "Japan",
                "established_year": 1981,
                "logo_url": "https://example.com/logos/maruti_suzuki.png",
            },
        }
        return VehicleScanDetails(**vehicle_unit_info)

    async def fetch_variant_info(self, variant_name: str) -> VehicleVariant:
        async with session_context(self.engine) as session:
            variant = await session.scalar(
                select(VehicleVariant).filter(
                    VehicleVariant.variant_name == variant_name
                )
            )
            if not variant:
                raise CustomHTTPException(
                    ErrorResponse.INVALID_VARIANT_PROVIDED,
                    details={"variant": variant_name},
                ).to_http_exception()
            return variant

    async def fetch_scan_details(self, unit_id: int) -> VehicleScanDetails:
        vehicle_scan_details: VehicleScanDetails = await self.fetch_unit_info(unit_id)

        variant: VehicleVariant = await self.fetch_variant_info(
            vehicle_scan_details.variant_info.variant_name
        )

        vehicle_unit = VehicleUnit(
            variant_id=variant.id, **vehicle_scan_details.vehicle_unit.model_dump()
        )
        flows = await self.inspection_config.flows
        print(flows)

        async with session_context(self.engine) as session:
            session.add(vehicle_unit)
            await session.commit()

        return vehicle_scan_details
