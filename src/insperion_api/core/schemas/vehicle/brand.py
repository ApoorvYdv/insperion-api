from pydantic import BaseModel


class AddVehicleBrandRequest(BaseModel):
    name: str
    country: str
    established_year: int


class UpdateVehicleBrandRequest(BaseModel):
    name: str | None
    country: str | None
    established_year: int | None
