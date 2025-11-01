from pydantic import BaseModel


class AddVehicleBrand(BaseModel):
    name: str
    country: str
    established_year: int


class UpdateVehicleBrand(BaseModel):
    name: str | None
    country: str | None
    established_year: int | None
