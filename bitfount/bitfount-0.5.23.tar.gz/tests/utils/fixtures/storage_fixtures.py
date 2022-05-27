"""Fixtures related to uploading/downloading from S3."""
from pytest import fixture

from bitfount.federated.transport.message_service import _S3_NETLOC_SUFFIX
from bitfount.types import _S3PresignedPOSTFields, _S3PresignedPOSTURL, _S3PresignedURL


@fixture
def s3_upload_url() -> _S3PresignedPOSTURL:
    """A faked upload URL for S3 POST."""
    return _S3PresignedPOSTURL(
        f"https://an-s3-upload-url{_S3_NETLOC_SUFFIX}/some-resource/path?hello=upload_world"  # noqa: B950  # better to keep the URL whole
    )


@fixture
def s3_upload_fields() -> _S3PresignedPOSTFields:
    """Faked upload fields for S3 POST."""
    return _S3PresignedPOSTFields({"some": "upload", "fields": "to_test_with"})


@fixture
def s3_download_url() -> _S3PresignedURL:
    """Fake download URL for S3 GET."""
    return _S3PresignedURL(
        f"https://an-s3-download-url{_S3_NETLOC_SUFFIX}/some-resource/path?hello=download_world"  # noqa: B950  # better to keep the URL whole
    )
