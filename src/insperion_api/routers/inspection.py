from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from insperion_api.core.controllers.inspection_controller import InspectionController
from insperion_api.utils.common.logger import logger

inspection_router = APIRouter(prefix="/v1/inspect", tags=["inspect"])


@inspection_router.websocket("")
async def inspect(
    request: WebSocket, controller: Annotated[InspectionController, Depends()]
):
    await request.accept()
    try:
        while True:
            data = await request.receive_text()

            results_json = await controller.inspect(data)

            await request.send_json(results_json)
    except WebSocketDisconnect:
        logger.warning("Client disconnected")

    except Exception as exc:
        logger.error(f"An error occurred: {exc}")
        await request.close(code=1011, reason=str(exc))
