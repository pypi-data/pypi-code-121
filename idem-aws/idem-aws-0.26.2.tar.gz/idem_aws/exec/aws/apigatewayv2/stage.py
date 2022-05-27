from collections import OrderedDict
from typing import Any
from typing import Dict

"""
Exec functions for AWS API Gateway v2 Stage resources.
"""


async def update_stage(
    hub,
    ctx,
    api_id: str,
    resource_id: str,
    raw_resource: Dict[str, Any],
    resource_parameters: Dict[str, None],
) -> Dict[str, Any]:
    r"""
    Updates an AWS API Gateway v2 Stage resource.

    Args:
        hub: required for functions in hub.
        ctx: context.
        api_id(string): The API resource identifier in Amazon Web Services.
        resource_id(string): The Stage resource identifier in Amazon Web Services.
        raw_resource(Dict): Existing resource parameters in Amazon Web Services.
        resource_parameters(Dict): Parameters from SLS file.

    Returns:
        Dict[str, Any]
    """

    result = dict(comment=(), result=True, ret=None)

    parameters = OrderedDict(
        {
            "AccessLogSettings": "access_log_settings",
            "AutoDeploy": "auto_deploy",
            "ClientCertificateId": "client_certificate_id",
            "DefaultRouteSettings": "default_route_settings",
            "DeploymentId": "deployment_id",
            "Description": "description",
            "RouteSettings": "route_settings",
            "StageVariables": "stage_variables",
        }
    )

    parameters_to_update = {}

    for key, value in resource_parameters.items():
        if value is not None and value != raw_resource.get(key):
            parameters_to_update[key] = resource_parameters[key]

    if parameters_to_update:
        result["ret"] = {}
        for parameter_raw, parameter_present in parameters.items():
            if parameter_raw in parameters_to_update:
                result["ret"][parameter_present] = parameters_to_update[parameter_raw]

        if ctx.get("test", False):
            result["comment"] = (
                f"Would update parameters: " + ",".join(result["ret"].keys()),
            )
        else:
            update_ret = await hub.exec.boto3.client.apigatewayv2.update_stage(
                ctx,
                ApiId=api_id,
                StageName=resource_id,
                **parameters_to_update,
            )
            if not update_ret["result"]:
                result["result"] = False
                result["comment"] = update_ret["comment"]
                return result

            result["comment"] = (
                f"Updated parameters: " + ",".join(result["ret"].keys()),
            )

    return result
