import boto3.exceptions
import botocore.errorfactory
import botocore.exceptions


def __init__(hub):
    for module in (botocore.errorfactory, botocore.exceptions, boto3.exceptions):
        for name in dir(module):
            e = getattr(module, name)
            try:
                if issubclass(e, Exception):
                    setattr(hub.tool.boto3.exception, name, e)
            except TypeError:
                ...
