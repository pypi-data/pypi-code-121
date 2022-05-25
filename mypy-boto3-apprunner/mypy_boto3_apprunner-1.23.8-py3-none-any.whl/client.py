"""
Type annotations for apprunner service client.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/)

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_apprunner.client import AppRunnerClient

    session = Session()
    client: AppRunnerClient = session.client("apprunner")
    ```
"""
import sys
from typing import Any, Dict, Mapping, Sequence, Type

from botocore.client import BaseClient, ClientMeta

from .type_defs import (
    AssociateCustomDomainResponseTypeDef,
    CreateAutoScalingConfigurationResponseTypeDef,
    CreateConnectionResponseTypeDef,
    CreateObservabilityConfigurationResponseTypeDef,
    CreateServiceResponseTypeDef,
    CreateVpcConnectorResponseTypeDef,
    DeleteAutoScalingConfigurationResponseTypeDef,
    DeleteConnectionResponseTypeDef,
    DeleteObservabilityConfigurationResponseTypeDef,
    DeleteServiceResponseTypeDef,
    DeleteVpcConnectorResponseTypeDef,
    DescribeAutoScalingConfigurationResponseTypeDef,
    DescribeCustomDomainsResponseTypeDef,
    DescribeObservabilityConfigurationResponseTypeDef,
    DescribeServiceResponseTypeDef,
    DescribeVpcConnectorResponseTypeDef,
    DisassociateCustomDomainResponseTypeDef,
    EncryptionConfigurationTypeDef,
    HealthCheckConfigurationTypeDef,
    InstanceConfigurationTypeDef,
    ListAutoScalingConfigurationsResponseTypeDef,
    ListConnectionsResponseTypeDef,
    ListObservabilityConfigurationsResponseTypeDef,
    ListOperationsResponseTypeDef,
    ListServicesResponseTypeDef,
    ListTagsForResourceResponseTypeDef,
    ListVpcConnectorsResponseTypeDef,
    NetworkConfigurationTypeDef,
    PauseServiceResponseTypeDef,
    ResumeServiceResponseTypeDef,
    ServiceObservabilityConfigurationTypeDef,
    SourceConfigurationTypeDef,
    StartDeploymentResponseTypeDef,
    TagTypeDef,
    TraceConfigurationTypeDef,
    UpdateServiceResponseTypeDef,
)

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = ("AppRunnerClient",)


class BotocoreClientError(BaseException):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str


class Exceptions:
    ClientError: Type[BotocoreClientError]
    InternalServiceErrorException: Type[BotocoreClientError]
    InvalidRequestException: Type[BotocoreClientError]
    InvalidStateException: Type[BotocoreClientError]
    ResourceNotFoundException: Type[BotocoreClientError]
    ServiceQuotaExceededException: Type[BotocoreClientError]


