"""
Error codes and their corresponding details.
This file contains all error code definitions used across the application
"""

from dataclasses import dataclass
from enum import Enum

from fastapi import status


@dataclass(frozen=True)
class ErrorDetail:
    """Immutable error detail configuration."""

    message: str
    status_code: int = status.HTTP_400_BAD_REQUEST
    error_type: str = "BUSINESS_ERROR"


class ErrorResponse(Enum):
    """Error codes with their corresponding details."""

    # Validation errors
    MISSING_REQUIRED_FIELD = ErrorDetail("Missing required field: {field}")
    VALIDATION_ERROR = ErrorDetail(
        message="Input validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )

    # Generic errors
    UNKNOWN_ERROR = ErrorDetail(
        message="Unknown error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_type="SYSTEM_ERROR",
    )
    INTERNAL_SERVER_ERROR = ErrorDetail(
        message="Internal server error",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_type="SYSTEM_ERROR",
    )

    # Authentication errors
    INVALID_JWT = ErrorDetail(
        message="Invalid JWT",
        status_code=status.HTTP_401_UNAUTHORIZED,
        error_type="AUTH_ERROR",
    )
    NOT_AUTHENTICATED = ErrorDetail(
        message="Not Authenticated",
        status_code=status.HTTP_401_UNAUTHORIZED,
        error_type="AUTH_ERROR",
    )
    NOT_AUTHORIZED = ErrorDetail(
        message="Not Authorized",
        status_code=status.HTTP_401_UNAUTHORIZED,
        error_type="AUTH_ERROR",
    )
    COGNITO_JWKS_FETCH_ERROR = ErrorDetail(
        message="Unable to fetch JWKS of default Cognito user pool",
        status_code=status.HTTP_401_UNAUTHORIZED,
        error_type="AUTH_ERROR",
    )
    # Resource errors
    RESOURCE_NOT_FOUND = ErrorDetail(
        message="Resource not found",
        status_code=status.HTTP_404_NOT_FOUND,
        error_type="RESOURCE_ERROR",
    )
    RESOURCE_ALREADY_EXISTS = ErrorDetail(
        message="Resource already exists",
        status_code=status.HTTP_409_CONFLICT,
        error_type="RESOURCE_ERROR",
    )

    # Rate limiting
    RATE_LIMIT_EXCEEDED = ErrorDetail(
        message="Rate limit exceeded",
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        error_type="RATE_LIMIT_ERROR",
    )

    # User Management Errors
    COGNITO_API_ERROR = ErrorDetail("Invalid Request: {error_code}")
