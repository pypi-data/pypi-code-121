from typing import Any
from typing import Dict
from typing import List


async def update_elasticache_parameters(
    hub,
    ctx,
    resource_id: str,
    old_parameters: List[Dict[str, Any]],
    parameter_name_values: List[Dict[str, Any]],
):
    """

    Args:
        hub:
        ctx:
        resource_id(Text): aws resource name
        old_parameters(List): list of old parameters
        parameter_name_values(List): list of required parameters

    Returns:
        {"result": True|False, "comment": "A tuple", "is_updated": True|False}

    """
    result = dict(comment=(), result=True, ret=None, is_updated=False)
    try:
        parameters_to_update = hub.tool.aws.elasticache.elasticache_utils.get_updated_cache_parameter_group(
            old_parameters, parameter_name_values
        )

        if parameters_to_update:
            n = len(parameters_to_update)

            # Can modify up to 20 parameters in a single request
            for i in range(0, n, 20):
                final_range = n if i + 20 > n else 20
                update_ret = await hub.exec.boto3.client.elasticache.modify_cache_parameter_group(
                    ctx=ctx,
                    CacheParameterGroupName=resource_id,
                    ParameterNameValues=parameters_to_update[i : i + final_range],
                )
                if not update_ret["result"]:
                    result["comment"] = update_ret["comment"]
                    result["result"] = False
                    return result
            if n > 0:
                result["is_updated"] = True
    except Exception as e:
        result["comment"] = result["comment"] + (str(e),)
        result["result"] = False
        return result

    return result
