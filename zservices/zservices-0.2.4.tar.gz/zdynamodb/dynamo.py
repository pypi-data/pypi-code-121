from zdynamodb import logger, Config
import boto3
from botocore.config import Config as BConfig


class DynamoDB:
    def __init__(self, connection_parameter=None, b_config=None):
        logger.debug('[DynamoDB]: Initiating DynamoDB Connection Class')
        self._connection_parameter = connection_parameter
        if self._connection_parameter:
            self.set_connection_parameter(**connection_parameter)
        self._resource = None
        self._config = BConfig(retries={'max_attempts': 3, 'mode': 'standard'})

    def set_connection_parameter(self, **kwargs):
        self._connection_parameter = {
            'region': Config.AWS['region'] if not kwargs.get('region') else kwargs.get('region'),
            "s3_key_id": Config.AWS['s3_key_id'] if not kwargs.get('s3_key_id') else kwargs.get('s3_key_id'),
            "s3_key_secret": Config.AWS['s3_key_secret'] if not kwargs.get('s3_key_secret')
            else kwargs.get('s3_key_secret'),
            "dynamo_table": Config.AWS['dynamo_table'] if not kwargs.get('dynamo_table')
            else kwargs.get('dynamo_table')
        }

    def get_connection_parameter(self):
        return self._connection_parameter

    @property
    def connection(self):
        if self._resource is None:
            self.connect()
        return self._resource

    def connect(self):
        if self._connection_parameter is None:
            self.set_connection_parameter()
        try:
            logger.debug('[DynamoDB]: Creating DynamoDB connection')
            dynamodb_resource = boto3.resource('dynamodb', region_name=self._connection_parameter['region'],
                                               aws_access_key_id=self._connection_parameter['s3_key_id'],
                                               aws_secret_access_key=self._connection_parameter['s3_key_secret'],
                                               config=self._config)
            self._resource = dynamodb_resource
            # For testing connection only, because boto3 only return resource class not exactly a connection
            table_name = self._connection_parameter.get('dynamo_table')
            if table_name:
                table = dynamodb_resource.Table(table_name)
                if table.table_status == 'ACTIVE':  # this throws exception as expected
                    logger.info(f'[DynamoDB]: Connection Successful. Connection={self._resource}')
                else:
                    raise Exception('Unable to connect to table=connection_backend')
        except Exception as e:
            self._resource = None
            logger.error(f'[DynamoDB]: connection issue, conn={self._resource}', exc_info=True)
            raise Exception(f'[DynamoDB]: Connection Error with DynamoDB. Error={e}')
