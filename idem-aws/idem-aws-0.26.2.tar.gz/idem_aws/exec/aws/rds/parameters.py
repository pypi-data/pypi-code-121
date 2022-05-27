import copy
from typing import Any
from typing import Dict
from typing import List


async def modify_db_group_parameters(
    hub,
    ctx,
    resource_name,
    old_parameters: List[Dict[str, Any]],
    new_parameters: List[Dict[str, Any]],
):
    """
    Update parameters of AWS RDS resources

    Args:
        hub:
        ctx:
        resource_name: aws resource name
        old_parameters: list of old parameters
        new_parameters: list of new parameters

    Returns:
        {"result": True|False, "comment": "A message", "ret": None}

    """
    parameters_to_modify = []
    parameters_to_remove = []
    old_parameters_map = {
        parameter.get("name"): parameter for parameter in old_parameters or []
    }
    parameters_result = copy.deepcopy(old_parameters_map)
    if new_parameters is not None:
        for parameter in new_parameters:
            if parameter.get("name") in old_parameters_map:
                if parameter.get("value") != old_parameters_map.get(
                    parameter.get("name")
                ).get("value"):
                    parameters_to_modify.append(parameter)
                    parameters_to_remove.append(
                        old_parameters_map.get(parameter.get("name"))
                    )
    result = dict(comment=(), result=True, ret=None)
    if not parameters_to_modify:
        return result
    if parameters_to_modify:
        if not ctx.get("test", False):
            update_payload_parameters = []
            for parameter in parameters_to_modify:
                update_payload_parameter = {}
                if parameter["apply_method"] is not None:
                    update_payload_parameter["ApplyMethod"] = parameter["apply_method"]
                if parameter["name"]:
                    update_payload_parameter["ParameterName"] = parameter["name"]
                if parameter["value"]:
                    update_payload_parameter["ParameterValue"] = parameter["value"]
                update_payload_parameters.append(update_payload_parameter)

            update_parameters_ret = (
                await hub.exec.boto3.client.rds.modify_db_parameter_group(
                    ctx,
                    DBParameterGroupName=resource_name,
                    Parameters=update_payload_parameters,
                )
            )
            if not update_parameters_ret["result"]:
                result["comment"] = update_parameters_ret["comment"]
                result["result"] = False
                return result
    for parameter in parameters_to_modify:
        parameters_result[parameter["name"]] = parameter

    result["ret"] = {"parameters": list(parameters_result.values())}
    result["comment"] = result["comment"] + (
        f"Update parameters: Add [{parameters_to_modify}] Remove [{parameters_to_remove}]",
    )
    return result
