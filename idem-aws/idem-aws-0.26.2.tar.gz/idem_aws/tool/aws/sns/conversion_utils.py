import json
from collections import OrderedDict
from typing import Any
from typing import Dict


def convert_raw_subscription_to_present(
    hub, raw_resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    """
    Util functions to convert raw resource state to present input format for SNS topic_subscription.

    """
    raw_attributes = raw_resource.get("Attributes")
    resource_id = raw_attributes.get("SubscriptionArn")
    resource_parameters = OrderedDict(
        {
            "TopicArn": "topic_arn",
            "Protocol": "protocol",
            "Endpoint": "endpoint",
        }
    )
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource.get("Attributes"):
            resource_translated[parameter_present] = raw_resource.get("Attributes").get(
                parameter_raw
            )

    attribute_params = [
        "DeliveryPolicy",
        "FilterPolicy",
        "RawMessageDelivery",
        "RedrivePolicy",
    ]

    attributes = {}
    for param in attribute_params:
        value = raw_attributes.get(param, None)
        if value:
            attributes[param] = standardise_json(hub, value)
    resource_translated["attributes"] = attributes

    return resource_translated


def convert_raw_topic_to_present(
    hub,
    raw_resource: Dict[str, Any],
    raw_resource_tags: Dict[str, Any],
    idem_resource_name: str = None,
) -> Dict[str, Any]:
    """
    Util functions to convert raw resource state to present input format for SNS topic.

    """
    raw_attributes = raw_resource.get("Attributes")
    resource_id = raw_attributes.get("TopicArn")
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    attribute_params = [
        "DeliveryPolicy",
        "DisplayName",
        "FifoTopic",
        "Policy",
        "KmsMasterKeyId",
        "ContentBasedDeduplication",
    ]

    attributes = {}
    for param in attribute_params:
        value = raw_attributes.get(param, None)
        if value:
            attributes[param] = standardise_json(hub, value)

    resource_translated["attributes"] = attributes

    if raw_resource_tags.get("ret") and raw_resource_tags.get("ret").get("Tags"):
        resource_translated["tags"] = raw_resource_tags.get("ret").get("Tags")

    return resource_translated


def convert_raw_topic_policy_to_present(
    hub, raw_resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    """
    Util functions to convert raw resource state to present input format for SNS topic_policy.

    """
    raw_attributes = raw_resource["ret"].get("Attributes")
    resource_id = raw_attributes.get("TopicArn") + "-policy"
    resource_translated = {
        "name": idem_resource_name,
        "resource_id": resource_id,
        "topic_arn": raw_attributes.get("TopicArn"),
        "policy": standardise_json(hub, raw_attributes.get("Policy")),
    }

    return resource_translated


def standardise_json(hub, value: str):
    """
    Utils function for standardising the json string format for SNS resources
    """
    if value is None:
        return None
    try:
        temp_value = json.loads(value)
        result = json.dumps(temp_value, separators=(", ", ": "))
    except (ValueError, TypeError) as e:
        # json.loads() only works on json string, normal string do not require standardisation so returning
        # the same string back
        hub.log.debug(
            "Was expecting a json string to standardise but received a normal string,so returning the string as it is."
            + str(e)
        )
        result = value
    return result
