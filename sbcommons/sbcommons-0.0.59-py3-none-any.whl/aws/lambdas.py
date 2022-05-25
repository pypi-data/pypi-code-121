import json
from typing import Dict

import boto3
from botocore.config import Config


def invoke_with_extended_timeout(function_name: str, event: Dict, invocation_type: str = 'Event'):
    config = Config(read_timeout=900, retries={'max_attempts': 1})
    return invoke(function_name, event, invocation_type, config)


def invoke(function_name: str, event: Dict, invocation_type: str = 'Event', config: Config = None):
    lambda_resource = boto3.client('lambda', config=config)
    return lambda_resource.invoke(
        FunctionName=function_name,
        InvocationType=invocation_type,
        Payload=json.dumps(event)
    )
