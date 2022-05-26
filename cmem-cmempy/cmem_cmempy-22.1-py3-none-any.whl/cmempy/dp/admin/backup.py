"""API for eccenca DataPlatform /api/admin/backup/*."""

from requests_toolbelt.multipart import encoder

from cmem.cmempy import config
from cmem.cmempy.api import request


def get_zip():
    """Get a full backup of the knowledge graphs."""
    uri = config.get_dp_api_endpoint() + "/api/admin/backup/zip"
    return request(
        uri,
        method="GET",
        stream=True
    )


def post_zip(zip_file):
    """Post a full backup of the knowledge graphs."""
    uri = config.get_dp_api_endpoint() + "/api/admin/restore/zip"
    with open(zip_file, 'rb') as file:
        files = [
            (
                'file',
                ('backup.zip', file, 'application/zip')
            )
        ]
        # https://stackoverflow.com/questions/42281387/
        multipart_encoder = encoder.MultipartEncoder(
            fields=files,
            boundary="xxx---------------xxx",
        )
        return request(
            uri,
            method="POST",
            data=multipart_encoder,
            headers={'Content-Type': multipart_encoder.content_type},
            stream=True
        )
