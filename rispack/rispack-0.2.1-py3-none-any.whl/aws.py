import json
import os

from boto3 import client, session
from requests_aws_sign import AWSV4Sign

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")


def get_signed_auth():
    """Returns a signed uri for calling endpoints with IAM authorization."""

    sess = session.Session()
    credentials = sess.get_credentials()
    service = "execute-api"

    return AWSV4Sign(credentials, AWS_REGION, service)


def get_ssm_parameter(name, encrypted=False):
    """Return a parameter value from the Systems Manger parameter store.

    :param name: The parameter name.
    :param encrypted: Flag indicating if the value is encrypted or not.
    """
    cli = client("ssm")
    param = cli.get_parameter(Name=name, WithDecryption=encrypted)

    return param["Parameter"]["Value"] if param else None

def get_secret(name):
    """Return a secret value from Secrets Manger.

    :param name: The secret name.
    """

    sess = session.Session()

    client = sess.client(service_name="secretsmanager", region_name=AWS_REGION)

    secret = client.get_secret_value(SecretId=name)

    return secret["SecretString"]


def get_proxy_token(endpoint: str, port: str, user: str):
    session = session.Session()
    client = session.client("rds")

    return client.generate_db_auth_token(
        DBHostname=endpoint,
        Port=port,
        DBUsername=user,
        Region=AWS_REGION,
    )
