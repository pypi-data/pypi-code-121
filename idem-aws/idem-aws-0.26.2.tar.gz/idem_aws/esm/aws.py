"""
Plugin for aws enforced state management
"""
import json
import pathlib
from typing import Any
from typing import Dict

import botocore.exceptions


def __init__(hub):
    hub.esm.aws.ACCT = ["aws"]
    hub.esm.aws.ESM_PROFILE = {}


async def get_state(hub, ctx) -> Dict[str, Any]:
    """
    Read this context's state from AWS S3 bucket. Return empty dict if the file key path does not exist in the bucket.

    Args:
        hub: The redistributed pop central hub.
        ctx: A dict with the keys/values for the execution of the Idem run located in
        `hub.idem.RUNS[ctx['run_name']]`.

    Returns:
        A dict containing all resource state records. Return empty dict if the file key path does not exist in the bucket.
    """
    try:
        client = hub.tool.boto3.client.get_client(ctx, service_name="s3")
        content = client.get_object(
            Bucket=hub.esm.aws.ESM_PROFILE.get("bucket"),
            Key=hub.esm.aws.ESM_PROFILE.get("key"),
        )
        state = json.loads(content["Body"].read())
        return state
    except botocore.exceptions.ClientError as client_ex:
        if client_ex.response["Error"]["Code"] == "NoSuchKey":
            hub.log.debug(
                f"No state file found from S3 bucket {hub.esm.aws.ESM_PROFILE.get('bucket')} using key {hub.esm.aws.ESM_PROFILE.get('key')}"
            )
            return {}
        else:
            hub.log.error(
                f"Failed to retrieve state file from S3 bucket {hub.esm.aws.ESM_PROFILE.get('bucket')} using key {hub.esm.aws.ESM_PROFILE.get('key')}"
                f" with error {client_ex.response['Error']['Message']}"
            )
            raise client_ex
    except Exception as e:
        hub.log.error(
            f"Failed to retrieve state file from S3 bucket {hub.esm.aws.ESM_PROFILE.get('bucket')} using key {hub.esm.aws.ESM_PROFILE.get('key')}"
            f" with error {str(e)}"
        )
        raise e


async def set_state(hub, ctx, state: Dict[str, Any]):
    """
    Write the state to this context's cache_file

    Args:
        hub: The redistributed pop central hub.
        ctx: A dict with the keys/values for the execution of the Idem run located in
        `hub.idem.RUNS[ctx['run_name']]`.
        state: A dict containing all resource states that will be stored in S3 bucket.

    Returns:
        None if the operation succeeds. An exception will raise if the operation failed.
    """
    try:
        ret = await hub.exec.boto3.client.s3.put_object(
            ctx,
            Bucket=hub.esm.aws.ESM_PROFILE.get("bucket"),
            Body=bytes(json.dumps(state), "utf-8"),
            Key=hub.esm.aws.ESM_PROFILE.get("key"),
            ServerSideEncryption="AES256"
            if hub.esm.aws.ESM_PROFILE.get("encrypt", False)
            else None,
        )
        if not ret["result"]:
            error_msg = (
                f"Failed to upload state file to S3 bucket {hub.esm.aws.ESM_PROFILE.get('bucket')} as"
                f" {hub.esm.aws.ESM_PROFILE.get('key')} with error {ret['comment']}"
            )
            raise RuntimeError(error_msg)
        else:
            hub.log.debug(
                f"Successfully upload state file to S3 bucket {hub.esm.aws.ESM_PROFILE.get('bucket')} as"
                f" {hub.esm.aws.ESM_PROFILE.get('key')}"
            )
            return
    except Exception as e:
        hub.log.error(str(e))
        raise e


