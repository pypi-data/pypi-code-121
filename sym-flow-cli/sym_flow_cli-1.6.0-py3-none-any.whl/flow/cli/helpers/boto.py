from io import IOBase
from pathlib import Path
from typing import Tuple
from urllib.parse import quote
from uuid import uuid4

import boto3
from sym.shared.cli.helpers.boto import make_intercept_boto_errors

from sym.flow.cli.helpers.constants import (
    DROPBOX_BUCKET,
    WRITE_ONLY_AWS_ACCESS_KEY_ID,
    WRITE_ONLY_AWS_SECRET_ACCESS_KEY,
)

intercept_boto_errors = make_intercept_boto_errors({})


def path_for_uploading(path: Path, ext: str) -> Tuple[str, str]:
    """Create a file name for the upload that includes the full
    path turned into hyphens so it is easy to find the right file.

    Will prefix the file name with a randomly generated uuid and return
    a tuple of that uuid and the full file name.
    """
    path_name = quote(str(path)).strip("/").replace("/", "-")
    unique_uuid = str(uuid4())
    return unique_uuid, str(Path(unique_uuid) / f"{path_name}.{ext}")


@intercept_boto_errors
def put_public_fileobj(file: IOBase, object_path: str, bucket: str = DROPBOX_BUCKET):
    s3_client = boto3.client(
        "s3",
        # Typically we don't include access keys like this, but are including write-only dropbox
        # keys here until we can generate temporary signed URLs via the API
        aws_access_key_id=WRITE_ONLY_AWS_ACCESS_KEY_ID,
        aws_secret_access_key=WRITE_ONLY_AWS_SECRET_ACCESS_KEY,
    )
    s3_client.upload_fileobj(
        file,
        bucket,
        object_path,
        ExtraArgs={"ACL": "bucket-owner-full-control"},
    )
