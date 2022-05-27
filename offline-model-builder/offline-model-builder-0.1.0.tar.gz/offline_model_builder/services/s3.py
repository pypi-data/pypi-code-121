import os
from typing import Union, BinaryIO, Dict, Any, ClassVar

import boto3


class S3Managed:

    def __init__(
            self,
            region_name: str,
            aws_access_key_id: str,
            aws_secret_access_key: str,
    ):
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.client = boto3.client(
            "s3",
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

    @property
    def get_aws_access_key_id(self) -> str:
        """Get current aws access key id
        :return: string aws access key id
        """
        return self.aws_access_key_id

    @property
    def get_region_name(self) -> str:
        """Get current aws region name
        :return: string region name
        """
        return self.region_name

    @property
    def get_aws_secret_access_key(self) -> str:
        """Get current aws secret access key
        :return: string aws secret access key
        """
        return self.aws_secret_access_key

    @property
    def get_aws_cred(self) -> Dict[str, Any]:
        """Get all current credential and return ans dictionary
        :return: dictionary object
        """
        return {
            "region_name": self.region_name,
            "aws_access_key_id": self.aws_access_key_id,
            "aws_secret_access_key": self.aws_secret_access_key,
        }

    def __str__(self):
        return "S3Managed({}, {}, {})".format(self.region_name, self.aws_access_key_id, self.aws_secret_access_key)

    @classmethod
    def read_from_env_variable(
            cls,
    ) -> ClassVar:
        """Return current s3 managed class object by read using env variable
        :return: current object class
        """
        region_name = os.getenv("AWS_ACCESS_KEY_ID")
        aws_access_key_id = os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_secret_access_key = os.getenv("AWS_REGION_NAME")
        return cls(region_name, aws_access_key_id, aws_secret_access_key)

    @classmethod
    def from_config(
            cls,
            region_name: str,
            aws_access_key_id: str,
            aws_secret_access_key: str,
    ) -> ClassVar:
        """Get current s3 object based on specified parameters
        :param region_name: string region name
        :param aws_access_key_id: string access key
        :param aws_secret_access_key: string secret key
        :return: current object class
        """
        return cls(region_name, aws_access_key_id, aws_secret_access_key)

    def write_files(
            self,
            files: Union[bytes, BinaryIO],
            bucket_name: str,
            file_name: str,
    ) -> Dict[str, Any]:
        """Upload file to s3 object
        :param files: bytes data types
        :param bucket_name: string bucket name
        :param file_name: string file name in s3
        :return:
        """
        return self.client.put_object(
            Body=files,
            Bucket=bucket_name,
            Key=file_name,
        )

    def read_files(
            self,
            bucket_name: str,
            file_name: str
    ) -> bytes:
        """Read value from s3 and return value as bytes
        :param bucket_name: string bucket name
        :param file_name: file name is s3
        :return: string value
        """
        file_bytes = self.client.get_object(Bucket=bucket_name, Key=file_name)
        if v := file_bytes.get("Body", None):
            return v.read()

        return bytes()
