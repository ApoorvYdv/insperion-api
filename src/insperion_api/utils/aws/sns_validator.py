import base64
import datetime
import re
from asyncio import Lock
from typing import Union
from urllib.parse import urlparse

import httpx
from cachetools import TTLCache
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from insperion_api.core.constants.error_response import ErrorResponse
from insperion_api.core.schemas.payments.payment_request import (
    SNSNotification,
    SNSSubscriptionConfirmation,
)
from insperion_api.utils.common.custom_http_exception import CustomHTTPException
from insperion_api.utils.common.logger import logger

SNSMessage = Union[SNSSubscriptionConfirmation, SNSNotification]


NOTIFICATION_VALIDATION_KEYS = sorted(
    ["Message", "MessageId", "Timestamp", "TopicArn", "Type"]
)
SUBSCRIPTION_CONFIRMATION_VALIDATION_KEYS = sorted(
    ["Message", "MessageId", "SubscribeURL", "Timestamp", "Token", "TopicArn", "Type"]
)

ONE_DAY = 60 * 60 * 24
CERTIFICATE_CACHE: TTLCache[str, x509.Certificate] = TTLCache(maxsize=15, ttl=ONE_DAY)
CERTIFICATE_CACHE_LOCK = Lock()


def check_if_hostname_is_valid_sns_location(hostname: str) -> bool:
    return bool(re.match(r"^sns\.[^.]+\.amazonaws\.com$", hostname))


def check_if_url_scheme_is_https(url) -> bool:
    return url.scheme == "https"


async def get_x509_certificate(message: SNSMessage) -> x509.Certificate:
    url = message.SigningCertURL

    async with CERTIFICATE_CACHE_LOCK:
        if url in CERTIFICATE_CACHE:
            cert = CERTIFICATE_CACHE[url]
            now = datetime.datetime.now(datetime.UTC)
            if cert.not_valid_before_utc <= now <= cert.not_valid_after_utc:
                return cert
            else:
                CERTIFICATE_CACHE.pop(url)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=5.0)
            response.raise_for_status()
            cert_data = response.read()
        except httpx.HTTPError as e:
            logger.error(
                f"SNS Verification failed: Failed to fetch certificate from {url}: {str(e)}"
            )
            raise CustomHTTPException(
                ErrorResponse.CERTIFICATE_VERIFICATION_FAILURE,
                details={
                    "message": f"Failed to fetch certificate from {url}: {str(e)}"
                },
            )

    cert = x509.load_pem_x509_certificate(cert_data, default_backend())

    async with CERTIFICATE_CACHE_LOCK:
        CERTIFICATE_CACHE[url] = cert
    return cert


async def validate_message_signature(
    message: SNSMessage, validation_keys: list[str]
) -> bool:
    # Validate required fields
    for validation_key in validation_keys + ["SignatureVersion", "SigningCertURL"]:
        if getattr(message, validation_key, None) is None:
            logger.error(f"SNS Verification failed: missing key {validation_key}")
            raise CustomHTTPException(
                ErrorResponse.CERTIFICATE_VERIFICATION_FAILURE,
                details={"message": f"Missing key: {validation_key}"},
            ).to_http_exception()

    if message.SignatureVersion != "1":
        logger.error(
            f"SNS Verification failed: Invalid SignatureVersion: {message.SignatureVersion}"
        )
        raise CustomHTTPException(
            ErrorResponse.CERTIFICATE_VERIFICATION_FAILURE,
            details={
                "message": f"Invalid SignatureVersion: {message.SignatureVersion}"
            },
        ).to_http_exception()

    signing_url = urlparse(message.SigningCertURL)
    if not check_if_url_scheme_is_https(signing_url) or (
        signing_url.hostname
        and not check_if_hostname_is_valid_sns_location(signing_url.hostname)
    ):
        logger.error(
            f"SNS Verification failed: Invalid SigningCertURL: {message.SigningCertURL}"
        )
        raise CustomHTTPException(
            ErrorResponse.CERTIFICATE_VERIFICATION_FAILURE,
            details={"message": f"Invalid SigningCertURL: {message.SigningCertURL}"},
        ).to_http_exception()

    # Get public key
    cert: x509.Certificate = await get_x509_certificate(message)
    public_key = cert.public_key()
    if not isinstance(public_key, RSAPublicKey):
        logger.error(
            f"SNS Verification failed: Expected RSAPublicKey, got {type(public_key).__name__}"
        )
        raise CustomHTTPException(
            ErrorResponse.CERTIFICATE_VERIFICATION_FAILURE,
            details={
                "message": f"Expected RSAPublicKey, got {type(public_key).__name__}"
            },
        )
    key: RSAPublicKey = public_key
    try:
        key.verify(
            signature=get_signature(message),
            data=build_data(message, validation_keys),
            padding=padding.PKCS1v15(),
            algorithm=hashes.SHA1(),
        )
    except InvalidSignature:
        logger.error(
            "SNS Verification failed: Signature verification failed during key.verify call"
        )
        raise CustomHTTPException(
            ErrorResponse.CERTIFICATE_VERIFICATION_FAILURE,
            details={"message": "Signature verification failed"},
        )

    logger.info("Verified incoming SNS message successfully")

    return True  # If no exception, it's valid


async def verify_subscription_confirmation(
    message: SNSSubscriptionConfirmation,
) -> bool:
    return await validate_message_signature(
        message, SUBSCRIPTION_CONFIRMATION_VALIDATION_KEYS
    )


async def verify_notification(message: SNSNotification) -> bool:
    return await validate_message_signature(message, NOTIFICATION_VALIDATION_KEYS)


def get_signature(message: SNSMessage) -> bytes:
    return base64.b64decode(message.Signature)


def build_data(message: SNSMessage, validation_keys: list[str]) -> bytes:
    keys_to_hash = []
    for k in validation_keys:
        v = getattr(message, k)
        keys_to_hash.extend([k, v])
    return ("\n".join(keys_to_hash) + "\n").encode()
