import logging

from botocore.exceptions import ClientError


log = logging.getLogger(__name__)


class BucketException(Exception):
    """
    Parent class to be inherited for consistency.
    """

    def __init__(self, message, bucket):
        log.error(message)
        self.bucket = bucket
        self.message = f"{message}"
        super().__init__(self.message)


class NoSuchKey(BucketException):
    """
    Raised if you try to access a non-existent object.
    """

    def __init__(self, key, bucket):
        self.key = key
        self.bucket = bucket
        self.message = f"Object not found in bucket {bucket} matching {key}"
        super().__init__(self.message, self.bucket)


class NoSuchBucket(BucketException):
    """
    Raised if you try to access a non-existent bucket.
    """

    def __init__(self, bucket_name):
        self.bucket = bucket_name
        self.message = f"Bucket named '{bucket_name}' does not exist!"
        super().__init__(self.message, self.bucket)


class BucketAlreadyExists(BucketException):
    """
    Raised if a bucket already exists.
    """

    def __init__(self, bucket_name):
        self.bucket = bucket_name
        self.message = f"Bucket named '{bucket_name}' already exists. Creation failed."
        super().__init__(self.message, self.bucket)


class BucketAccessDenied(BucketException):
    """
    Raised if access to a bucket is denied. Likely because it does not exist.
    """

    def __init__(self, bucket_name):
        self.bucket = bucket_name
        self.message = f"Unable to access bucket {self.bucket}. Does it exist?"
        super().__init__(self.message, self.bucket)


class NoSuchCORSConfiguration(BucketException):
    """
    Raised if no CORS configuration is set for a bucket.
    """

    def __init__(self, bucket_name):
        self.bucket = bucket_name
        self.message = f"Bucket {self.bucket} does not have CORS configured."
        super().__init__(self.message, self.bucket)


class UnknownBucketException(BucketException):
    """
    Raised for unknown S3 exceptions.
    """

    def __init__(self, bucket_name, e: ClientError):
        self.bucket = bucket_name
        error_code: str = e.response.get("Error").get("Code")
        error_message: str = e.response.get("Error").get("Message")
        self.message = f"Unknown bucket exception {error_code}: {error_message}"
        super().__init__(self.message, self.bucket)
