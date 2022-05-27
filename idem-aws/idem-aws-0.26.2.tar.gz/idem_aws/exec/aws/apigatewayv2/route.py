from collections import OrderedDict
from typing import Any
from typing import Dict

"""
Exec functions for AWS API Gateway v2 Route resources.
"""


async def update_route(
    hub,
    ctx,
    api_id: str,
    resource_id: str,
    raw_resource: Dict[str, Any],
    resource_parameters: Dict[str, None],
) -> Dict[str, Any]:
    r"""
    Updates an AWS API Gateway v2 Route resource.

    Args:
        hub: required for functions in hub.
        ctx: context.
        api_id(string): The API resource identifier in Amazon Web Services.
        resource_id(string): The Route resource identifier in Amazon Web Services.
        raw_resource(Dict): Existing resource parameters in Amazon Web Services.
        resource_parameters(Dict): Parameters from SLS file.

    Returns:
        Dict[str, Any]
    """

    result = dict(comment=(), result=True, ret=None)

    parameters = OrderedDict(
        {
            "ApiKeyRequired": "api_key_required",
            "AuthorizationScopes": "authorization_scopes",
            "AuthorizationType": "authorization_type",
            "AuthorizerId": "authorizer_id",
            "ModelSelectionExpression": "model_selection_expression",
            "OperationName": "operation_name",
            "RequestModels": "request_models",
            "RequestParameters": "request_parameters",
            "RouteKey": "route_key",
            "RouteResponseSelectionExpression": "route_response_selection_expression",
            "Target": "target",
        }
    )

    parameters_to_update = {}

    authorization_scopes = resource_parameters.get("AuthorizationScopes")
    if authorization_scopes is not None:
        if not hub.tool.aws.state_comparison_utils.are_lists_identical(
            authorization_scopes,
            raw_resource.get("AuthorizationScopes"),
        ):
            parameters_to_update["AuthorizationScopes"] = authorization_scopes

        resource_parameters.pop("AuthorizationScopes")

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
            update_ret = await hub.exec.boto3.client.apigatewayv2.update_route(
                ctx,
                ApiId=api_id,
                RouteId=resource_id,
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