async def enter(hub, ctx):
    """
    Verify that only one process can access the same enforced state record file in S3 bucket.
    Set a lock by performing an atomic operation to put the file key to DynamoDB.
    If esm profile is not specified in credential profile. Then we try to find it from the Idem config.
    The config file should have the following structure:

      extras:
        aws:
          esm:
            bucket: idem-storage-bucket-name
            dynamodb_table: idem-esm-lock-table-name
            key: /my-file-path/my-esm-cache.json
            encrypt: True

    Args:
        hub: The redistributed pop central hub.
        ctx: A dict with the keys/values for the execution of the Idem run located in
        `hub.idem.RUNS[ctx['run_name']]`.

    Returns:
        None if lock has been acquired successfully. Raise exception if lock was failed to be acquired
    """
    hub.esm.aws.ESM_PROFILE = ctx.acct.get("esm")
    if not hub.esm.aws.ESM_PROFILE:
        if (
            "extras" in hub.OPT.acct
            and hub.OPT.acct.extras
            and "aws" in hub.OPT.acct.extras
        ):
            hub.esm.aws.ESM_PROFILE = hub.OPT.acct.extras.aws.get("esm")
    if not hub.esm.aws.ESM_PROFILE:
        raise ValueError("ESM profile is required to support remote ESM storage.")
    if not hub.esm.aws.ESM_PROFILE.get("dynamodb_table"):
        raise ValueError("dynamodb_table is required in ESM profile.")
    if not hub.esm.aws.ESM_PROFILE.get("bucket"):
        raise ValueError("bucket is required in ESM profile.")
    if not hub.esm.aws.ESM_PROFILE.get("key"):
        raise ValueError("key is required in ESM profile.")
    try:
        # Put item with conditional expression to acquire the lock. The conditional check and put operation is atomic.
        # This ensures that the S3 bucket file can be locked properly.
        db_resource = hub.tool.boto3.resource.create(
            ctx, "dynamodb", "Table", hub.esm.aws.ESM_PROFILE.get("dynamodb_table")
        )
        db_resource.put_item(
            Item={
                "LockID": f"{hub.esm.aws.ESM_PROFILE.get('bucket')}/{hub.esm.aws.ESM_PROFILE.get('key')}"
            },
            ConditionExpression="attribute_not_exists(#r)",
            ExpressionAttributeNames={"#r": "LockID"},
        )
        # Lock acquired
        return
    except botocore.exceptions.ClientError as e:
        # Another exception than ConditionalCheckFailedException was caught, raise as-is
        if e.response["Error"]["Code"] != "ConditionalCheckFailedException":
            raise e
        else:
            # If conditional check failed, it means the lock cannot be acquired because it is already locked
            raise ValueError(
                f"File {hub.esm.aws.ESM_PROFILE.get('bucket')}/{hub.esm.aws.ESM_PROFILE.get('key')}"
                f" has been locked by another user/process."
            )


async def exit_(hub, ctx, handle: pathlib.Path, exception: Exception):
    """
    Release the db lock and handle errors

    Args:
        hub: The redistributed pop central hub.
        ctx: A dict with the keys/values for the execution of the Idem run located in
        `hub.idem.RUNS[ctx['run_name']]`.
        handle: This parameter is inherited from Idem. It is not being used in Idem-aws plugin.
        exception: Error.

    Returns:
        None if file lock has been released. Raise Exception if any failure happened.
    """
    if exception:
        hub.log.error(f"{exception.__class__.__name__}: {exception}")
    if hub.esm.aws.ESM_PROFILE is None:
        raise ValueError("ESM profile is required to support remote ESM storage.")
    try:
        # Delete item with conditional expression to release the lock
        db_resource = hub.tool.boto3.resource.create(
            ctx, "dynamodb", "Table", hub.esm.aws.ESM_PROFILE.get("dynamodb_table")
        )
        db_resource.delete_item(
            Key={
                "LockID": f"{hub.esm.aws.ESM_PROFILE.get('bucket')}/{hub.esm.aws.ESM_PROFILE.get('key')}"
            },
            ConditionExpression="attribute_exists(#r)",
            ExpressionAttributeNames={"#r": "LockID"},
        )
        # Lock released
        return
    except botocore.exceptions.ClientError as e:
        # Another exception than ConditionalCheckFailedException was caught, raise as-is
        if e.response["Error"]["Code"] != "ConditionalCheckFailedException":
            raise e
        else:
            # Else, lock has been released
            hub.log.debug(
                f"Lock {hub.esm.aws.ESM_PROFILE.get('bucket')}/{hub.esm.aws.ESM_PROFILE.get('key')}"
                f" has been previously released."
            )
            return
