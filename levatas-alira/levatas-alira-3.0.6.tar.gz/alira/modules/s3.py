import boto3
import uuid
import logging
import os

from pathlib import Path

from alira.instance import Instance
from alira.modules.module import ConnectionError, InternalError
from alira.modules.module import Connection

from botocore.exceptions import EndpointConnectionError

PIPELINE_S3_MODULE_NAME = "s3"


class S3(Connection):
    def __init__(
        self,
        configuration_directory: str,
        bucket: str,
        key_prefix: str,
        public: bool,
        module_id: str = None,
        autogenerate_name: bool = False,
        filtering: str = None,
        files: str = None,
        files_directory: str = None,
        provider=None,
        **kwargs,
    ):
        super().__init__(
            configuration_directory=configuration_directory,
            module_id=module_id or PIPELINE_S3_MODULE_NAME,
            **kwargs,
        )

        self.filtering = self._load_function(filtering)

        self.files = files
        self.files_directory = files_directory or "files"

        self.provider = provider or S3Provider(
            configuration_directory=self.configuration_directory,
            bucket=bucket,
            key_prefix=key_prefix,
            public=public,
            autogenerate_name=autogenerate_name,
            files_directory=self.files_directory,
            **kwargs,
        )

    def run(self, instance: Instance, **kwargs):
        super().run(instance, **kwargs)

        if self.filtering and not self.filtering(instance):
            logging.info(
                f"The instance didn't pass the filtering criteria. Instance: {instance}"
            )
            return {"status": "SKIPPED"}

        default_files = instance.files if instance.files else None
        if self.files:
            filenames = instance.get_attribute(self.files, default=default_files)
            # The `files` field might be pointing to field containing a single
            # file. In that case, we need to convert it to a list.
            if filenames and not isinstance(filenames, list):
                filenames = [filenames]
        else:
            filenames = default_files

        if filenames and len(filenames) > 0:
            try:
                uploaded_files = self.provider.upload(filenames)

                return {
                    "status": "SUCCESS",
                    "files": [x for x in uploaded_files.values() if x is not None],
                }
            except InternalError as e:
                return {"status": "FAILURE", "message": str(e)}

        return {
            "status": "SUCCESS",
            "message": "No files to upload",
        }


class S3Provider:
    """
    This class handles the logic of uploading files to an S3 bucket. This class is
    used by any of the AWS modules that have to upload files to S3.
    """

    def __init__(
        self,
        configuration_directory: str,
        bucket: str,
        key_prefix: str = None,
        public: bool = False,
        autogenerate_name: bool = False,
        files_directory: str = None,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        aws_region_name: str = None,
        **kwargs,
    ):
        self.configuration_directory = configuration_directory
        self.bucket = bucket
        self.key_prefix = key_prefix
        self.public = public
        self.autogenerate_name = autogenerate_name
        self.files_directory = files_directory or "files"

        self.aws_access_key_id = aws_access_key_id or os.environ.get(
            "ALIRA_AWS_ACCESS_KEY_ID", None
        )
        self.aws_secret_access_key = aws_secret_access_key or os.environ.get(
            "ALIRA_AWS_SECRET_ACCESS_KEY", None
        )
        self.aws_region_name = aws_region_name or os.environ.get(
            "ALIRA_AWS_REGION_NAME", None
        )

        if (
            not self.aws_access_key_id
            or not self.aws_secret_access_key
            or not self.aws_region_name
        ):
            raise InternalError("The AWS credentials were not specified")

    def upload(self, files: list):
        logging.info(f"Uploading files to S3 Bucket {self.bucket}...")

        result = {}

        for file in files:
            if self.autogenerate_name:
                _, file_extension = os.path.splitext(file)
                s3_key = f"{uuid.uuid4().hex}{file_extension}"
            else:
                s3_key = os.path.basename(file)

            if self.key_prefix:
                s3_key = os.path.join(self.key_prefix, s3_key)

            filename = os.path.join(
                self.configuration_directory, self.files_directory, file
            )

            if os.path.isfile(filename):
                try:
                    with open(filename, "rb") as f:
                        buffer = f.read()

                    self._upload_file(s3_key=s3_key, filename=filename, buffer=buffer)

                    if self.public:
                        result[
                            file
                        ] = f"https://{self.bucket}.s3.amazonaws.com/{s3_key}"
                    else:
                        result[file] = f"s3://{self.bucket}/{s3_key}"
                except EndpointConnectionError as e:
                    raise ConnectionError(e)
                except Exception as e:
                    logging.exception(e)
                    raise InternalError(f"There was an error uploading file {file}")
            else:
                logging.info(f"File {file} does not exist")
                result[file] = None

        return result

    def _upload_file(self, s3_key, filename, buffer):
        logging.info(
            f"Uploading {filename} to bucket {self.bucket} and location {s3_key}..."
        )

        arguments = {"Bucket": self.bucket, "Key": s3_key, "Body": buffer}

        extension = Path(filename).suffix.lower()
        content_type = "binary/octet-stream"
        if extension in [".jpg", ".jpeg"]:
            content_type = "image/jpeg"
        elif extension == ".png":
            content_type = "image/png"

        arguments["ContentType"] = content_type
        if self.public:
            arguments["ACL"] = "public-read"

        self._put_object(**arguments)

        s3_location = f"s3://{self.bucket}/{s3_key}"
        logging.info(f"Uploaded {filename} to {s3_location}")

    def _put_object(self, **kwargs):
        session = boto3.Session(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.aws_region_name,
        )

        client = session.client("s3")
        client.put_object(**kwargs)
