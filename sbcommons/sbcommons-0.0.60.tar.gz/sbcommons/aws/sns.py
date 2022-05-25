from typing import Any

import boto3


def sns_client(region: str) -> Any:
    return boto3.client('sns', region_name=region)


def publish(topic_arn: str, region: str, message: str):
    client = sns_client(region)
    client.publish(
        TargetArn=topic_arn,
        Message=message
    )
