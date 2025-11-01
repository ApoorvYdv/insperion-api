from typing import Any, Dict, Optional

from fastapi import HTTPException

from insperion_api.core.constants.error_response import ErrorResponse


class CustomHTTPException(Exception):
    """Custom business logic exception."""

    def __init__(
        self,
        error_response: ErrorResponse,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[str] = None,
    ):
        self.error_response = error_response
        self.details = details or {}
        self.context = context

        # Format message with any placeholders if present
        message = error_response.value.message
        try:
            message = message.format(**self.details)
        except KeyError:
            # fallback: don't fail if details are missing
            pass
        self.message = message

        super().__init__(message)

    def to_http_exception(self) -> HTTPException:
        """Convert to FastAPI HTTPException."""
        raise HTTPException(
            status_code=self.error_response.value.status_code,
            detail=str(self.message),
        )
