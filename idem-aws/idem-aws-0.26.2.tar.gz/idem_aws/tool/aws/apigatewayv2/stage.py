from collections import OrderedDict
from typing import Any
from typing import Dict

"""
Util functions for AWS API Gateway v2 Stage resources.
"""


def convert_raw_stage_to_present(
    hub, api_id: str, raw_resource: Dict[str, Any]
) -> Dict[str, Any]:
    r"""
    Convert AWS API Gateway v2 Stage resource to a common idem present state.

    Args:
        hub: required for functions in hub.
        api_id(string): The API resource identifier in Amazon Web Services.
        raw_resource(Dict[str, Any]): The AWS response to convert.

    Returns:
        Dict[str, Any]: Common idem present state
    """

    resource_parameters = OrderedDict(
        {
            "AccessLogSettings": "access_log_settings",
            "ApiGatewayManaged": "api_gateway_managed",
            "AutoDeploy": "auto_deploy",
            "ClientCertificateId": "client_certificate_id",
            "DefaultRouteSettings": "default_route_settings",
            "DeploymentId": "deployment_id",
            "Description": "description",
            "LastDeploymentStatusMessage": "last_deployment_status_message",
            "RouteSettings": "route_settings",
            "StageVariables": "stage_variables",
            "Tags": "tags",
        }
    )
    resource_translated = {
        "resource_id": raw_resource.get("StageName"),
        "name": raw_resource.get("StageName"),
        "api_id": api_id,
    }

    for parameter_raw, parameter_present in resource_parameters.items():
        if raw_resource.get(parameter_raw) is not None:
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)

    return resource_translated
