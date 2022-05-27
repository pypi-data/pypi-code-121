from collections import OrderedDict
from typing import Any
from typing import Dict


def convert_raw_db_subnet_group_to_present(
    hub,
    raw_resource: Dict[str, Any],
    idem_resource_name: str = None,
    tags: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Convert AWS returned data structure to correct idem db_subnet_group present state

     Args:
        hub: required for functions in hub
        raw_resource: The aws response to convert
        idem_resource_name (Text, Optional): The idem name of the resource
        tags (List, Optional): The tags of the resource. Defaults to None.

    Returns: Valid idem state for db_subnet_group of type Dict['string', Any]
    """
    resource_id = raw_resource.get("DBSubnetGroupName")
    raw_resource["Tags"] = tags
    resource_parameters = OrderedDict(
        {
            "DBSubnetGroupDescription": "db_subnet_group_description",
            "Subnets": "subnet_ids",
            "Tags": "tags",
        }
    )
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    for parameter_raw, parameter_present in resource_parameters.items():
        if raw_resource.get(parameter_raw) is not None:
            if parameter_raw == "Subnets":
                resource_translated[parameter_present] = [
                    subnet["SubnetIdentifier"] for subnet in raw_resource.get("Subnets")
                ]
            else:
                resource_translated[parameter_present] = raw_resource.get(parameter_raw)

    return resource_translated
