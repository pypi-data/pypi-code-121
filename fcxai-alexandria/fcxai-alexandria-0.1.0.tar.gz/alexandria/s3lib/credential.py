import boto3


def load_aws_client(aws_access_key=None, aws_secret_key=None):
    client = boto3.client(
        "s3", aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key
    )
    return client
