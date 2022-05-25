from typing import Any

import boto3


def dms_client(region: str) -> Any:
    return boto3.client('dms', region_name=region)


def describe_replication_task(region: str, is_single: bool = True, **kwargs):
    client = dms_client(region)
    replication_tasks = client.describe_replication_tasks(**kwargs)
    return replication_tasks['ReplicationTasks'][0] if is_single else replication_tasks


def start_replication_task(region: str, task_arn: str, task_type: str, **kwargs):
    client = dms_client(region)
    client.start_replication_task(
        ReplicationTaskArn=task_arn,
        StartReplicationTaskType=task_type,
        **kwargs
    )
