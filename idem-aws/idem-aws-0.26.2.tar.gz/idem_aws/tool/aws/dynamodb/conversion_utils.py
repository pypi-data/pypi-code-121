from collections import OrderedDict
from typing import Any
from typing import Dict
from typing import List

"""
Util functions to convert raw Dynamo DB resource state from AWS to present input format.
"""


def convert_raw_dynamodb_table_to_present(
    hub,
    raw_resource: Dict[str, Any],
    idem_resource_name: str = None,
    tags: List = None,
) -> [str, Any]:
    describe_parameters = OrderedDict(
        {
            "AttributeDefinitions": "attribute_definitions",
            "KeySchema": "key_schema",
            "TableStatus": "table_status",
        }
    )
    new_table_resource = {"resource_id": idem_resource_name, "name": idem_resource_name}
    for parameter_old_key, parameter_new_key in describe_parameters.items():
        if raw_resource.get(parameter_old_key) is not None:
            new_table_resource[parameter_new_key] = raw_resource.get(parameter_old_key)
    if raw_resource.get("StreamSpecification"):
        new_table_resource["stream_specification"] = raw_resource.get(
            "StreamSpecification"
        ).copy()
    if raw_resource.get("BillingModeSummary"):
        new_table_resource["billing_mode"] = raw_resource.get("BillingModeSummary").get(
            "BillingMode"
        )
    if raw_resource.get("TableClassSummary"):
        new_table_resource["table_class"] = raw_resource.get("TableClassSummary").get(
            "TableClass"
        )
    if raw_resource.get("LocalSecondaryIndexes"):
        local_secondary_indexes = []
        for local_index in raw_resource.get("LocalSecondaryIndexes"):
            new_local_index = {
                "IndexName": local_index["IndexName"],
                "KeySchema": local_index["KeySchema"],
                "Projection": local_index["Projection"],
            }
            local_secondary_indexes.append(new_local_index)
        new_table_resource["local_secondary_indexes"] = local_secondary_indexes

    if raw_resource.get("GlobalSecondaryIndexes"):
        global_secondary_indexes = []
        for global_index in raw_resource.get("GlobalSecondaryIndexes"):
            new_global_index = {
                "IndexName": global_index["IndexName"],
                "KeySchema": global_index["KeySchema"],
                "Projection": global_index["Projection"],
            }
            if global_index.get("ProvisionedThroughput"):
                provisioned_throughput = global_index.get("ProvisionedThroughput")
                new_provisioned = {
                    "ReadCapacityUnits": provisioned_throughput["ReadCapacityUnits"],
                    "WriteCapacityUnits": provisioned_throughput["WriteCapacityUnits"],
                }
                new_global_index["ProvisionedThroughput"] = new_provisioned
            global_secondary_indexes.append(new_global_index)
        new_table_resource["global_secondary_indexes"] = global_secondary_indexes

    if raw_resource.get("ProvisionedThroughput"):
        provisioned_throughput = raw_resource.get("ProvisionedThroughput")
        new_provisioned = {
            "ReadCapacityUnits": provisioned_throughput["ReadCapacityUnits"],
            "WriteCapacityUnits": provisioned_throughput["WriteCapacityUnits"],
        }
        new_table_resource["provisioned_throughput"] = new_provisioned

    if raw_resource.get("SSEDescription"):
        sse_specification = raw_resource.get("SSEDescription")
        new_sse_specification = {
            "KMSMasterKeyArn": sse_specification["KMSMasterKeyArn"],
            "SSEType": sse_specification["SSEType"],
        }
        if (
            sse_specification.get("Status") == "ENABLED"
            or sse_specification.get("Status") == "ENABLING"
        ):
            new_sse_specification["Enabled"] = True
        else:
            new_sse_specification["Enabled"] = False
        new_table_resource["sse_specification"] = new_sse_specification
    if raw_resource.get("Replicas"):
        new_table_resource["replica_updates"] = raw_resource.get("Replicas")
    if tags:
        new_table_resource["tags"] = tags
    return new_table_resource
