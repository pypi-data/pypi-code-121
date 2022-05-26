import requests

from xero.auth import OAuth2Credentials

from xero.exceptions import *

from oauth2 import *
import boto3
import ast


def get_auth_token(client_id, token_details, profile_name=None):
    """
    Consumes the client id and the previous auth processes refresh token.
    This returns an authentication token that will last 30 minutes
    to make queries the minute it is used. Or it will expire in 60 days of no use.
    The newly generated last refresh token now needs token stored for
    next use.
    """
    bucket = token_details["bucket_name"]
    token_name = token_details["token_path"]
    local_token_path = token_details["local_token_path"]
    boto3_session = None
    if profile_name is None:
        boto3_session = boto3.Session()
    else:
        boto3_session = boto3.Session(profile_name=profile_name)

    s3_resource = boto3_session.resource("s3")
    s3_resource.Bucket(bucket).download_file(token_name, local_token_path)
    token_file = open(local_token_path, "r")

    auth_token = ast.literal_eval(token_file.read())
    # print(auth_token)
    auth_creds = OAuth2Credentials(client_id, client_secret="", token=auth_token)

    return refresh_auth_token(client_id, auth_creds)


def refresh_auth_token(client_id, auth_creds):
    """
    A simple handle of the token expiration.
    """
    if not auth_creds.expired():
        return auth_creds

    cred = {
        "grant_type": "refresh_token",
        "refresh_token": auth_creds.token["refresh_token"],  #
        "client_id": client_id,
    }
    response = requests.post("https://identity.xero.com/connect/token", cred)
    auth_token = response.json()
    print(auth_token)

    save_auth_token(client_id, auth_token)
    return OAuth2Credentials(client_id, client_secret="", token=auth_token)


def save_auth_token(client_id, auth_token):
    """
    function to persist the latest auth token to s3
    """
    # TODO: pull update_refresh_token from readers into here
    pass
