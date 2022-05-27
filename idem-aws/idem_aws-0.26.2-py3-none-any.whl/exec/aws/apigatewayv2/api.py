from collections import OrderedDict
from typing import Any
from typing import Dict

"""
Exec functions for AWS API Gateway v2 API resources.
"""


async def update_api(
    hub,
    ctx,
    resource_id: str,
    raw_resource: Dict[str, Any],
    resource_parameters: Dict[str, None],
) -> Dict[str, Any]:
    r"""
    Updates an AWS API Gateway v2 API resource.

    Args:
        hub: required for functions in hub.
        ctx: context.
        resource_id(string): The API resource identifier in Amazon Web Services.
        raw_resource(Dict): Existing resource parameters in Amazon Web Services.
        resource_parameters(Dict): Parameters from SLS file.

    Returns:
        Dict[str, Any]
    """

    result = dict(comment=(), result=True, ret=None)

    parameters = OrderedDict(
        {
            "ApiKeySelectionExpression": "api_key_selection_expression",
            "CorsConfiguration": "cors_configuration",
            "CredentialsArn": "credentials_arn",
            "Description": "description",
            "DisableExecuteApiEndpoint": "disable_execute_api_endpoint",
            "DisableSchemaValidation": "disable_schema_validation",
            "RouteKey": "route_key",
            "RouteSelectionExpression": "route_selection_expression",
            "Target": "target",
            "Version": "version",
        }
    )

    parameters_to_update = {}

    cors_configuration = resource_parameters.get("CorsConfiguration")
    if cors_configuration is not None:
        update_cors_configuration = False
        old_cors_configuration = raw_resource.get("CorsConfiguration")

        if cors_configuration.get(
            "AllowCredentials"
        ) is not None and cors_configuration.get(
            "AllowCredentials"
        ) != old_cors_configuration.get(
            "MaxAge"
        ):
            update_cors_configuration = True
        elif (
            not hub.tool.aws.state_comparison_utils.are_lists_identical(
                cors_configuration.get("AllowHeaders"),
                old_cors_configuration.get("AllowHeaders"),
            )
            or not hub.tool.aws.state_comparison_utils.are_lists_identical(
                cors_configuration.get("AllowMethods"),
                old_cors_configuration.get("AllowMethods"),
            )
            or not hub.tool.aws.state_comparison_utils.are_lists_identical(
                cors_configuration.get("AllowOrigins"),
                old_cors_configuration.get("AllowOrigins"),
            )
            or not hub.tool.aws.state_comparison_utils.are_lists_identical(
                cors_configuration.get("ExposeHeaders"),
                old_cors_configuration.get("ExposeHeaders"),
            )
        ):
            update_cors_configuration = True
        elif cors_configuration.get("MaxAge") is not None and cors_configuration.get(
            "MaxAge"
        ) != old_cors_configuration.get("MaxAge"):
            update_cors_configuration = True

        if update_cors_configuration:
            parameters_to_update["CorsConfiguration"] = cors_configuration

        resource_parameters.pop("CorsConfiguration")

    for key, value in resource_parameters.items():
        if value is not None and value != raw_resource[key]:
            parameters_to_update[key] = resource_parameters[key]

    if parameters_to_update:
        result["ret"] = {}
        for parameter_raw, parameter_present in parameters.items():
            if parameter_raw in parameters_to_update:
                result["ret"][parameter_present] = parameters_to_update[parameter_raw]

        if ctx.get("test", False):
            result["comment"] = (
                "Would update parameters: " + ",".join(result["ret"].keys()),
            )
        else:
            update_ret = await hub.exec.boto3.client.apigatewayv2.update_api(
                ctx,
                ApiId=resource_id,
                **parameters_to_update,
            )
            if not update_ret["result"]:
                result["result"] = False
                result["comment"] = update_ret["comment"]
                return result

            result["comment"] = (
                "Updated parameters: " + ",".join(result["ret"].keys()),
            )

    return result
