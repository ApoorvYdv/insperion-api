from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import ValidationError

from insperion_api.core.constants.error_response import ErrorResponse
from insperion_api.routers.developer.config import config_router
from insperion_api.routers.inspection import inspection_router
from insperion_api.settings.config import settings
from insperion_api.utils.common.pydantic_error_parser import build_error_response

description = """
Insperion API
"""

app = FastAPI(
    title="Insperion API",
    description=description,
    version="0.0.1",
    responses={404: {"description": "Not found"}},
)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Access-Control-Allow-Headers",
        "Content-Type",
        "Authorization",
        "Access-Control-Allow-Origin",
        "Client",
        "ngrok-skip-browser-warning",
    ],
    expose_headers=["Content-Disposition"],
)


@app.exception_handler(RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = build_error_response(exc)

    return JSONResponse(
        status_code=ErrorResponse.VALIDATION_ERROR.value.status_code,
        content={
            "errors": errors,
            "detail": ErrorResponse.VALIDATION_ERROR.value.message,
        },
    )


@app.exception_handler(Exception)
async def internal_server_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=ErrorResponse.INTERNAL_SERVER_ERROR.value.status_code,
        content={"detail": ErrorResponse.INTERNAL_SERVER_ERROR.value.message},
    )


app.include_router(inspection_router)
app.include_router(config_router)
