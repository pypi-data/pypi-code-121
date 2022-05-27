from collections import OrderedDict
from typing import Any
from typing import Dict
from typing import List


def convert_raw_db_parameter_group_to_present(
    hub,
    raw_resource: Dict[str, Any],
    idem_resource_name: str = None,
    parameters: List[Dict[str, Any]] = None,
    tags: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Convert AWS returned data structure to correct idem db_parameter_group present state

     Args:
        hub: required for functions in hub
        raw_resource: The aws response to convert
        idem_resource_name (Text, Optional): The idem of the idem resource
        Parameters (List[Dict[str, str]], Optional): The Parameter list of the resource. Defaults to None.
        tags (List, Optional): The tags of the resource. Defaults to None.

    Returns: Valid idem state for db_parameter_group of type Dict['string', Any]
    """
    resource_id = raw_resource.get("DBParameterGroupName")
    raw_resource["Tags"] = tags
    raw_resource["Parameters"] = parameters
    resource_parameters = OrderedDict(
        {
            "DBParameterGroupFamily": "db_parameter_group_family",
            "Description": "description",
            "Tags": "tags",
            "Parameters": "parameters",
        }
    )
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    for parameter_raw, parameter_present in resource_parameters.items():
        if raw_resource.get(parameter_raw) is not None:
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)
    return resource_translated
