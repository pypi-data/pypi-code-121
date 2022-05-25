import base64
import json
import os

import boto3
from botocore.exceptions import ClientError


def get_secret_from_file(secrets_name, key=None):
    """
    :param key: a specific key from secrets
    :param secrets_name: secrets file name where secrets are stored
    """
    try:
        from secret.zeno_secrets import all_secrets
        secrets = all_secrets[secrets_name]
        try:
            if key:
                return secrets[key]
            else:
                return secrets
        except KeyError:
            error_message = "Set the {0} environment variable".format(key)
            raise EnvironmentError(error_message)
    except FileNotFoundError:
        error_message = "secrets.json not found in config folder"
        raise EnvironmentError(error_message)


class Config:
    __shared_instance = 'getsecrets'

    @staticmethod
    def get_instance():

        """Static Access Method"""
        if Config.__shared_instance == 'getsecrets':
            Config()
        return Config.__shared_instance

    def __init__(self):

        """virtual private constructor"""
        if Config.__shared_instance != 'getsecrets':
            raise Exception("This class is a config class !")
        else:
            Config.__shared_instance = self
        self.secrets = None

    def download_secret(self, secrets_name=None):
        if self.secrets:
            return self.secrets
        secret_name = f"arn:aws:secretsmanager:ap-south-1:921939243643:secret:{secrets_name}"
        region_name = "ap-south-1"

        # Create a Secrets Manager client
        session = boto3.session.Session(
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            region_name=os.environ.get("REGION_NAME")
        )
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )

        try:
            print("connecting with secrets manager for getting secrets")
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'DecryptionFailureException':
                raise e
            elif e.response['Error']['Code'] == 'InternalServiceErrorException':
                raise e
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                raise e
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                raise e
            elif e.response['Error']['Code'] == 'ResourceNotFoundException':
                raise e
        else:
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
                return json.loads(secret)
            else:
                decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
                return json.loads(decoded_binary_secret)

    def get_secrets(self):
        if os.environ.get('env') == 'stage':
            self.secrets = self.download_secret(secrets_name='staging/etl')
        elif os.environ.get('env') == 'prod':
            self.secrets = self.download_secret(secrets_name='production/etl')
        else:
            self.secrets = get_secret_from_file(secrets_name='development/etl')
        return self.secrets
