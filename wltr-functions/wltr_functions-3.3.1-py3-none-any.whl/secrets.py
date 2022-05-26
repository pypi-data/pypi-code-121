import json
import boto3
import base64
from botocore.exceptions import ClientError


class Secrets(object):
    class AWS:
        def __init__(self, secret, region):
            self.secret_name = secret
            self.region_name = region

        def get_secret(self):
            session = boto3.session.Session()

            client = session.client(service_name='secretsmanager',
                                    region_name=self.region_name)

            aws_secret = ''

            try:
                get_secret_value_response = client.get_secret_value(SecretId=self.secret_name)

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
                    aws_secret = get_secret_value_response['SecretString']

                else:
                    decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])

            return json.loads(aws_secret)
