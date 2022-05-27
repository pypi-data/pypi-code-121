from collections import OrderedDict
from typing import Any
from typing import Dict

"""
Util functions for AWS API Gateway v2 Route resources.
"""


def convert_raw_route_to_present(
    hub, api_id: str, raw_resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    r"""
    Convert AWS API Gateway v2 Route resource to a common idem present state.

    Args:
        hub: required for functions in hub.
        api_id(string): The API resource identifier in Amazon Web Services.
        raw_resource(Dict[str, Any]): The AWS response to convert.
        idem_resource_name(string, optional): An Idem name of the resource.

    Returns:
        Dict[str, Any]: Common idem present state
    """

    resource_parameters = OrderedDict(
        {
            "ApiGatewayManaged": "api_gateway_managed",
            "ApiKeyRequired": "api_key_required",
            "AuthorizationScopes": "authorization_scopes",
            "AuthorizationType": "authorization_type",
            "AuthorizerId": "authorizer_id",
            "ModelSelectionExpression": "model_selection_expression",
            "OperationName": "operation_name",
            "RequestModels": "request_models",
            "RequestParameters": "request_parameters",
            "RouteId": "route_id",
            "RouteKey": "route_key",
            "RouteResponseSelectionExpression": "route_response_selection_expression",
            "Target": "target",
        }
    )
    resource_translated = {
        "name": idem_resource_name
        if idem_resource_name
        else raw_resource.get("RouteId"),
        "resource_id": raw_resource.get("RouteId"),
        "api_id": api_id,
    }

    for parameter_raw, parameter_present in resource_parameters.items():
        if raw_resource.get(parameter_raw) is not None:
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)

    return resource_translated
