from typing import Any
from typing import Dict


async def update_rule(
    hub,
    ctx,
    resource_id: str,
    before: Dict[str, Any],
    source: Dict[str, Any],
    scope: Dict[str, Any],
    frequency: str = Any,
    input_parameters: str = Any,
):
    """
    Update rule of AWS Config rule

    Args:
        hub: The redistributed pop central hub.
        ctx: A dict with the keys/values for the execution of the Idem run located in
        `hub.idem.RUNS[ctx['run_name']]`.
        resource_id: AWS Config rule name
        before: Contains current configuration for the resource
        source: Dict. The rule owner, the rule identifier. Required for update.
        scope: Dict. Defines which resources can trigger an evaluation for the rule. The scope can include one or more
         resource types, a combination of one resource type.
        frequency: String. The maximum frequency with which Config runs evaluations for a rule.
        input_parameters: A string, in JSON format

    Returns:
        {"result": True|False, "comment": Tuple, "ret": Dict}
    """
    result = dict(comment=(), result=True, ret=None)
    update_payload = {}
    update = False
    for key, value in {
        "MaximumExecutionFrequency": frequency,
        "Scope": scope,
        "InputParameters": input_parameters,
    }.items():
        if value is not None:
            if before.get(key) != value:
                update = True
            update_payload[key] = value
    if update:
        update_payload["ConfigRuleName"] = resource_id
        update_payload["Source"] = source
        if not ctx.get("test", False):
            update_ret = await hub.exec.boto3.client.config.put_config_rule(
                ctx=ctx, ConfigRule=update_payload
            )
            if not update_ret["result"]:
                result["comment"] = update_ret["comment"]
                result["result"] = False
                return result
        result["ret"] = {}
        for key, mapped_key in {
            "MaximumExecutionFrequency": "max_execution_frequency",
            "Scope": "scope",
            "InputParameters": "input_parameters",
        }.items():
            if key in update_payload:
                if (update_payload[key] is not None) and before.get(
                    key
                ) != update_payload[key]:
                    result["ret"][mapped_key] = update_payload[key]
                    result["comment"] = result["comment"] + (
                        f"Updated {mapped_key}: {update_payload[key]}",
                    )
    return result
