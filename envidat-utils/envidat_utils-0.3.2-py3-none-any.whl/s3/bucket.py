import os
import logging
import json
import mimetypes
import boto3

from typing import Any, NoReturn, Union
from pathlib import Path
from io import BytesIO
from textwrap import dedent
from botocore.config import Config
from botocore.exceptions import ClientError

from envidat.s3 import exceptions
from envidat.utils import get_url


log = logging.getLogger(__name__)


class Bucket:
    """
    Class to handle S3 bucket transactions.
    Handles boto3 exceptions with custom exception classes.
    """

    _AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY")
    _AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_KEY")
    _AWS_ENDPOINT = os.getenv("AWS_ENDPOINT")
    _AWS_REGION = os.getenv("AWS_REGION", default="")

    def __init__(
        self, bucket_name: str = None, is_new: bool = False, is_public: bool = False
    ) -> NoReturn:
        """
        Init the Bucket object.

        :param bucket_name: Name of the bucket.
        :param is_new: If true, creates a new bucket.
        :param is_public: If true, makes the bucket public on creation.
        """

        if None in [Bucket._AWS_ACCESS_KEY_ID, Bucket._AWS_SECRET_ACCESS_KEY]:
            missing_vars = {"AWS_ACCESS_KEY", "AWS_SECRET_KEY"} - set(os.environ)
            if not missing_vars:
                log.info(
                    "Environment variables set after Bucket class import. "
                    "Re-configuring Bucket with specified environment variables."
                )
                Bucket.config(
                    os.getenv("AWS_ACCESS_KEY"),
                    os.getenv("AWS_SECRET_KEY"),
                    endpoint=os.getenv("AWS_ENDPOINT"),
                    region=os.getenv("AWS_REGION", default=""),
                )

        log.debug(
            "S3 Bucket object instantiated. "
            f"Access key: {Bucket._AWS_ACCESS_KEY_ID} | "
            f"Secret key: {Bucket._AWS_SECRET_ACCESS_KEY} | "
            f"Endpoint: {Bucket._AWS_ENDPOINT} | "
            f"Region: {Bucket._AWS_REGION} | "
            f"is_new: {is_new} | "
            f"is_public: {is_public}"
        )
        # Ensure credentials are configured
        if not Bucket._AWS_ACCESS_KEY_ID or not Bucket._AWS_SECRET_ACCESS_KEY:
            log.error("Bucket instantiated without access key and secret key set.")
            raise TypeError(
                "AWS Access Key ID and AWS Secret Access Key must be configured. "
                "Set them with environment variables AWS_ACCESS_KEY and AWS_ACCESS_KEY "
                "or with Bucket.config(access_key, secret_key, endpoint, region)"
            )
        if bucket_name is None:
            log.debug("Getting bucket name from environment variable.")
            self.bucket_name = os.getenv("AWS_BUCKET_NAME")
        else:
            self.bucket_name = bucket_name

        self.is_public = is_public

        if is_new:
            self.create()

    @classmethod
    def config(
        cls, access_key: str, secret_key: str, endpoint: str = None, region: str = None
    ) -> NoReturn:
        """
        Config the bucket connection parameters before init.

        :param access_key: AWS_ACCESS_KEY_ID.
        :param secret_key: AWS_SECRET_ACCESS_KEY.
        :param endpoint: Endpoint for the S3, if not AWS.
        :param region: AWS_REGION.
        """
        cls._AWS_ACCESS_KEY_ID = access_key
        cls._AWS_SECRET_ACCESS_KEY = secret_key
        cls._AWS_ENDPOINT = endpoint
        cls._AWS_REGION = region

    @staticmethod
    def get_boto3_resource() -> NoReturn:
        """
        Configure boto3 resource object.
        """

        log.debug("Accessing boto3 resource.")
        return boto3.resource(
            "s3",
            aws_access_key_id=Bucket._AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Bucket._AWS_SECRET_ACCESS_KEY,
            endpoint_url=Bucket._AWS_ENDPOINT,
            region_name=Bucket._AWS_REGION,
            config=Config(signature_version="s3v4"),
        )

    @staticmethod
    def get_boto3_client() -> NoReturn:
        """
        Cofigure boto3 client object.
        """

        log.debug("Accessing boto3 client.")
        return boto3.client(
            "s3",
            aws_access_key_id=Bucket._AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Bucket._AWS_SECRET_ACCESS_KEY,
            endpoint_url=Bucket._AWS_ENDPOINT,
            region_name=Bucket._AWS_REGION,
            config=Config(signature_version="s3v4"),
        )

    def _handle_boto3_client_error(self, e: ClientError, key=None) -> NoReturn:
        """
        Handle boto3 ClientError.
        The exception type returned from the server is nested here.
        Refer to exceptions.py

        :param e: The ClientError to handle
        :param key: The S3 object key. Default None.
        """
        error_code: str = e.response.get("Error").get("Code")

        log.debug(e.response)

        if error_code == "AccessDenied":
            raise exceptions.BucketAccessDenied(self.bucket_name)
        elif error_code == "NoSuchBucket":
            raise exceptions.NoSuchBucket(self.bucket_name)
        elif error_code == "NoSuchKey":
            raise exceptions.NoSuchKey(key, self.bucket_name)
        elif error_code == "BucketAlreadyExists":
            raise exceptions.BucketAlreadyExists(self.bucket_name)
        elif error_code == "NoSuchCORSConfiguration":
            raise exceptions.NoSuchCORSConfiguration(self.bucket_name)
        else:
            raise exceptions.UnknownBucketException(self.bucket_name, e)

    def _raise_file_not_found(self, file_path: str, is_dir: bool = False) -> NoReturn:
        """
        Raise error if expected file not found on disk.

        :param file_path: The path to the expected file.
        :param is_dir: True if path is a directory.
        """

        msg = (
            f"Referenced {'directory' if is_dir else 'file'} "
            f"not found on disk: {file_path}"
        )
        log.error(msg)
        raise FileNotFoundError(msg)

    def _raise_parameter_error(self, param_name, value) -> NoReturn:
        """
        Raise error if incorrect parameters are provided.

        :param param_name: The parameter name.
        :param value: The parameter value.
        """

        if value is None:
            msg = f"A value must be set for parameter {param_name}"
        else:
            msg = f"Invalid value for parameter {param_name}: {value}"
        log.error(msg)
        raise ValueError(msg)

    def create(self) -> "boto3.resource.Bucket":
        """
        Create the S3 bucket on the endpoint.
        Method may be called directly to manipulate the boto3 Bucket object.

        :return: A boto3 Bucket object.
        """

        resource = Bucket.get_boto3_resource()

        try:
            log.info(f"Creating bucket named {self.bucket_name}")
            bucket = resource.create_bucket(
                ACL="public-read" if self.is_public else "private",
                Bucket=self.bucket_name,
                CreateBucketConfiguration={
                    "LocationConstraint": f"{Bucket._AWS_REGION}"
                },
                ObjectLockEnabledForBucket=False,
            )
            log.debug("Bucket created successfully")
            return bucket
        except ClientError as e:
            self._handle_boto3_client_error(e)

    def get(
        self,
        key: str,
        response_content_type: str = None,
        response_encoding: str = "utf-8",
    ) -> (Any, dict):
        """
        Get an object from the bucket into a memory object.
        Defaults to utf-8 decode, unless specified.

        :param key: The key, i.e. path within the bucket to get.
        :param response_content_type: Content type to enforce on the response.

        :return: tuple of decoded data and a dict containing S3 object metadata.
        """

        resource = Bucket.get_boto3_resource()
        s3_object = resource.Object(self.bucket_name, key)

        try:
            log.info(f"Getting S3 object with key {key}")
            if response_content_type:
                response = s3_object.get(ResponseContentType=response_content_type)
            else:
                response = s3_object.get()

            log.debug(
                f"Reading and decoding returned data with encoding {response_encoding}"
            )
            data = response.get("Body").read().decode(response_encoding)
            metadata: dict = response.get("Metadata")

            return data, metadata

        except ClientError as e:
            self._handle_boto3_client_error(e, key=key)

    def put(
        self,
        key: str,
        data: Union[str, bytes],
        content_type: str = None,
        metadata: dict = {},
    ) -> dict:
        """
        Put an in memory object into the bucket.

        :param key: The key, i.e. path within the bucket to store as.
        :param data: The data to store, can be bytes or string.
        :param content_type: The mime type to store the data as.
            E.g. important for binary data or html text.
        :param metadata: Dictionary of metadata.
            E.g. timestamp or organisation details as string type.

        :return: Response dictionary from S3.
        """

        resource = Bucket.get_boto3_resource()
        s3_object = resource.Object(self.bucket_name, key)

        try:
            log.info(
                "Uploading S3 object with: "
                f"Key: {key} | "
                f"ContentType: {content_type} | "
                f"Metadata: {metadata}"
            )
            if content_type:
                response = s3_object.put(
                    Body=data, ContentType=content_type, Key=key, Metadata=metadata
                )
            else:
                response = s3_object.put(Body=data, Key=key, Metadata=metadata)
            return response

        except ClientError as e:
            self._handle_boto3_client_error(e, key=key)

    def delete(self, key: str) -> dict:
        """
        Delete specified object of a given key.

        :param key: The key, i.e. path within the bucket to delete.

        :return: Response dictionary from S3.
        """

        client = Bucket.get_boto3_client()

        try:
            log.info(f"Deleting S3 object with key: {key}")
            response = client.delete_object(Bucket=self.bucket_name, Key=key)
            return response

        except ClientError as e:
            self._handle_boto3_client_error(e, key=key)

    def upload_file(self, key: str, local_filepath: Union[str, Path]) -> bool:
        """
        Upload a local file to the bucket.
        Transparently manages multipart uploads.

        :param key: The key, i.e. path within the bucket to store under.
        :param local_filepath: Path string or Pathlib object to upload.

        :return: True if success, False is failure.
        """

        resource = Bucket.get_boto3_resource()
        s3_object = resource.Object(self.bucket_name, key)

        file_path = Path(local_filepath).resolve()
        if not file_path.is_file():
            self._raise_file_not_found(file_path)
        else:
            file_path = str(file_path)
        log.debug(f"File to upload: {file_path}")

        log.debug("Guessing file mimetype")
        mimetype, _ = mimetypes.guess_type(file_path)
        if mimetype is None:
            log.debug("Failed to guess mimetype, setting to application/octet-stream")
            mimetype = "application/octet-stream"

        try:
            log.info(f"Uploading to S3 from file: File Path: {file_path} | Key: {key}")
            s3_object.upload_file(file_path, ExtraArgs={"ContentType": mimetype})
            return True

        except ClientError as e:
            self._handle_boto3_client_error(e, key=key)

        return False

    def download_file(self, key: str, local_filepath: Union[str, Path]) -> bool:
        """
        Download S3 object to a local file.
        Transparently manages multipart downloads.

        :param key: The key, i.e. path within the bucket to store under.
        :param local_filepath: Path string or Pathlib object to download to.

        :return: True if success, False is failure.
        """

        resource = Bucket.get_boto3_resource()
        s3_object = resource.Object(self.bucket_name, key)

        file_path = Path(local_filepath).resolve()
        if not file_path.parent.is_dir():
            self._raise_file_not_found(file_path, is_dir=True)
        else:
            file_path = str(file_path)

        try:
            log.info(
                f"Downloading from S3 to file: Key: {key} | File Path: {file_path}"
            )
            s3_object.download_file(file_path)
            return True

        except ClientError as e:
            self._handle_boto3_client_error(e, key=key)

        return False

    def configure_static_website(
        self,
        index_file: str = "index.html",
        error_file: str = "error.html",
        include_icon: bool = True,
    ) -> bool:
        """
        Add static website hosting config to an S3 bucket.

        :param index_file: Name of index html file displaying page content.
        :param error_file: Name of error html file displaying error content.
        :param include_icon: Include the envidat favicon.ico for the bucket.

        :return: True if success, False is failure.

        Note: WARNING this will set all data to public read policy.
        """

        client = Bucket.get_boto3_client()

        try:
            log.debug("Setting public read access policy for static website.")
            public_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicRead",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{self.bucket_name}/*",
                    }
                ],
            }
            bucket_policy = json.dumps(public_policy)
            client.put_bucket_policy(Bucket=self.bucket_name, Policy=bucket_policy)
            log.info("Public read access policy set for static website.")

            log.debug("Setting S3 static website configuration...")
            client.put_bucket_website(
                Bucket=self.bucket_name,
                WebsiteConfiguration={
                    "ErrorDocument": {
                        "Key": error_file,
                    },
                    "IndexDocument": {
                        "Suffix": index_file,
                    },
                },
            )

            if include_icon:
                log.debug("Adding envidat favicon.ico to bucket root")
                icon = get_url("https://envidat.ch/favicon.ico").content
                self.put("favicon.ico", icon, content_type="image/x-icon")

            log.info(f"Static website configured for bucket: {self.bucket_name}")

            return True

        except ClientError as e:
            self._handle_boto3_client_error(e)

        return False

    def generate_index_html(
        self, title: str, file_list: Union[list, str], index_file: str = "index.html"
    ) -> BytesIO:
        """
        Write index file to root of S3 bucket, with embedded S3 download links.

        :param title: HTML title tag for page.
        :param file_list: List of file name to generate access urls for.
        :param index_file: Name of index html file displaying page content.

        :return: Response dictionary from index file upload.
        """

        if isinstance(file_list, str):
            log.debug(f"Converting string file_list into list: {file_list}")
            file_list = [file_list]

        buf = BytesIO()

        # Start HTML
        html_block = dedent(
            f"""
            <html>
            <head>
            <meta charset="utf-8">
            <title>{title}</title>
            </head>
            <body>
            """
        ).strip()
        log.debug(f"Writing start HTML block to buffer: {html_block}")
        buf.write(html_block.encode("utf_8"))

        # Files
        log.info("Iterating file list to write S3 links to index.")
        for file_name in file_list:
            log.debug(f"File name: {file_name}")
            html_block = dedent(
                f"""
                <div class='flex py-2 xs6'>
                <a href='https://{self.bucket_name}.s3-zh.os.switch.ch/{file_name}'>
                    https://{self.bucket_name}.s3-zh.os.switch.ch/{file_name}
                </a>
                </div>"""
            )
            log.debug(f"Writing file link HTML to buffer: {html_block}")
            buf.write(html_block.encode("utf_8"))

        # Close
        html_block = dedent(
            """
            </body>
            </html>"""
        )
        log.debug(f"Writing end HTML block to buffer: {html_block}")
        buf.write(html_block.encode("utf_8"))

        buf.seek(0)
        decoded_html = buf.read().decode("utf_8")

        response = self.put(index_file, decoded_html, content_type="text/html")
        return response

    def list_all(self) -> list:
        """
        Get a list of all objects in the bucket.

        :return: List of s3.ObjectSummary dicts, containing object metadata.
            Or a list of object keys only, if keys_only specified.
        """

        resource = Bucket.get_boto3_resource()

        try:
            log.debug(f"Getting bucket named: {self.bucket_name}")
            bucket = resource.Bucket(self.bucket_name)

            log.debug("Listing all objects in bucket")
            objects = bucket.objects.all()

            file_names = [os.path.splitext(file.key)[0] for file in objects]
            log.info(
                f"Returned {len(file_names)} objects from "
                f"bucket named {self.bucket_name}"
            )

            return file_names

        except ClientError as e:
            self._handle_boto3_client_error(e)

    def list_dir(
        self,
        path: str = "",
        recursive: bool = False,
        filter_ext: str = "",
        names_only: bool = False,
    ) -> list:
        """
        Get a list of all objects in a specific directory (s3 path).
        Returns up to a max of 1000 values.

        :param path: The directory in the bucket. Default to root.
        :param recursive: To list all objects and subdirectory objects recursively.
        :param filter_ext: File extension to filter by, e.g. 'txt'
        :param names_only: Remove file extensions and path, giving only the file name.

        :return: List of s3.ObjectSummary dicts, containing object metadata.
        """

        resource = Bucket.get_boto3_resource()

        if path:
            path = path[1:] if path.startswith("/") else path
            path = (path + "/") if not path.endswith("/") else path

        try:
            log.debug(f"Getting bucket named: {self.bucket_name}")
            bucket = resource.Bucket(self.bucket_name)

            log.debug(
                "Filtering objects in bucket with params: "
                f"path: {path} | recursive: {recursive} | filter_ext: {filter_ext}"
            )
            filtered_objects = bucket.objects.filter(
                Delimiter="/" if not recursive else "",
                # EncodingType='url',
                # Marker='string',
                # MaxKeys=123,
                Prefix=path,
            )

        except ClientError as e:
            self._handle_boto3_client_error(e)

        # Test if a match is made, else function will return [False]
        if not isinstance(
            filtered_objects, boto3.resources.collection.ResourceCollection
        ):
            log.info("No matching files for bucket filter parameters.")
            return []

        if filter_ext:
            log.debug(f"Further filtering return by file extension: {filter_ext}")
            file_names = [
                obj.key for obj in filtered_objects if obj.key.endswith(filter_ext)
            ]
        else:
            file_names = [obj.key for obj in filtered_objects]

        if names_only:
            log.debug("Removing extensions from file names")
            file_paths = [Path(file_name) for file_name in file_names]
            file_names = [str(file_path.stem) for file_path in file_paths]

        log.info(
            f"Returned {len(file_names)} filtered objects from "
            f"bucket named {self.bucket_name}"
        )

        return file_names

    def get_cors_config(self) -> dict:
        """
        Get the CORS config for a bucket.

        :return: Response dictionary containing CORS config.
        """

        client = Bucket.get_boto3_client()

        try:
            log.info(f"Getting CORS config for bucket named {self.bucket_name}")
            response = client.get_bucket_cors(Bucket=self.bucket_name)
            cors_rules = (
                response["CORSRules"][0] if len(response["CORSRules"]) > 0 else None
            )
            return cors_rules

        except ClientError as e:
            self._handle_boto3_client_error(e)

        return None

    def set_cors_config(self, origins: list = None, allow_all: bool = None) -> dict:
        """
        Set the CORS config for a bucket.

        :param allow_all: Allow all origins, set to wildcard *.

        :return: True if success, False is failure.
        """

        client = Bucket.get_boto3_client()

        if allow_all is None and origins is None:
            log.debug("No origins provided for param allow_all")
            self._raise_parameter_error("allow_all", allow_all)

        if allow_all:
            origins = ["*"]

        cors_configuration = {
            "CORSRules": [
                {
                    "AllowedHeaders": ["Authorization"],
                    "AllowedMethods": ["GET", "PUT"],
                    "AllowedOrigins": origins,
                    "ExposeHeaders": ["ETag", "x-amz-request-id"],
                    "MaxAgeSeconds": 3000,
                }
            ]
        }

        try:
            log.info(
                "Setting CORS config for bucket named "
                f"{self.bucket_name} to origins {origins}"
            )
            client.put_bucket_cors(
                Bucket=self.bucket_name, CORSConfiguration=cors_configuration
            )
            return True

        except ClientError as e:
            self._handle_boto3_client_error(e)

        return False
