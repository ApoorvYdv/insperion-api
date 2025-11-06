from typing import Any, Dict, Optional

from pydantic import BaseModel


class BrandInfo(BaseModel):
    name: str
    country: str
    established_year: int
    logo_url: Optional[str] = None


class ModelInfo(BaseModel):
    model_name: str
    year_launched: int
    body_type: str
    seating_capacity: int


class VariantInfo(BaseModel):
    variant_name: str
    engine_type: str
    transmission: str
    fuel_type: str
    price: float
    features: Dict[str, Any]


class VehicleUnitInfo(BaseModel):
    vin: str
    psn: Optional[str] = None
    chassis_no: Optional[str] = None
    manufacturing_year: int
    color: str


class VehicleScanDetails(BaseModel):
    vehicle_unit: VehicleUnitInfo
    variant_info: VariantInfo
    model_info: ModelInfo
    brand_info: BrandInfo

    class Config:
        schema_extra = {
            "example": {
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
        }
