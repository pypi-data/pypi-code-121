from collections import OrderedDict
from typing import Dict


async def update_addon(
    hub,
    ctx,
    name: str,
    before: Dict,
    addon_version: str,
    service_account_role_arn: str,
    resolve_conflicts: str,
    client_request_token: str,
    timeout: Dict = None,
):
    """
    Updates an Amazon EKS add-on.

    Args:
       hub:
       ctx:
       name: An Idem name of the resource
       before(Dict): AWS cluster addon
       addon_version(Text): The version of the add-on. The version must match one of the versions returned
                            by ` DescribeAddonVersions
       service_account_role_arn(Text): The Amazon Resource Name (ARN) of an existing IAM role to bind to the add-on's
                                       service account. The role must be assigned the IAM permissions required by the add-on. If you don't specify
                                       an existing IAM role, then the add-on uses the permissions assigned to the node IAM role.
       resolve_conflicts(Text): How to resolve parameter value conflicts when migrating an existing add-on
                                to an Amazon EKS add-on
       client_request_token(Text):Unique, case-sensitive identifier that you provide to ensure the idempotency of the request.
                                  This field is autopopulated if not provided.
       timeout(Dict, optional): Timeout configuration for creating or updating addon.
            * create (Dict) -- Timeout configuration for creating addon
                * delay(int, default=10) -- The amount of time in seconds to wait between attempts.
                * max_attempts(int, default=60) -- Customized timeout configuration containing delay and max attempts.
            * update (string) -- Timeout configuration for updating addon
                * delay(int, default=10) -- The amount of time in seconds to wait between attempts.
                * max_attempts(int, default=60) -- Customized timeout configuration containing delay and max attempts.

    Returns:
       {"result": True|False, "comment": A message Tuple, "ret": Dict}
    """
    result = dict(comment=(), result=True, ret=None)
    update_payload = {}

    if (
        service_account_role_arn
        and before.get("service_account_role_arn") != service_account_role_arn
    ):
        update_payload["serviceAccountRoleArn"] = service_account_role_arn
    if addon_version and before.get("addon_version") != addon_version:
        update_payload["addonVersion"] = addon_version
    if resolve_conflicts and before.get("resolve_conflicts") != resolve_conflicts:
        update_payload["resolveConflicts"] = resolve_conflicts
    if client_request_token:
        update_payload["clientRequestToken"] = client_request_token

    if update_payload:
        if not ctx.get("test", False):
            update_ret = await hub.exec.boto3.client.eks.update_addon(
                ctx=ctx,
                clusterName=before.get("cluster_name"),
                addonName=before.get("resource_id"),
                **update_payload,
            )
            if not update_ret["result"]:
                result["comment"] = update_ret["comment"]
                result["result"] = False
                return result
            else:
                waiter_config = hub.tool.aws.waiter_utils.create_waiter_config(
                    default_delay=10,
                    default_max_attempts=60,
                    timeout_config=timeout.get("update") if timeout else None,
                )
                hub.log.debug(f"Waiting on updating aws.eks.addon '{name}'")
                try:
                    await hub.tool.boto3.client.wait(
                        ctx,
                        "eks",
                        "addon_active",
                        addonName=before.get("resource_id"),
                        clusterName=before.get("cluster_name"),
                        WaiterConfig=waiter_config,
                    )
                except Exception as e:
                    result["comment"] = result["comment"] + (str(e),)
                    result["result"] = False
                    return result
        result["ret"] = {}
        update_params_map = OrderedDict(
            {
                "addonVersion": "addon_version",
                "serviceAccountRoleArn": "service_account_role_arn",
                "resolveConflicts": "resolve_conflicts",
            }
        )

        for parameter_raw, parameter_present in update_params_map.items():
            if parameter_raw in update_payload:
                result["ret"][parameter_present] = update_payload.get(parameter_raw)
                result["comment"] = result["comment"] + (
                    f"Update {parameter_present}: {update_payload[parameter_raw]} on addon {before.get('resource_id')}",
                )
    return result
