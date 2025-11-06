from functools import lru_cache

import httpx
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from pydantic import BaseModel
from starlette.requests import Request

from insperion_api.core.constants.error_response import ErrorResponse
from insperion_api.settings.config import settings
from insperion_api.utils.common.custom_http_exception import CustomHTTPException
from insperion_api.utils.common.logger import logger


class JWKS(BaseModel):
    keys: list[dict[str, str]]


class JWTAuthorizationCredentials(HTTPAuthorizationCredentials):
    jwt_token: str
    header: dict[str, str]
    claims: dict[str, str | list[str] | int]
    signature: str
    message: str


@lru_cache(maxsize=5)
def get_jwks(user_pool_id: str) -> JWKS:
    endpoint = (
        f"https://cognito-idp.{user_pool_id.split('_')[0]}"
        f".amazonaws.com/{user_pool_id}/.well-known/jwks.json"
    )
    response = httpx.get(endpoint)
    if response.status_code != 200:
        raise CustomHTTPException(
            error_response=ErrorResponse.COGNITO_JWKS_FETCH_ERROR
        ).to_http_exception()
    jwks = JWKS.model_validate(response.json())
    return jwks


class JWTBearer(HTTPBearer):
    def __init__(self, jwks: JWKS | None = None, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def _load_jwks(self):
        user_pool_id = settings.cognito_user_pool_id
        logger.warning(
            "Using user_pool_id set in environment (COGNITO_USER_POOL_ID) instead of the config table"
        )
        return get_jwks(user_pool_id)

    async def __call__(self, request: Request):
        if self.jwks is None:
            self.jwks = await self._load_jwks()

        jwt_token = request.headers.get("Authorization")
        if not jwt_token:
            raise CustomHTTPException(
                error_response=ErrorResponse.NOT_AUTHENTICATED
            ).to_http_exception()

        try:
            jwt_token = jwt_token.split(" ")[1]  # the part after "Bearer"
            message, signature = jwt_token.rsplit(".", 1)

            claims = jwt.decode(jwt_token, self.jwks.model_dump())

            return JWTAuthorizationCredentials(
                jwt_token=jwt_token,
                header=jwt.get_unverified_header(jwt_token),
                claims=claims,
                signature=signature,
                message=message,
                scheme="Bearer",
                credentials=jwt_token,
            )

        except Exception as ex:
            logger.error(f"Error occurred during auth token verification: {ex}")
            raise CustomHTTPException(
                error_response=ErrorResponse.INVALID_JWT
            ).to_http_exception()


auth = JWTBearer()
