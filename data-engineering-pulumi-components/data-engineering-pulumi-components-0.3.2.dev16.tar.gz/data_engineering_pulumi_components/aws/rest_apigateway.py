from typing import Optional

from data_engineering_pulumi_components.utils import Tagger
from pulumi import ComponentResource, ResourceOptions
import pulumi_aws as aws


class RestApigatewayService(ComponentResource):
    def __init__(
        self,
        name: str,
        tagger: Tagger,
        t: Optional[str] = None,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        """
        Encapsulates Amazon API Gateway functions that are used to
        create a REST API that integrates with another AWS service.
        Parameters
        ----------
        name : str
            The name of the resource.
        tagger : Tagger
            A tagger resource.
        t: The type of this resource.
        opts : Optional[ResourceOptions]
            Options for the resource. By default, None.
        """
        if t is None:
            t = "data-engineering-pulumi-components:aws:RestApi"

        super().__init__(
            t=t,
            name=name,
            props=None,
            opts=opts,
        )

        self._name = name
        self._resources = {}
        self._methods = {}
        self._integrations = {}
        self._response200 = {}

        self._api = aws.apigateway.RestApi(
            f"{self._name}-api",
            endpoint_configuration=aws.apigateway.RestApiEndpointConfigurationArgs(
                types="REGIONAL"
            ),
            tags=tagger.create_tags(name=f"{name}-api"),
        )

    def resource(self, path_part: str):
        self._resources[path_part] = aws.apigateway.Resource(
            f"{self._name}-resource-{path_part}",
            path_part=path_part,
            parent_id=self._api.root_resource_id,
            rest_api=self._api.id,
        )

    def method(
        self,
        http_method: str,
        authorisation_type: str,
        method_request_param: dict,
        gateway_authoriser_id: str,
        path_part: str,
    ):
        self._methods[path_part] = aws.apigateway.Method(
            f"{self._name}-method-{path_part}",
            rest_api=self._api.id,
            resource_id=self._resources[path_part].id,
            http_method=http_method,
            authorization=authorisation_type,
            authorizer_id=gateway_authoriser_id,
            request_parameters=method_request_param,
            opts=ResourceOptions(depends_on=[self._resources[path_part]]),
        )

    def integration(
        self,
        integration_http_method: str,
        integration_type: str,
        integration_request_param: dict,
        lambda_forwarder_invoke_arn: str,
        path_part: str,
    ):
        self._integrations[path_part] = aws.apigateway.Integration(
            f"{self._name}-integration-{path_part}",
            rest_api=self._api.id,
            resource_id=self._resources[path_part].id,
            http_method=self._methods[path_part].http_method,
            integration_http_method=integration_http_method,
            type=integration_type,
            uri=lambda_forwarder_invoke_arn,
            request_parameters=integration_request_param,
            opts=ResourceOptions(
                depends_on=[self._resources[path_part], self._methods[path_part]]
            ),
        )

    def method_response(self, status_code: str, path_part: str):
        self._response200[path_part] = aws.apigateway.MethodResponse(
            f"{self._name}-method-response-{path_part}",
            rest_api=self._api.id,
            resource_id=self._resources[path_part].id,
            http_method=self._methods[path_part].http_method,
            status_code=status_code,
            opts=ResourceOptions(
                depends_on=[self._resources[path_part], self._methods[path_part]]
            ),
        )

    def deployment(self, stage_name: str):
        # List all components to be created before the deployment
        # Resources and methods not needed, as their integrations already depend on them
        # But not all integrations need a response200, so list both here
        dependencies = list(self._integrations.values()) + list(
            self._response200.values()
        )

        self._deployment = aws.apigateway.Deployment(
            f"{self._name}-deployment",
            rest_api=self._api,
            stage_name=stage_name,
            opts=ResourceOptions(depends_on=dependencies),
        )
