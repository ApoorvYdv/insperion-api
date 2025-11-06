from typing import Optional

from pydantic import BaseModel


class AddVehicleModelRequest(BaseModel):
    brand_id: int
    model_name: str
    year_launched: int
    body_type: str
    seating_capacity: int


class UpdateVehicleModelRequest(BaseModel):
    brand_id: int
    model_name: Optional[str] = None
    year_launched: Optional[int] = None
    body_type: Optional[str] = None
    seating_capacity: Optional[int] = None
