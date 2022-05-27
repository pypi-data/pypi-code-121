from collections import OrderedDict
from typing import Any
from typing import Dict

"""
Util functions for AWS API Gateway v2 API resources.
"""


def convert_raw_api_to_present(hub, raw_resource: Dict[str, Any]) -> Dict[str, Any]:
    r"""
    Convert AWS API Gateway v2 API resource to a common idem present state.

    Args:
        hub: required for functions in hub.
        raw_resource(Dict[str, Any]): The AWS response to convert.

    Returns:
        Dict[str, Any]: Common idem present state
    """

    resource_parameters = OrderedDict(
        {
            "ApiEndpoint": "api_endpoint",
            "ApiGatewayManaged": "api_gateway_managed",
            "ApiId": "api_id",
            "ApiKeySelectionExpression": "api_key_selection_expression",
            "CorsConfiguration": "cors_configuration",
            "Description": "description",
            "DisableExecuteApiEndpoint": "disable_execute_api_endpoint",
            "DisableSchemaValidation": "disable_schema_validation",
            "Name": "name",
            "ProtocolType": "protocol_type",
            "RouteSelectionExpression": "route_selection_expression",
            "Tags": "tags",
            "Version": "version",
        }
    )
    resource_translated = {
        "resource_id": raw_resource.get("ApiId"),
    }

    for parameter_raw, parameter_present in resource_parameters.items():
        if raw_resource.get(parameter_raw) is not None:
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)

    return resource_translated
