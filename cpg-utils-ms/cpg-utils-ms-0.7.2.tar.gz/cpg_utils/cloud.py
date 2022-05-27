"""Convenience functions related to cloud infrastructure."""

from typing import Optional
from google.auth import jwt
from google.cloud import secretmanager
import google.api_core.exceptions


def email_from_id_token(id_token: str) -> str:
    """Decodes the ID token (JWT) to get the email address of the caller.

    See http://bit.ly/2YAIkzy for details.

    This function assumes that the token has been verified beforehand."""

    return jwt.decode(id_token, verify=False)['email']


def read_secret(project_id: str, secret_name: str) -> Optional[str]:
    """Reads the latest version of a GCP Secret Manager secret.

    Returns None if the secret doesn't exist."""

    secret_manager = secretmanager.SecretManagerServiceClient()
    secret_path = secret_manager.secret_path(project_id, secret_name)

    try:
        response = secret_manager.access_secret_version(
            request={'name': f'{secret_path}/versions/latest'}
        )
        return response.payload.data.decode('UTF-8')
    except google.api_core.exceptions.ClientError:
        # Fail gracefully if there's no secret version yet.
        return None
    except AttributeError:
        # Sometimes the google API fails when no version is present, with:
        #   File "{site-packages}/google/api_core/exceptions.py",
        #   line 532, in from_grpc_error if isinstance(rpc_exc, grpc.Call) or _is_informative_grpc_error(rpc_exc):
        #   AttributeError: 'NoneType' object has no attribute 'Call'
        return None


def write_secret(project_id: str, secret_name: str, secret_value: str) -> None:
    """
    Adds a new version for a GCP Secret Manager secret and disables all previous versions

    Parameters
    ----------
    project_id
    secret_name
    secret_value

    Returns
    -------

    """

    secret_manager = secretmanager.SecretManagerServiceClient()
    secret_path = secret_manager.secret_path(project_id, secret_name)

    response = secret_manager.add_secret_version(
        request={
            'parent': secret_path,
            'payload': {'data': secret_value.encode('UTF-8')},
        }
    )

    # Disable all previous versions.
    for version in secret_manager.list_secret_versions(request={'parent': secret_path}):
        # Don't attempt to change the state of destroyed / already disabled secrets and
        # don't disable the latest version.
        if (
            version.state == secretmanager.SecretVersion.State.ENABLED
            and version.name != response.name
        ):
            secret_manager.disable_secret_version(request={'name': version.name})
