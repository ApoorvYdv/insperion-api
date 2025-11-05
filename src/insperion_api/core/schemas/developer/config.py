from typing import Optional

from pydantic import BaseModel


class AddConfigRequest(BaseModel):
    config_section: str
    config_key: str
    config_value: dict
    config_description: str
    is_exposable: bool


class UpdateConfigRequest(BaseModel):
    config_section: Optional[str] = None
    config_key: Optional[str] = None
    config_value: Optional[dict] = None
    config_description: Optional[str] = None
    is_exposable: Optional[bool] = None
