from typing import Annotated

from fastapi import Depends

from insperion_api.core.controllers.developer.config_controller import ConfigController


class InspectionConfig:
    CONFIG_SECTION = "inspection"

    def __init__(
        self, config_controller: Annotated[ConfigController, Depends()]
    ) -> None:
        self.config_controller = config_controller

    async def _get_value(self, key: str):
        configs = await self.config_controller.get_configs(self.CONFIG_SECTION)
        config_map = {c.config_key: c.config_value for c in configs}
        return config_map.get(key)

    @property
    async def flows(self):
        return await self._get_value("flows")
