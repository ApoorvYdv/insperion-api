from typing import Optional

from pydantic import BaseModel


class AddVehicleVariantRequest(BaseModel):
    model_id: int
    variant_name: str
    engine_type: str
    transmission: str
    fuel_type: str
    vin: str
    psn: str
    chassis_no: str
    price: float
    features: dict


class UpdateVehicleVariantRequest(BaseModel):
    model_id: int
    variant_name: Optional[str] = None
    engine_type: Optional[str] = None
    transmission: Optional[str] = None
    fuel_type: Optional[str] = None
    vin: Optional[str] = None
    psn: Optional[str] = None
    chassis_no: Optional[str] = None
    price: Optional[float] = None
    features: Optional[dict] = None
