from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, UploadFile

from insperion_api.core.controllers.common.config_wrappers.s3_config import S3Config
from insperion_api.utils.aws.async_aws_client import get_s3


class S3:
    def __init__(
        self,
        s3_client: Any = Depends(get_s3),
        s3_config: S3Config = Depends(),
    ):
        self.s3_client = s3_client
        self.s3_config = s3_config

    async def upload(
        self,
        key: str,
        file: UploadFile,
        metadata: Optional[dict] = None,
        content_type: Optional[str] = None,
    ) -> bool:
        try:
            async with self.s3_client as s3:
                await s3.upload_fileobj(
                    Fileobj=file,
                    Bucket=await self.s3_config.bucket("UPP", "GLOBAL"),
                    Key=key,
                    ExtraArgs=(
                        {"Metadata": metadata, "ContentType": content_type}
                        if metadata
                        else None
                    ),
                )
            return True
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to upload file: {str(e)}"
            )

    async def delete(self, filename: str) -> Dict[str, str]:
        try:
            async with self.s3_client as s3:
                await s3.delete_object(
                    Bucket=await self.s3_config.bucket("UPP", "GLOBAL"), Key=filename
                )
            return {"message": "File deleted successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to delete file: {str(e)}"
            )

    async def key_exists(self, key: str) -> bool:
        try:
            async with self.s3_client as s3:
                results = await s3.list_objects_v2(
                    Bucket=await self.s3_config.bucket("UPP", "GLOBAL"), Prefix=key
                )
            if "Contents" in results:
                for obj in results["Contents"]:
                    if obj["Key"] == key:
                        return True
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to check file existence: {str(e)}"
            )
        return False

    async def generate_presigned_post(
        self, key: str, content_type: Optional[str] = None, expiration: int = 3600
    ) -> Dict[str, str]:
        try:
            async with self.s3_client as s3:
                response = await s3.generate_presigned_post(
                    Bucket=await self.s3_config.bucket("UPP", "GLOBAL"),
                    Key=key,
                    ExpiresIn=expiration,
                    Fields={"Content-Type": content_type} if content_type else None,
                    Conditions=(
                        [{"Content-Type": content_type}] if content_type else None
                    ),
                )
            return response
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate presigned post URL: {str(e)}",
            )

    async def get_signed_url(self, key: str, expiration: int = 3600) -> str:
        try:
            async with self.s3_client as s3:
                url = await s3.generate_presigned_url(
                    ClientMethod="get_object",
                    Params={
                        "Bucket": await self.s3_config.bucket("UPP", "GLOBAL"),
                        "Key": key,
                    },
                    ExpiresIn=expiration,
                )
            return url
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to generate presigned URL: {str(e)}"
            )

    async def list_files(self, key: str) -> list:
        try:
            async with self.s3_client as s3:
                results = await s3.list_objects_v2(
                    Bucket=await self.s3_config.bucket("UPP", "GLOBAL"), Prefix=key
                )
            if "Contents" in results:
                return results["Contents"]

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to check files existence: {str(e)}"
            )
        return []

    async def get_metadata(self, key: str) -> list:
        async with self.s3_client as s3:
            response = await s3.head_object(
                Bucket=await self.s3_config.bucket("UPP", "GLOBAL"), Key=key
            )
            return response.get("Metadata", {})

    async def get_file_obj(self, key):
        async with self.s3_client as s3:
            response = await s3.get_object(
                Bucket=await self.s3_config.bucket("UPP", "GLOBAL"), Key=key
            )
            content = await response["Body"].read()
            return content.decode("utf-8")

    async def put_object(
        self, key: str, body: str | bytes, content_type: Optional[str] = None
    ):
        async with self.s3_client as s3:
            await s3.put_object(
                Bucket=await self.s3_config.bucket("UPP", "GLOBAL"),
                Key=key,
                Body=body,
                **{
                    k: v
                    for k, v in {"ContentType": content_type}.items()
                    if v is not None
                },
            )
