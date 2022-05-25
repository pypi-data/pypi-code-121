"""
Main interface for apigateway service.

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_apigateway import (
        APIGatewayClient,
        Client,
        GetApiKeysPaginator,
        GetAuthorizersPaginator,
        GetBasePathMappingsPaginator,
        GetClientCertificatesPaginator,
        GetDeploymentsPaginator,
        GetDocumentationPartsPaginator,
        GetDocumentationVersionsPaginator,
        GetDomainNamesPaginator,
        GetGatewayResponsesPaginator,
        GetModelsPaginator,
        GetRequestValidatorsPaginator,
        GetResourcesPaginator,
        GetRestApisPaginator,
        GetSdkTypesPaginator,
        GetUsagePaginator,
        GetUsagePlanKeysPaginator,
        GetUsagePlansPaginator,
        GetVpcLinksPaginator,
    )

    session = Session()
    client: APIGatewayClient = session.client("apigateway")

    get_api_keys_paginator: GetApiKeysPaginator = client.get_paginator("get_api_keys")
    get_authorizers_paginator: GetAuthorizersPaginator = client.get_paginator("get_authorizers")
    get_base_path_mappings_paginator: GetBasePathMappingsPaginator = client.get_paginator("get_base_path_mappings")
    get_client_certificates_paginator: GetClientCertificatesPaginator = client.get_paginator("get_client_certificates")
    get_deployments_paginator: GetDeploymentsPaginator = client.get_paginator("get_deployments")
    get_documentation_parts_paginator: GetDocumentationPartsPaginator = client.get_paginator("get_documentation_parts")
    get_documentation_versions_paginator: GetDocumentationVersionsPaginator = client.get_paginator("get_documentation_versions")
    get_domain_names_paginator: GetDomainNamesPaginator = client.get_paginator("get_domain_names")
    get_gateway_responses_paginator: GetGatewayResponsesPaginator = client.get_paginator("get_gateway_responses")
    get_models_paginator: GetModelsPaginator = client.get_paginator("get_models")
    get_request_validators_paginator: GetRequestValidatorsPaginator = client.get_paginator("get_request_validators")
    get_resources_paginator: GetResourcesPaginator = client.get_paginator("get_resources")
    get_rest_apis_paginator: GetRestApisPaginator = client.get_paginator("get_rest_apis")
    get_sdk_types_paginator: GetSdkTypesPaginator = client.get_paginator("get_sdk_types")
    get_usage_paginator: GetUsagePaginator = client.get_paginator("get_usage")
    get_usage_plan_keys_paginator: GetUsagePlanKeysPaginator = client.get_paginator("get_usage_plan_keys")
    get_usage_plans_paginator: GetUsagePlansPaginator = client.get_paginator("get_usage_plans")
    get_vpc_links_paginator: GetVpcLinksPaginator = client.get_paginator("get_vpc_links")
    ```
"""
from .client import APIGatewayClient
from .paginator import (
    GetApiKeysPaginator,
    GetAuthorizersPaginator,
    GetBasePathMappingsPaginator,
    GetClientCertificatesPaginator,
    GetDeploymentsPaginator,
    GetDocumentationPartsPaginator,
    GetDocumentationVersionsPaginator,
    GetDomainNamesPaginator,
    GetGatewayResponsesPaginator,
    GetModelsPaginator,
    GetRequestValidatorsPaginator,
    GetResourcesPaginator,
    GetRestApisPaginator,
    GetSdkTypesPaginator,
    GetUsagePaginator,
    GetUsagePlanKeysPaginator,
    GetUsagePlansPaginator,
    GetVpcLinksPaginator,
)

Client = APIGatewayClient


__all__ = (
    "APIGatewayClient",
    "Client",
    "GetApiKeysPaginator",
    "GetAuthorizersPaginator",
    "GetBasePathMappingsPaginator",
    "GetClientCertificatesPaginator",
    "GetDeploymentsPaginator",
    "GetDocumentationPartsPaginator",
    "GetDocumentationVersionsPaginator",
    "GetDomainNamesPaginator",
    "GetGatewayResponsesPaginator",
    "GetModelsPaginator",
    "GetRequestValidatorsPaginator",
    "GetResourcesPaginator",
    "GetRestApisPaginator",
    "GetSdkTypesPaginator",
    "GetUsagePaginator",
    "GetUsagePlanKeysPaginator",
    "GetUsagePlansPaginator",
    "GetVpcLinksPaginator",
)