class AppRunnerClient(BaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        AppRunnerClient exceptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.exceptions)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#exceptions)
        """

    def associate_custom_domain(
        self, *, ServiceArn: str, DomainName: str, EnableWWWSubdomain: bool = ...
    ) -> AssociateCustomDomainResponseTypeDef:
        """
        Associate your own domain name with the App Runner subdomain URL of your App
        Runner service.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.associate_custom_domain)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#associate_custom_domain)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.can_paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#can_paginate)
        """

    def create_auto_scaling_configuration(
        self,
        *,
        AutoScalingConfigurationName: str,
        MaxConcurrency: int = ...,
        MinSize: int = ...,
        MaxSize: int = ...,
        Tags: Sequence[TagTypeDef] = ...
    ) -> CreateAutoScalingConfigurationResponseTypeDef:
        """
        Create an App Runner automatic scaling configuration resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.create_auto_scaling_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#create_auto_scaling_configuration)
        """

    def create_connection(
        self,
        *,
        ConnectionName: str,
        ProviderType: Literal["GITHUB"],
        Tags: Sequence[TagTypeDef] = ...
    ) -> CreateConnectionResponseTypeDef:
        """
        Create an App Runner connection resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.create_connection)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#create_connection)
        """

    def create_observability_configuration(
        self,
        *,
        ObservabilityConfigurationName: str,
        TraceConfiguration: TraceConfigurationTypeDef = ...,
        Tags: Sequence[TagTypeDef] = ...
    ) -> CreateObservabilityConfigurationResponseTypeDef:
        """
        Create an App Runner observability configuration resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.create_observability_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#create_observability_configuration)
        """

    def create_service(
        self,
        *,
        ServiceName: str,
        SourceConfiguration: SourceConfigurationTypeDef,
        InstanceConfiguration: InstanceConfigurationTypeDef = ...,
        Tags: Sequence[TagTypeDef] = ...,
        EncryptionConfiguration: EncryptionConfigurationTypeDef = ...,
        HealthCheckConfiguration: HealthCheckConfigurationTypeDef = ...,
        AutoScalingConfigurationArn: str = ...,
        NetworkConfiguration: NetworkConfigurationTypeDef = ...,
        ObservabilityConfiguration: ServiceObservabilityConfigurationTypeDef = ...
    ) -> CreateServiceResponseTypeDef:
        """
        Create an App Runner service.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.create_service)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#create_service)
        """

    def create_vpc_connector(
        self,
        *,
        VpcConnectorName: str,
        Subnets: Sequence[str],
        SecurityGroups: Sequence[str] = ...,
        Tags: Sequence[TagTypeDef] = ...
    ) -> CreateVpcConnectorResponseTypeDef:
        """
        Create an App Runner VPC connector resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.create_vpc_connector)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#create_vpc_connector)
        """

    def delete_auto_scaling_configuration(
        self, *, AutoScalingConfigurationArn: str
    ) -> DeleteAutoScalingConfigurationResponseTypeDef:
        """
        Delete an App Runner automatic scaling configuration resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.delete_auto_scaling_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#delete_auto_scaling_configuration)
        """

    def delete_connection(self, *, ConnectionArn: str) -> DeleteConnectionResponseTypeDef:
        """
        Delete an App Runner connection.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.delete_connection)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#delete_connection)
        """

    def delete_observability_configuration(
        self, *, ObservabilityConfigurationArn: str
    ) -> DeleteObservabilityConfigurationResponseTypeDef:
        """
        Delete an App Runner observability configuration resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.delete_observability_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#delete_observability_configuration)
        """

    def delete_service(self, *, ServiceArn: str) -> DeleteServiceResponseTypeDef:
        """
        Delete an App Runner service.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.delete_service)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#delete_service)
        """

    def delete_vpc_connector(self, *, VpcConnectorArn: str) -> DeleteVpcConnectorResponseTypeDef:
        """
        Delete an App Runner VPC connector resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.delete_vpc_connector)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#delete_vpc_connector)
        """

    def describe_auto_scaling_configuration(
        self, *, AutoScalingConfigurationArn: str
    ) -> DescribeAutoScalingConfigurationResponseTypeDef:
        """
        Return a full description of an App Runner automatic scaling configuration
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.describe_auto_scaling_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#describe_auto_scaling_configuration)
        """

    def describe_custom_domains(
        self, *, ServiceArn: str, NextToken: str = ..., MaxResults: int = ...
    ) -> DescribeCustomDomainsResponseTypeDef:
        """
        Return a description of custom domain names that are associated with an App
        Runner service.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.describe_custom_domains)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#describe_custom_domains)
        """

    def describe_observability_configuration(
        self, *, ObservabilityConfigurationArn: str
    ) -> DescribeObservabilityConfigurationResponseTypeDef:
        """
        Return a full description of an App Runner observability configuration resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.describe_observability_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#describe_observability_configuration)
        """

    def describe_service(self, *, ServiceArn: str) -> DescribeServiceResponseTypeDef:
        """
        Return a full description of an App Runner service.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.describe_service)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#describe_service)
        """

    def describe_vpc_connector(
        self, *, VpcConnectorArn: str
    ) -> DescribeVpcConnectorResponseTypeDef:
        """
        Return a description of an App Runner VPC connector resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.describe_vpc_connector)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#describe_vpc_connector)
        """

    def disassociate_custom_domain(
        self, *, ServiceArn: str, DomainName: str
    ) -> DisassociateCustomDomainResponseTypeDef:
        """
        Disassociate a custom domain name from an App Runner service.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.disassociate_custom_domain)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#disassociate_custom_domain)
        """

    def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: Mapping[str, Any] = ...,
        ExpiresIn: int = 3600,
        HttpMethod: str = ...,
    ) -> str:
        """
        Generate a presigned url given a client, its method, and arguments.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.generate_presigned_url)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#generate_presigned_url)
        """

    def list_auto_scaling_configurations(
        self,
        *,
        AutoScalingConfigurationName: str = ...,
        LatestOnly: bool = ...,
        MaxResults: int = ...,
        NextToken: str = ...
    ) -> ListAutoScalingConfigurationsResponseTypeDef:
        """
        Returns a list of active App Runner automatic scaling configurations in your
        Amazon Web Services account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.list_auto_scaling_configurations)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#list_auto_scaling_configurations)
        """

    def list_connections(
        self, *, ConnectionName: str = ..., MaxResults: int = ..., NextToken: str = ...
    ) -> ListConnectionsResponseTypeDef:
        """
        Returns a list of App Runner connections that are associated with your Amazon
        Web Services account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.list_connections)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#list_connections)
        """

    def list_observability_configurations(
        self,
        *,
        ObservabilityConfigurationName: str = ...,
        LatestOnly: bool = ...,
        MaxResults: int = ...,
        NextToken: str = ...
    ) -> ListObservabilityConfigurationsResponseTypeDef:
        """
        Returns a list of active App Runner observability configurations in your Amazon
        Web Services account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.list_observability_configurations)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#list_observability_configurations)
        """

    def list_operations(
        self, *, ServiceArn: str, NextToken: str = ..., MaxResults: int = ...
    ) -> ListOperationsResponseTypeDef:
        """
        Return a list of operations that occurred on an App Runner service.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.list_operations)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#list_operations)
        """

    def list_services(
        self, *, NextToken: str = ..., MaxResults: int = ...
    ) -> ListServicesResponseTypeDef:
        """
        Returns a list of running App Runner services in your Amazon Web Services
        account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.list_services)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#list_services)
        """

    def list_tags_for_resource(self, *, ResourceArn: str) -> ListTagsForResourceResponseTypeDef:
        """
        List tags that are associated with for an App Runner resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.list_tags_for_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#list_tags_for_resource)
        """

    def list_vpc_connectors(
        self, *, MaxResults: int = ..., NextToken: str = ...
    ) -> ListVpcConnectorsResponseTypeDef:
        """
        Returns a list of App Runner VPC connectors in your Amazon Web Services account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.list_vpc_connectors)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#list_vpc_connectors)
        """

    def pause_service(self, *, ServiceArn: str) -> PauseServiceResponseTypeDef:
        """
        Pause an active App Runner service.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.pause_service)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#pause_service)
        """

    def resume_service(self, *, ServiceArn: str) -> ResumeServiceResponseTypeDef:
        """
        Resume an active App Runner service.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.resume_service)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#resume_service)
        """

    def start_deployment(self, *, ServiceArn: str) -> StartDeploymentResponseTypeDef:
        """
        Initiate a manual deployment of the latest commit in a source code repository or
        the latest image in a source image repository to an App Runner service.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.start_deployment)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#start_deployment)
        """

    def tag_resource(self, *, ResourceArn: str, Tags: Sequence[TagTypeDef]) -> Dict[str, Any]:
        """
        Add tags to, or update the tag values of, an App Runner resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.tag_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#tag_resource)
        """

    def untag_resource(self, *, ResourceArn: str, TagKeys: Sequence[str]) -> Dict[str, Any]:
        """
        Remove tags from an App Runner resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.untag_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#untag_resource)
        """

    def update_service(
        self,
        *,
        ServiceArn: str,
        SourceConfiguration: SourceConfigurationTypeDef = ...,
        InstanceConfiguration: InstanceConfigurationTypeDef = ...,
        AutoScalingConfigurationArn: str = ...,
        HealthCheckConfiguration: HealthCheckConfigurationTypeDef = ...,
        NetworkConfiguration: NetworkConfigurationTypeDef = ...,
        ObservabilityConfiguration: ServiceObservabilityConfigurationTypeDef = ...
    ) -> UpdateServiceResponseTypeDef:
        """
        Update an App Runner service.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apprunner.html#AppRunner.Client.update_service)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/client/#update_service)
        """
