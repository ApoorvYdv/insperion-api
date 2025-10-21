from collections.abc import AsyncGenerator
from enum import Enum

import aioboto3
from botocore.config import Config

from insperion_api.settings.config import get_env


class AWSServices(Enum):
    S3 = "s3"
    SNS = "sns"
    COGNITO = "cognito-idp"
    LAMBDA = "lambda"
    KMS = "kms"
    SES = "ses"


async def get_client(service: str):
    """Creates and returns an async client for the specified AWS service."""
    session = aioboto3.Session()
    aws_credentials = {
        k: v
        for k, v in {
            "aws_access_key_id": get_env("AWS_ACCESS_KEY_ID"),
            "aws_secret_access_key": get_env("AWS_SECRET_ACCESS_KEY"),
            "aws_session_token": get_env("AWS_SESSION_TOKEN"),
            "region_name": get_env("AWS_REGION"),
        }.items()
        if v
    }
    if service == AWSServices.S3.value:
        aws_credentials["config"] = Config(signature_version="s3v4")
    async with session.client(
        service,
        **aws_credentials,
    ) as client:
        yield client


async def get_s3() -> AsyncGenerator:
    """Returns an asynchronous generator for the S3 client."""
    async for s3_client in get_client(AWSServices.S3.value):
        yield s3_client


async def get_sns() -> AsyncGenerator:
    """Returns an asynchronous generator for the SNS client."""
    async for sns_client in get_client(AWSServices.SNS.value):
        yield sns_client


async def get_cognito() -> AsyncGenerator:
    """Returns an asynchronous generator for the Cognito client."""
    async for cognito_client in get_client(AWSServices.COGNITO.value):
        yield cognito_client


async def get_lambda() -> AsyncGenerator:
    """Returns an asynchronous generator for the Lambda client."""
    async for lambda_client in get_client(AWSServices.LAMBDA.value):
        yield lambda_client


async def get_kms() -> AsyncGenerator:
    """Returns an asynchronous generator for the KMS client."""
    async for kms_client in get_client(AWSServices.KMS.value):
        yield kms_client


async def get_ses() -> AsyncGenerator:
    """Returns an asynchronous generator for the SES client."""
    async for ses_client in get_client(AWSServices.SES.value):
        yield ses_client
