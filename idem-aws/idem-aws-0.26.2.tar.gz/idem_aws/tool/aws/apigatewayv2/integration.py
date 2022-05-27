from collections import OrderedDict
from typing import Any
from typing import Dict

"""
Util functions for AWS API Gateway v2 Integration resources.
"""


def convert_raw_integration_to_present(
    hub, api_id: str, raw_resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    r"""
    Convert AWS API Gateway v2 Integration resource to a common idem present state.

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
            "ConnectionId": "connection_id",
            "ConnectionType": "connection_type",
            "ContentHandlingStrategy": "content_handling_strategy",
            "CredentialsArn": "credentials_arn",
            "Description": "description",
            "IntegrationMethod": "integration_method",
            "IntegrationResponseSelectionExpression": "integration_response_selection_expression",
            "IntegrationSubtype": "integration_subtype",
            "IntegrationType": "integration_type",
            "IntegrationUri": "integration_uri",
            "PassthroughBehavior": "passthrough_behavior",
            "PayloadFormatVersion": "payload_format_version",
            "RequestParameters": "request_parameters",
            "RequestTemplates": "request_templates",
            "ResponseParameters": "response_parameters",
            "TemplateSelectionExpression": "template_selection_expression",
            "TimeoutInMillis": "timeout_in_millis",
            "TlsConfig": "tls_config",
        }
    )
    resource_translated = {
        "name": idem_resource_name
        if idem_resource_name
        else raw_resource.get("IntegrationId"),
        "resource_id": raw_resource.get("IntegrationId"),
        "api_id": api_id,
    }

    for parameter_raw, parameter_present in resource_parameters.items():
        if raw_resource.get(parameter_raw) is not None:
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)

    return resource_translated
