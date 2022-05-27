"""
Util functions to execute update on AWS DynamoDB Table.
"""
from collections import OrderedDict
from typing import Any
from typing import Dict
from typing import List


async def compare_inputs_and_update_dynamodb_table(
    hub,
    ctx,
    plan_state: Dict[str, Any],
    attribute_definitions: List,
    name: str,
    billing_mode: str = None,
    provisioned_throughput: dict = None,
    global_secondary_indexes: List = None,
    sse_specification: dict = None,
    stream_specification: dict = None,
    replica_updates: List = None,
    table_class: str = None,
    timeout: Dict = None,
):
    result = dict(comment=(), result=True, ret=None)
    if not ctx.get("test", False):
        update_ret = await hub.exec.boto3.client.dynamodb.update_table(
            ctx=ctx,
            AttributeDefinitions=attribute_definitions,
            TableName=name,
            BillingMode=billing_mode,
            ProvisionedThroughput=provisioned_throughput,
            GlobalSecondaryIndexes=global_secondary_indexes,
            SSESpecification=sse_specification,
            StreamSpecification=stream_specification,
            ReplicaUpdates=replica_updates,
            TableClass=table_class,
        )
        result["result"] = update_ret["result"]
        result["comment"] = (
            update_ret["comment"]
            if result["result"]
            else (f"Updated aws.dynamodb.table {name}.",)
        )
        if update_ret["result"]:
            waiter_config = hub.tool.aws.waiter_utils.create_waiter_config(
                default_delay=15,
                default_max_attempts=40,
                timeout_config=timeout.get("update") if timeout else None,
            )
            hub.log.debug(f"Waiting on updating aws.dynamodb.table '{name}'")
            try:
                await hub.tool.boto3.client.wait(
                    ctx,
                    "dynamodb",
                    "table_exists",
                    TableName=name,
                    WaiterConfig=waiter_config,
                )
            except Exception as e:
                result["comment"] = result["comment"] + (str(e),)
                result["result"] = False
    else:
        update_params = OrderedDict(
            {
                "billing_mode": billing_mode,
                "attribute_definitions": attribute_definitions,
                "name": name,
                "table_class": table_class,
                "provisioned_throughput": provisioned_throughput,
                "global_secondary_indexes": global_secondary_indexes,
                "sse_specification": sse_specification,
                "stream_specification": stream_specification,
                "replica_updates": replica_updates,
            }
        )
        for key, value in update_params.items():
            if value is None:
                if key not in plan_state:
                    plan_state[key] = None
            else:
                plan_state[key] = value
    return result
