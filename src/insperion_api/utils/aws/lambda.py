import json
from enum import Enum
from typing import Any, Dict, Optional

from fastapi import Depends

from insperion_api.core.constants.error_response import ErrorResponse
from insperion_api.core.controllers.common.config_wrappers.lambda_config import (
    LambdaConfig,
)
from insperion_api.utils.aws.async_aws_client import get_lambda
from insperion_api.utils.common.custom_http_exception import CustomHTTPException
from insperion_api.utils.common.logger import logger


class InvocationType(str, Enum):
    REQUEST_RESPONSE = "RequestResponse"
    EVENT = "Event"


class LambdaException(Exception):
    def __init__(
        self, status_code: int = 400, function_error: str = "Error", message: str = ""
    ):
        self.status_code = status_code
        self.function_error = function_error
        self.message = message or "An error occurred in Lambda execution."
        super().__init__(self.message)


class Lambda:
    def __init__(
        self,
        lambda_client: Any = Depends(get_lambda),
        lambda_config: LambdaConfig = Depends(),
    ):
        self.lambda_client = lambda_client
        self.lambda_config = lambda_config

    async def invoke(
        self,
        payload: Dict[str, Any],
        invocation_type: str = InvocationType.REQUEST_RESPONSE.value,
    ) -> Optional[Dict[str, Any]]:
        """
        Asynchronously invoke an AWS Lambda function.
        """
        # Convert payload to JSON
        try:
            payload_json = json.dumps(payload).encode("utf-8")

            # Validate invocation type
            if invocation_type not in [item.value for item in InvocationType]:
                raise ValueError(f"Invalid invocation type: {invocation_type}")

            # Invoke Lambda function asynchronously
            response = await self.lambda_client.invoke(
                FunctionName=await self.lambda_config.html_to_pdf_arn("UPP", "GLOBAL"),
                Payload=payload_json,
                InvocationType=invocation_type,
            )
            # Read and process response payload
            response_payload = await response["Payload"].read()
            response_data = json.loads(response_payload.decode("utf-8"))

            return self._handle_lambda_response(response_data, invocation_type)
        except Exception as err:
            logger.error("Lambda invocation failed", str(err))
            raise CustomHTTPException(
                ErrorResponse.LAMBDA_INVOCATION_FAILED
            ).to_http_exception()

    def _handle_lambda_response(
        self, response: Dict[str, Any], invocation_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Handles the Lambda response depending on the invocation type.
        """
        status_code = response.get("statusCode", 400)
        if status_code in (200, 204, 202):
            return response

        function_error = response.get("FunctionError", "")
        logger.error(function_error)

        if invocation_type == InvocationType.REQUEST_RESPONSE.value:
            raise CustomHTTPException(
                ErrorResponse.REQUEST_INVOCATION_FAILED,
            ).to_http_exception()

        elif invocation_type == InvocationType.EVENT.value:
            raise CustomHTTPException(
                ErrorResponse.EVENT_INVOCATION_FAILED
            ).to_http_exception()
