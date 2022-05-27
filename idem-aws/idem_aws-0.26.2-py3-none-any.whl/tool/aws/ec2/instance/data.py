"""
Functions to sanitize the data in a present state
"""
import datetime
from typing import Any
from typing import Dict
from typing import List


def sanitize_dict(hub, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Iterate over a present state and verify that all the options are serializable
    """
    result = {}

    for key, value in data.items():
        if value is None:
            continue
        result[key] = hub.tool.aws.ec2.instance.data.sanitize_value(value)

    return result


def sanitize_list(hub, data: List[Any]) -> List[Any]:
    """
    Iterate over a present state and verify that all the options are serializable
    """
    result = []

    for value in data:
        if value is None:
            continue
        result.append(hub.tool.aws.ec2.instance.data.sanitize_value(value))

    return result


def sanitize_value(hub, data: Any) -> Any:
    """
    Iterate over a present state and verify that all the options are serializable
    """

    if isinstance(data, Dict):
        return hub.tool.aws.ec2.instance.data.sanitize_dict(data)
    elif isinstance(data, datetime.datetime):
        return str(data)
    elif isinstance(data, List):
        return hub.tool.aws.ec2.instance.data.sanitize_list(data)
    else:
        return data
