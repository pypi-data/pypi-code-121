import datetime
import os
from abc import ABC, abstractmethod
from typing import Any

from azure.storage.blob import BlobSasPermissions, generate_blob_sas
from azure.storage.blob.aio import BlobClient, ContainerClient

try:
    from aiobotocore.session import get_session  # type: ignore

    HAS_AIOBOTOCORE = True
except ImportError:  # pragma: no cover
    HAS_AIOBOTOCORE = False


class Storage(ABC):
    def __init__(self, bucket_name, region_name) -> None:
        self.region_name = region_name
        self.bucket_name = bucket_name

    @abstractmethod
    def delete_object(self, key: str):
        pass

    @abstractmethod
    def generate_presigned_url(self, key: str, size: str, content_md5: str, **kwargs: Any):
        pass


class AsyncAmazonS3Storage(Storage):
    async def delete_object(self, key: str):
        self._check_if_installed_aiobotocore()

        session = get_session()
        async with session.create_client("s3", self.region_name) as client:
            await client.delete_object(Bucket=self.bucket_name, Key=key)

    async def generate_presigned_url(
        self, key: str, size: str, content_md5: str, **kwargs: Any
    ):
        self._check_if_installed_aiobotocore()

        headers = {"Content-Length": str(size), "Content-MD5": content_md5}
        session = get_session()
        async with session.create_client(
            "s3",
            region_name=self.region_name,
            endpoint_url=f"https://s3.{self.region_name}.amazonaws.com",
        ) as client:
            url = await client.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": key,
                    "ContentLength": size,
                    "ContentMD5": content_md5,
                },
            )

            return url, headers

    @staticmethod
    def _check_if_installed_aiobotocore():
        if not HAS_AIOBOTOCORE:  # pragma: no cover
            raise ImportError(
                "Can not get session from aiobotocore. " "Please install `aiobotocore>=1.4.0`"
            )


class AsyncAzureBlobStorage(Storage):
    def __init__(self, container_name: str, account_key: str, **kwargs: Any) -> None:
        connection_string = kwargs.get(
            "conn_str",
            os.environ.get("AZURE_STORAGE_CONNECTION_STRING"),
        )
        self.container_name = container_name
        self.client: ContainerClient = ContainerClient.from_connection_string(
            conn_str=connection_string, container_name=container_name
        )
        self.account_key = account_key

    async def delete_object(self, key: str):
        await self.client.delete_blobs(list(key))

    async def generate_presigned_url(
        self, key: str, size: str, content_md5: str, expiry: int = 1, **kwargs: Any
    ):
        headers = {
            "x-ms-version": "2021-04-10",
            "x-ms-blob-type": "BlockBlob",
            "Content-Type": "image/jpg",
        }
        blob_name = key.split("/")[-1]
        sas_token = generate_blob_sas(
            account_name="pbx2brian",
            container_name=self.container_name,
            blob_name=blob_name,
            account_key=self.account_key,
            permission=BlobSasPermissions(create=True, write=True),
            expiry=datetime.datetime.now() + datetime.timedelta(hours=expiry),
        )
        container_blob_url = self.client.get_blob_client(blob_name).url
        blob_client = BlobClient.from_blob_url(container_blob_url, credential=sas_token)

        return blob_client.url, headers
