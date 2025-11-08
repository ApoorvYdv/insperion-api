from typing import Annotated

from fastapi import Depends

from insperion_api.core.constants.error_response import ErrorResponse
from insperion_api.core.controllers.developer.config_controller import ConfigController
from insperion_api.utils.common.custom_http_exception import CustomHTTPException


class InspectionConfig:
    CONFIG_SECTION = "inspection"

    def __init__(
        self, config_controller: Annotated[ConfigController, Depends()]
    ) -> None:
        self.config_controller = config_controller

    async def _get_value(self, key: str):
        configs = await self.config_controller.get_configs(self.CONFIG_SECTION)
        config_map = {c.config_key: c.config_value for c in configs}
        if key not in config_map:
            raise CustomHTTPException(
                ErrorResponse.CONFIG_KEY_NOT_FOUND
            ).to_http_exception()
        return config_map[key]

    @property
    async def flows(self):
        return await self._get_value("flows")
