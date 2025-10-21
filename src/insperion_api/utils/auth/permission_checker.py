import asyncio

from cachetools import TTLCache
from fastapi import Depends
from sqlalchemy import select

from insperion_api.core.constants.error_response import ErrorResponse
from insperion_api.core.models.agency.agency import (
    Permission,
    Role,
    RolePermissionMapper,
)
from insperion_api.utils.auth.auth_token_decoder import (
    JWTAuthorizationCredentials,
    auth,
)
from insperion_api.utils.aws.async_aws_client import get_cognito
from insperion_api.utils.common.custom_http_exception import CustomHTTPException
from insperion_api.utils.database.connections import get_async_engine
from insperion_api.utils.database.session_context_manager import session_context

permissions_cache = TTLCache(maxsize=100, ttl=600)
permissions_cache_lock = asyncio.Lock()


async def fetch_permissions(role_names: str, agency: str):
    """
    Fetch permissions for a semicolon-separated string of roles, e.g. "admin;helpdesk".
    """
    async with permissions_cache_lock:
        if role_names in permissions_cache:
            return permissions_cache[role_names]

    role_list = [r.strip() for r in role_names.split(";") if r.strip()]

    async with session_context(get_async_engine(), agency) as session:
        if not role_list:
            permission_list = []
        else:
            roles_subquery = select(Role.id).where(Role.name.in_(role_list))

            result = await session.scalars(
                select(Permission)
                .join(
                    RolePermissionMapper,
                    RolePermissionMapper.permission_id == Permission.id,
                )
                .where(RolePermissionMapper.role_id.in_(roles_subquery))
                .distinct()
            )
            permissions = result.all()
            permission_list = [
                (permission.operation, permission.resource)
                for permission in permissions
            ]

    async with permissions_cache_lock:
        permissions_cache[role_names] = permission_list

    return permission_list


class RequiredPermissions:
    """
    Protects a route by checking if the authenticated user has any of the required permissions to access it.

    Example usage as a dependency in a route:
    ```
    credentials: JWTAuthorizationCredentials = Depends(
        RequiredPermissions([("update", "config")])
    )
    ```
    """

    def __init__(self, required_permissions: list[tuple[str, str]] = []) -> None:
        self.required_permissions = required_permissions

    async def __call__(
        self,
        credentials: JWTAuthorizationCredentials = Depends(auth),
        cognito_client=Depends(get_cognito),
    ):
        if len(self.required_permissions) == 0:
            return credentials

        user_attributes = await cognito_client.get_user(
            AccessToken=credentials.jwt_token
        )
        user_attributes_dict = {
            attribute["Name"]: attribute["Value"]
            for attribute in user_attributes["UserAttributes"]
        }

        user_permissions = await fetch_permissions(
            user_attributes_dict.get("custom:roles", ""),
            agency="durango",  # TODO: temporary
        )

        if all(
            permission not in user_permissions
            for permission in self.required_permissions
        ):
            raise CustomHTTPException(ErrorResponse.NOT_AUTHORIZED).to_http_exception()

        return credentials
