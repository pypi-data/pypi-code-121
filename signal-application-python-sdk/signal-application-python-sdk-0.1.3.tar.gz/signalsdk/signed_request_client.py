import logging

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import requests
from signalsdk.signal_exception import SignalAppSignedReqError

def signed_request(method, url, data=None, params=None, headers=None):
    session = boto3.Session()
    credentials = session.get_credentials()
    creds = credentials.get_frozen_credentials()
    logging.info(f"signalsdk::accesskey: {creds.access_key}, secretkey: {creds.secret_key}")
    request = AWSRequest(method=method, url=url, data=data, params=params, headers=headers)
    SigV4Auth(creds, "execute-api", 'us-east-1').add_auth(request)
    response = requests.request(method=method, url=url, headers=dict(request.headers), data=data)
    if response.status_code == 200:
        return response.json()
    raise SignalAppSignedReqError
