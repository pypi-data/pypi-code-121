import boto3
import base64

from botocore.exceptions import ClientError


class SecretsManager:
    ERROR_KEY = 'Error'
    CODE_KEY = 'Code'

    def __init__(self, secret_name, region_name):
        if not secret_name or not region_name:
            raise Exception("Secret name or region name need to be provided.")
        self.secret_name = secret_name
        self.client = boto3.session.Session().client(
            service_name='secretsmanager',
            region_name=region_name
        )

    def get(self):
        try:
            get_secret_value_response = self.client.get_secret_value(SecretId=self.secret_name)
        except ClientError as e:
            if 'DecryptionFailureException' == e.response[self.ERROR_KEY][self.CODE_KEY]:
                # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
                raise e
            elif 'InternalServiceErrorException' == e.response[self.ERROR_KEY][self.CODE_KEY]:
                # An error occurred on the server side.
                raise e
            elif 'InvalidParameterException' == e.response[self.ERROR_KEY][self.CODE_KEY]:
                # You provided an invalid value for a parameter.
                raise e
            elif 'InvalidRequestException' == e.response[self.ERROR_KEY][self.CODE_KEY]:
                # You provided a parameter value that is not valid for the current state of the resource.
                raise e
            elif 'ResourceNotFoundException' == e.response[self.ERROR_KEY][self.CODE_KEY]:
                # We can't find the resource that you asked for.
                raise e
        else:
            # Decrypts secret using the associated KMS CMK. Depending on whether the secret is a string or binary, one
            # of these fields will be populated.
            if 'SecretString' in get_secret_value_response:
                return get_secret_value_response['SecretString']
            else:
                return base64.b64decode(get_secret_value_response['SecretBinary'])

    def update(self, data):
        return self.client.update_secret(SecretId=self.secret_name, SecretString=data)
