import base64
import json
import logging
import textwrap
import warnings

import boto3
from botocore.exceptions import ClientError

from ..docker import load_secrets

# logger
logger = logging.getLogger(__name__)

# create client for SecretsManager
def _create_client(
    profile_name=None,
    aws_access_key_id=None,
    aws_secret_access_key=None,
    region_name="ap-northeast-2",
    load_docker_secret=True,
):
    """Create boto3 secretsmanager client.

    Priority:
        1. profile_name
        2. aws_access_key_id & secret_access_key
        3. docker secret (/run/secret)
    """

    # session configuration
    session_conf = dict()
    if load_docker_secret:
        load_secrets()
    if region_name is not None:
        session_conf.update({"region_name": region_name})
    if aws_access_key_id is not None:
        if aws_secret_access_key is not None:
            session_conf.update(
                {
                    "aws_access_key_id": aws_access_key_id,
                    "aws_secret_access_key": aws_secret_access_key,
                }
            )
    if profile_name is not None:
        session_conf = {"profile_name": profile_name}

    # return clinet
    session = boto3.session.Session(**session_conf)
    return session.client(service_name="secretsmanager")


# get secrets
def get_secrets(
    secret_name: str,
    profile_name: str = None,
    aws_access_key_id: str = None,
    aws_secret_access_key: str = None,
    region_name: str = "ap-northeast-2",
    load_docker_secret: bool = True,
):
    """Get secrets from AWS SecretsManager.

    Example
    -------
    >>> conf = get_secrets("some/secrets")
    """

    # get client
    client = _create_client(
        profile_name=profile_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name,
        load_docker_secret=load_docker_secret,
    )

    # get secrets
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        code = e.response["Error"]["Code"]
        description = textwrap.dedent(ERROR_DESCRIPTIONS["CODE"]).strip("\n")
        logger.error(code)
        logger.error(description)
        raise e
    else:
        if "SecretString" in get_secret_value_response:
            secrets = get_secret_value_response["SecretString"]
            secrets = json.loads(secrets)
        else:
            secrets = base64.b64decode(get_secret_value_response["SecretBinary"])

    return secrets


# list secrets
def list_secrets(
    profile_name: str = None,
    aws_access_key_id: str = None,
    aws_secret_access_key: str = None,
    region_name: str = "ap-northeast-2",
    load_docker_secret: bool = True,
    shorten=True,
):
    """
    (TODO)
      - filter tags
    """

    # get client
    client = _create_client(
        profile_name=profile_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name,
        load_docker_secret=load_docker_secret,
    )

    # get secrets
    opts = {}
    secret_list = []
    while True:
        response = client.list_secrets(**opts)
        secret_list += response.get("SecretList", [])
        next_token = response.get("NextToken")
        if next_token is None:
            break
        opts.update({"NextToken": next_token})

    if shorten:
        return {x["Name"]: x["Description"] for x in secret_list}

    return secret_list


# [DEPRECATED]
def get_secret(secret_name, region_name="ap-northeast-2"):
    _warn = "'get_secret' will be deprecated soon, use 'get_secrets'!"
    warnings.warn(_warn, FutureWarning)

    return get_secrets(secret_name=secret_name, region_name=region_name)


# errors
ERROR_DESCRIPTIONS = {
    "DecryptionFailureException": """
    Secrets Manager can't decrypt the protected secret text using the provided KMS key.
    Deal with the exception here, and/or rethrow at your discretion.
    """,
    "InternalServiceErrorException": """
    An error occurred on the server side.
    Deal with the exception here, and/or rethrow at your discretion.
    """,
    "InvalidParameterException": """
    You provided an invalid value for a parameter.
    Deal with the exception here, and/or rethrow at your discretion.
    """,
    "InvalidRequestException": """
    You provided a parameter value that is not valid for the current state of the resource.
    Deal with the exception here, and/or rethrow at your discretion.
    """,
    "ResourceNotFoundException": """
    We can't find the resource that you asked for.
    Deal with the exception here, and/or rethrow at your discretion.
    """,
}
