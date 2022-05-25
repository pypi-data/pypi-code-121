"""
Type annotations for apprunner service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_apprunner/type_defs/)

Usage::

    ```python
    from mypy_boto3_apprunner.type_defs import AssociateCustomDomainRequestRequestTypeDef

    data: AssociateCustomDomainRequestRequestTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence

from .literals import (
    AutoScalingConfigurationStatusType,
    CertificateValidationRecordStatusType,
    ConfigurationSourceType,
    ConnectionStatusType,
    CustomDomainAssociationStatusType,
    EgressTypeType,
    HealthCheckProtocolType,
    ImageRepositoryTypeType,
    ObservabilityConfigurationStatusType,
    OperationStatusType,
    OperationTypeType,
    RuntimeType,
    ServiceStatusType,
    VpcConnectorStatusType,
)

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal
if sys.version_info >= (3, 9):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


__all__ = (
    "AssociateCustomDomainRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "AuthenticationConfigurationTypeDef",
    "AutoScalingConfigurationSummaryTypeDef",
    "AutoScalingConfigurationTypeDef",
    "CertificateValidationRecordTypeDef",
    "CodeConfigurationValuesTypeDef",
    "SourceCodeVersionTypeDef",
    "ConnectionSummaryTypeDef",
    "ConnectionTypeDef",
    "TagTypeDef",
    "TraceConfigurationTypeDef",
    "EncryptionConfigurationTypeDef",
    "HealthCheckConfigurationTypeDef",
    "InstanceConfigurationTypeDef",
    "ServiceObservabilityConfigurationTypeDef",
    "VpcConnectorTypeDef",
    "DeleteAutoScalingConfigurationRequestRequestTypeDef",
    "DeleteConnectionRequestRequestTypeDef",
    "DeleteObservabilityConfigurationRequestRequestTypeDef",
    "DeleteServiceRequestRequestTypeDef",
    "DeleteVpcConnectorRequestRequestTypeDef",
    "DescribeAutoScalingConfigurationRequestRequestTypeDef",
    "DescribeCustomDomainsRequestRequestTypeDef",
    "DescribeObservabilityConfigurationRequestRequestTypeDef",
    "DescribeServiceRequestRequestTypeDef",
    "DescribeVpcConnectorRequestRequestTypeDef",
    "DisassociateCustomDomainRequestRequestTypeDef",
    "EgressConfigurationTypeDef",
    "ImageConfigurationTypeDef",
    "ListAutoScalingConfigurationsRequestRequestTypeDef",
    "ListConnectionsRequestRequestTypeDef",
    "ListObservabilityConfigurationsRequestRequestTypeDef",
    "ObservabilityConfigurationSummaryTypeDef",
    "ListOperationsRequestRequestTypeDef",
    "OperationSummaryTypeDef",
    "ListServicesRequestRequestTypeDef",
    "ServiceSummaryTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "ListVpcConnectorsRequestRequestTypeDef",
    "PauseServiceRequestRequestTypeDef",
    "ResumeServiceRequestRequestTypeDef",
    "StartDeploymentRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "StartDeploymentResponseTypeDef",
    "ListAutoScalingConfigurationsResponseTypeDef",
    "CreateAutoScalingConfigurationResponseTypeDef",
    "DeleteAutoScalingConfigurationResponseTypeDef",
    "DescribeAutoScalingConfigurationResponseTypeDef",
    "CustomDomainTypeDef",
    "CodeConfigurationTypeDef",
    "ListConnectionsResponseTypeDef",
    "CreateConnectionResponseTypeDef",
    "DeleteConnectionResponseTypeDef",
    "CreateAutoScalingConfigurationRequestRequestTypeDef",
    "CreateConnectionRequestRequestTypeDef",
    "CreateVpcConnectorRequestRequestTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "TagResourceRequestRequestTypeDef",
    "CreateObservabilityConfigurationRequestRequestTypeDef",
    "ObservabilityConfigurationTypeDef",
    "CreateVpcConnectorResponseTypeDef",
    "DeleteVpcConnectorResponseTypeDef",
    "DescribeVpcConnectorResponseTypeDef",
    "ListVpcConnectorsResponseTypeDef",
    "NetworkConfigurationTypeDef",
    "ImageRepositoryTypeDef",
    "ListObservabilityConfigurationsResponseTypeDef",
    "ListOperationsResponseTypeDef",
    "ListServicesResponseTypeDef",
    "AssociateCustomDomainResponseTypeDef",
    "DescribeCustomDomainsResponseTypeDef",
    "DisassociateCustomDomainResponseTypeDef",
    "CodeRepositoryTypeDef",
    "CreateObservabilityConfigurationResponseTypeDef",
    "DeleteObservabilityConfigurationResponseTypeDef",
    "DescribeObservabilityConfigurationResponseTypeDef",
    "SourceConfigurationTypeDef",
    "CreateServiceRequestRequestTypeDef",
    "ServiceTypeDef",
    "UpdateServiceRequestRequestTypeDef",
    "CreateServiceResponseTypeDef",
    "DeleteServiceResponseTypeDef",
    "DescribeServiceResponseTypeDef",
    "PauseServiceResponseTypeDef",
    "ResumeServiceResponseTypeDef",
    "UpdateServiceResponseTypeDef",
)

_RequiredAssociateCustomDomainRequestRequestTypeDef = TypedDict(
    "_RequiredAssociateCustomDomainRequestRequestTypeDef",
    {
        "ServiceArn": str,
        "DomainName": str,
    },
)
_OptionalAssociateCustomDomainRequestRequestTypeDef = TypedDict(
    "_OptionalAssociateCustomDomainRequestRequestTypeDef",
    {
        "EnableWWWSubdomain": bool,
    },
    total=False,
)


class AssociateCustomDomainRequestRequestTypeDef(
    _RequiredAssociateCustomDomainRequestRequestTypeDef,
    _OptionalAssociateCustomDomainRequestRequestTypeDef,
):
    pass


ResponseMetadataTypeDef = TypedDict(
    "ResponseMetadataTypeDef",
    {
        "RequestId": str,
        "HostId": str,
        "HTTPStatusCode": int,
        "HTTPHeaders": Dict[str, str],
        "RetryAttempts": int,
    },
)

AuthenticationConfigurationTypeDef = TypedDict(
    "AuthenticationConfigurationTypeDef",
    {
        "ConnectionArn": str,
        "AccessRoleArn": str,
    },
    total=False,
)

AutoScalingConfigurationSummaryTypeDef = TypedDict(
    "AutoScalingConfigurationSummaryTypeDef",
    {
        "AutoScalingConfigurationArn": str,
        "AutoScalingConfigurationName": str,
        "AutoScalingConfigurationRevision": int,
    },
    total=False,
)

AutoScalingConfigurationTypeDef = TypedDict(
    "AutoScalingConfigurationTypeDef",
    {
        "AutoScalingConfigurationArn": str,
        "AutoScalingConfigurationName": str,
        "AutoScalingConfigurationRevision": int,
        "Latest": bool,
        "Status": AutoScalingConfigurationStatusType,
        "MaxConcurrency": int,
        "MinSize": int,
        "MaxSize": int,
        "CreatedAt": datetime,
        "DeletedAt": datetime,
    },
    total=False,
)

CertificateValidationRecordTypeDef = TypedDict(
    "CertificateValidationRecordTypeDef",
    {
        "Name": str,
        "Type": str,
        "Value": str,
        "Status": CertificateValidationRecordStatusType,
    },
    total=False,
)

_RequiredCodeConfigurationValuesTypeDef = TypedDict(
    "_RequiredCodeConfigurationValuesTypeDef",
    {
        "Runtime": RuntimeType,
    },
)
_OptionalCodeConfigurationValuesTypeDef = TypedDict(
    "_OptionalCodeConfigurationValuesTypeDef",
    {
        "BuildCommand": str,
        "StartCommand": str,
        "Port": str,
        "RuntimeEnvironmentVariables": Mapping[str, str],
    },
    total=False,
)


class CodeConfigurationValuesTypeDef(
    _RequiredCodeConfigurationValuesTypeDef, _OptionalCodeConfigurationValuesTypeDef
):
    pass


SourceCodeVersionTypeDef = TypedDict(
    "SourceCodeVersionTypeDef",
    {
        "Type": Literal["BRANCH"],
        "Value": str,
    },
)

ConnectionSummaryTypeDef = TypedDict(
    "ConnectionSummaryTypeDef",
    {
        "ConnectionName": str,
        "ConnectionArn": str,
        "ProviderType": Literal["GITHUB"],
        "Status": ConnectionStatusType,
        "CreatedAt": datetime,
    },
    total=False,
)

ConnectionTypeDef = TypedDict(
    "ConnectionTypeDef",
    {
        "ConnectionName": str,
        "ConnectionArn": str,
        "ProviderType": Literal["GITHUB"],
        "Status": ConnectionStatusType,
        "CreatedAt": datetime,
    },
    total=False,
)

TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": str,
    },
    total=False,
)

TraceConfigurationTypeDef = TypedDict(
    "TraceConfigurationTypeDef",
    {
        "Vendor": Literal["AWSXRAY"],
    },
)

EncryptionConfigurationTypeDef = TypedDict(
    "EncryptionConfigurationTypeDef",
    {
        "KmsKey": str,
    },
)

HealthCheckConfigurationTypeDef = TypedDict(
    "HealthCheckConfigurationTypeDef",
    {
        "Protocol": HealthCheckProtocolType,
        "Path": str,
        "Interval": int,
        "Timeout": int,
        "HealthyThreshold": int,
        "UnhealthyThreshold": int,
    },
    total=False,
)

InstanceConfigurationTypeDef = TypedDict(
    "InstanceConfigurationTypeDef",
    {
        "Cpu": str,
        "Memory": str,
        "InstanceRoleArn": str,
    },
    total=False,
)

_RequiredServiceObservabilityConfigurationTypeDef = TypedDict(
    "_RequiredServiceObservabilityConfigurationTypeDef",
    {
        "ObservabilityEnabled": bool,
    },
)
_OptionalServiceObservabilityConfigurationTypeDef = TypedDict(
    "_OptionalServiceObservabilityConfigurationTypeDef",
    {
        "ObservabilityConfigurationArn": str,
    },
    total=False,
)


class ServiceObservabilityConfigurationTypeDef(
    _RequiredServiceObservabilityConfigurationTypeDef,
    _OptionalServiceObservabilityConfigurationTypeDef,
):
    pass


VpcConnectorTypeDef = TypedDict(
    "VpcConnectorTypeDef",
    {
        "VpcConnectorName": str,
        "VpcConnectorArn": str,
        "VpcConnectorRevision": int,
        "Subnets": List[str],
        "SecurityGroups": List[str],
        "Status": VpcConnectorStatusType,
        "CreatedAt": datetime,
        "DeletedAt": datetime,
    },
    total=False,
)

DeleteAutoScalingConfigurationRequestRequestTypeDef = TypedDict(
    "DeleteAutoScalingConfigurationRequestRequestTypeDef",
    {
        "AutoScalingConfigurationArn": str,
    },
)

DeleteConnectionRequestRequestTypeDef = TypedDict(
    "DeleteConnectionRequestRequestTypeDef",
    {
        "ConnectionArn": str,
    },
)

DeleteObservabilityConfigurationRequestRequestTypeDef = TypedDict(
    "DeleteObservabilityConfigurationRequestRequestTypeDef",
    {
        "ObservabilityConfigurationArn": str,
    },
)

DeleteServiceRequestRequestTypeDef = TypedDict(
    "DeleteServiceRequestRequestTypeDef",
    {
        "ServiceArn": str,
    },
)

DeleteVpcConnectorRequestRequestTypeDef = TypedDict(
    "DeleteVpcConnectorRequestRequestTypeDef",
    {
        "VpcConnectorArn": str,
    },
)

DescribeAutoScalingConfigurationRequestRequestTypeDef = TypedDict(
    "DescribeAutoScalingConfigurationRequestRequestTypeDef",
    {
        "AutoScalingConfigurationArn": str,
    },
)

_RequiredDescribeCustomDomainsRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeCustomDomainsRequestRequestTypeDef",
    {
        "ServiceArn": str,
    },
)
_OptionalDescribeCustomDomainsRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeCustomDomainsRequestRequestTypeDef",
    {
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)


class DescribeCustomDomainsRequestRequestTypeDef(
    _RequiredDescribeCustomDomainsRequestRequestTypeDef,
    _OptionalDescribeCustomDomainsRequestRequestTypeDef,
):
    pass


DescribeObservabilityConfigurationRequestRequestTypeDef = TypedDict(
    "DescribeObservabilityConfigurationRequestRequestTypeDef",
    {
        "ObservabilityConfigurationArn": str,
    },
)

DescribeServiceRequestRequestTypeDef = TypedDict(
    "DescribeServiceRequestRequestTypeDef",
    {
        "ServiceArn": str,
    },
)

DescribeVpcConnectorRequestRequestTypeDef = TypedDict(
    "DescribeVpcConnectorRequestRequestTypeDef",
    {
        "VpcConnectorArn": str,
    },
)

DisassociateCustomDomainRequestRequestTypeDef = TypedDict(
    "DisassociateCustomDomainRequestRequestTypeDef",
    {
        "ServiceArn": str,
        "DomainName": str,
    },
)

EgressConfigurationTypeDef = TypedDict(
    "EgressConfigurationTypeDef",
    {
        "EgressType": EgressTypeType,
        "VpcConnectorArn": str,
    },
    total=False,
)

ImageConfigurationTypeDef = TypedDict(
    "ImageConfigurationTypeDef",
    {
        "RuntimeEnvironmentVariables": Mapping[str, str],
        "StartCommand": str,
        "Port": str,
    },
    total=False,
)

ListAutoScalingConfigurationsRequestRequestTypeDef = TypedDict(
    "ListAutoScalingConfigurationsRequestRequestTypeDef",
    {
        "AutoScalingConfigurationName": str,
        "LatestOnly": bool,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

ListConnectionsRequestRequestTypeDef = TypedDict(
    "ListConnectionsRequestRequestTypeDef",
    {
        "ConnectionName": str,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

ListObservabilityConfigurationsRequestRequestTypeDef = TypedDict(
    "ListObservabilityConfigurationsRequestRequestTypeDef",
    {
        "ObservabilityConfigurationName": str,
        "LatestOnly": bool,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

ObservabilityConfigurationSummaryTypeDef = TypedDict(
    "ObservabilityConfigurationSummaryTypeDef",
    {
        "ObservabilityConfigurationArn": str,
        "ObservabilityConfigurationName": str,
        "ObservabilityConfigurationRevision": int,
    },
    total=False,
)

_RequiredListOperationsRequestRequestTypeDef = TypedDict(
    "_RequiredListOperationsRequestRequestTypeDef",
    {
        "ServiceArn": str,
    },
)
_OptionalListOperationsRequestRequestTypeDef = TypedDict(
    "_OptionalListOperationsRequestRequestTypeDef",
    {
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)


class ListOperationsRequestRequestTypeDef(
    _RequiredListOperationsRequestRequestTypeDef, _OptionalListOperationsRequestRequestTypeDef
):
    pass


OperationSummaryTypeDef = TypedDict(
    "OperationSummaryTypeDef",
    {
        "Id": str,
        "Type": OperationTypeType,
        "Status": OperationStatusType,
        "TargetArn": str,
        "StartedAt": datetime,
        "EndedAt": datetime,
        "UpdatedAt": datetime,
    },
    total=False,
)

ListServicesRequestRequestTypeDef = TypedDict(
    "ListServicesRequestRequestTypeDef",
    {
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

ServiceSummaryTypeDef = TypedDict(
    "ServiceSummaryTypeDef",
    {
        "ServiceName": str,
        "ServiceId": str,
        "ServiceArn": str,
        "ServiceUrl": str,
        "CreatedAt": datetime,
        "UpdatedAt": datetime,
        "Status": ServiceStatusType,
    },
    total=False,
)

ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
    },
)

ListVpcConnectorsRequestRequestTypeDef = TypedDict(
    "ListVpcConnectorsRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

PauseServiceRequestRequestTypeDef = TypedDict(
    "PauseServiceRequestRequestTypeDef",
    {
        "ServiceArn": str,
    },
)

ResumeServiceRequestRequestTypeDef = TypedDict(
    "ResumeServiceRequestRequestTypeDef",
    {
        "ServiceArn": str,
    },
)

StartDeploymentRequestRequestTypeDef = TypedDict(
    "StartDeploymentRequestRequestTypeDef",
    {
        "ServiceArn": str,
    },
)

UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "TagKeys": Sequence[str],
    },
)

StartDeploymentResponseTypeDef = TypedDict(
    "StartDeploymentResponseTypeDef",
    {
        "OperationId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListAutoScalingConfigurationsResponseTypeDef = TypedDict(
    "ListAutoScalingConfigurationsResponseTypeDef",
    {
        "AutoScalingConfigurationSummaryList": List[AutoScalingConfigurationSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateAutoScalingConfigurationResponseTypeDef = TypedDict(
    "CreateAutoScalingConfigurationResponseTypeDef",
    {
        "AutoScalingConfiguration": AutoScalingConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteAutoScalingConfigurationResponseTypeDef = TypedDict(
    "DeleteAutoScalingConfigurationResponseTypeDef",
    {
        "AutoScalingConfiguration": AutoScalingConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeAutoScalingConfigurationResponseTypeDef = TypedDict(
    "DescribeAutoScalingConfigurationResponseTypeDef",
    {
        "AutoScalingConfiguration": AutoScalingConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredCustomDomainTypeDef = TypedDict(
    "_RequiredCustomDomainTypeDef",
    {
        "DomainName": str,
        "EnableWWWSubdomain": bool,
        "Status": CustomDomainAssociationStatusType,
    },
)
_OptionalCustomDomainTypeDef = TypedDict(
    "_OptionalCustomDomainTypeDef",
    {
        "CertificateValidationRecords": List[CertificateValidationRecordTypeDef],
    },
    total=False,
)


class CustomDomainTypeDef(_RequiredCustomDomainTypeDef, _OptionalCustomDomainTypeDef):
    pass


_RequiredCodeConfigurationTypeDef = TypedDict(
    "_RequiredCodeConfigurationTypeDef",
    {
        "ConfigurationSource": ConfigurationSourceType,
    },
)
_OptionalCodeConfigurationTypeDef = TypedDict(
    "_OptionalCodeConfigurationTypeDef",
    {
        "CodeConfigurationValues": CodeConfigurationValuesTypeDef,
    },
    total=False,
)


class CodeConfigurationTypeDef(
    _RequiredCodeConfigurationTypeDef, _OptionalCodeConfigurationTypeDef
):
    pass


ListConnectionsResponseTypeDef = TypedDict(
    "ListConnectionsResponseTypeDef",
    {
        "ConnectionSummaryList": List[ConnectionSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateConnectionResponseTypeDef = TypedDict(
    "CreateConnectionResponseTypeDef",
    {
        "Connection": ConnectionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteConnectionResponseTypeDef = TypedDict(
    "DeleteConnectionResponseTypeDef",
    {
        "Connection": ConnectionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredCreateAutoScalingConfigurationRequestRequestTypeDef = TypedDict(
    "_RequiredCreateAutoScalingConfigurationRequestRequestTypeDef",
    {
        "AutoScalingConfigurationName": str,
    },
)
_OptionalCreateAutoScalingConfigurationRequestRequestTypeDef = TypedDict(
    "_OptionalCreateAutoScalingConfigurationRequestRequestTypeDef",
    {
        "MaxConcurrency": int,
        "MinSize": int,
        "MaxSize": int,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateAutoScalingConfigurationRequestRequestTypeDef(
    _RequiredCreateAutoScalingConfigurationRequestRequestTypeDef,
    _OptionalCreateAutoScalingConfigurationRequestRequestTypeDef,
):
    pass


_RequiredCreateConnectionRequestRequestTypeDef = TypedDict(
    "_RequiredCreateConnectionRequestRequestTypeDef",
    {
        "ConnectionName": str,
        "ProviderType": Literal["GITHUB"],
    },
)
_OptionalCreateConnectionRequestRequestTypeDef = TypedDict(
    "_OptionalCreateConnectionRequestRequestTypeDef",
    {
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateConnectionRequestRequestTypeDef(
    _RequiredCreateConnectionRequestRequestTypeDef, _OptionalCreateConnectionRequestRequestTypeDef
):
    pass


_RequiredCreateVpcConnectorRequestRequestTypeDef = TypedDict(
    "_RequiredCreateVpcConnectorRequestRequestTypeDef",
    {
        "VpcConnectorName": str,
        "Subnets": Sequence[str],
    },
)
_OptionalCreateVpcConnectorRequestRequestTypeDef = TypedDict(
    "_OptionalCreateVpcConnectorRequestRequestTypeDef",
    {
        "SecurityGroups": Sequence[str],
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateVpcConnectorRequestRequestTypeDef(
    _RequiredCreateVpcConnectorRequestRequestTypeDef,
    _OptionalCreateVpcConnectorRequestRequestTypeDef,
):
    pass


ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "Tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "Tags": Sequence[TagTypeDef],
    },
)

_RequiredCreateObservabilityConfigurationRequestRequestTypeDef = TypedDict(
    "_RequiredCreateObservabilityConfigurationRequestRequestTypeDef",
    {
        "ObservabilityConfigurationName": str,
    },
)
_OptionalCreateObservabilityConfigurationRequestRequestTypeDef = TypedDict(
    "_OptionalCreateObservabilityConfigurationRequestRequestTypeDef",
    {
        "TraceConfiguration": TraceConfigurationTypeDef,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateObservabilityConfigurationRequestRequestTypeDef(
    _RequiredCreateObservabilityConfigurationRequestRequestTypeDef,
    _OptionalCreateObservabilityConfigurationRequestRequestTypeDef,
):
    pass


ObservabilityConfigurationTypeDef = TypedDict(
    "ObservabilityConfigurationTypeDef",
    {
        "ObservabilityConfigurationArn": str,
        "ObservabilityConfigurationName": str,
        "TraceConfiguration": TraceConfigurationTypeDef,
        "ObservabilityConfigurationRevision": int,
        "Latest": bool,
        "Status": ObservabilityConfigurationStatusType,
        "CreatedAt": datetime,
        "DeletedAt": datetime,
    },
    total=False,
)

CreateVpcConnectorResponseTypeDef = TypedDict(
    "CreateVpcConnectorResponseTypeDef",
    {
        "VpcConnector": VpcConnectorTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteVpcConnectorResponseTypeDef = TypedDict(
    "DeleteVpcConnectorResponseTypeDef",
    {
        "VpcConnector": VpcConnectorTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeVpcConnectorResponseTypeDef = TypedDict(
    "DescribeVpcConnectorResponseTypeDef",
    {
        "VpcConnector": VpcConnectorTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListVpcConnectorsResponseTypeDef = TypedDict(
    "ListVpcConnectorsResponseTypeDef",
    {
        "VpcConnectors": List[VpcConnectorTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

NetworkConfigurationTypeDef = TypedDict(
    "NetworkConfigurationTypeDef",
    {
        "EgressConfiguration": EgressConfigurationTypeDef,
    },
    total=False,
)

_RequiredImageRepositoryTypeDef = TypedDict(
    "_RequiredImageRepositoryTypeDef",
    {
        "ImageIdentifier": str,
        "ImageRepositoryType": ImageRepositoryTypeType,
    },
)
_OptionalImageRepositoryTypeDef = TypedDict(
    "_OptionalImageRepositoryTypeDef",
    {
        "ImageConfiguration": ImageConfigurationTypeDef,
    },
    total=False,
)


class ImageRepositoryTypeDef(_RequiredImageRepositoryTypeDef, _OptionalImageRepositoryTypeDef):
    pass


ListObservabilityConfigurationsResponseTypeDef = TypedDict(
    "ListObservabilityConfigurationsResponseTypeDef",
    {
        "ObservabilityConfigurationSummaryList": List[ObservabilityConfigurationSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListOperationsResponseTypeDef = TypedDict(
    "ListOperationsResponseTypeDef",
    {
        "OperationSummaryList": List[OperationSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListServicesResponseTypeDef = TypedDict(
    "ListServicesResponseTypeDef",
    {
        "ServiceSummaryList": List[ServiceSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AssociateCustomDomainResponseTypeDef = TypedDict(
    "AssociateCustomDomainResponseTypeDef",
    {
        "DNSTarget": str,
        "ServiceArn": str,
        "CustomDomain": CustomDomainTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeCustomDomainsResponseTypeDef = TypedDict(
    "DescribeCustomDomainsResponseTypeDef",
    {
        "DNSTarget": str,
        "ServiceArn": str,
        "CustomDomains": List[CustomDomainTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisassociateCustomDomainResponseTypeDef = TypedDict(
    "DisassociateCustomDomainResponseTypeDef",
    {
        "DNSTarget": str,
        "ServiceArn": str,
        "CustomDomain": CustomDomainTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredCodeRepositoryTypeDef = TypedDict(
    "_RequiredCodeRepositoryTypeDef",
    {
        "RepositoryUrl": str,
        "SourceCodeVersion": SourceCodeVersionTypeDef,
    },
)
_OptionalCodeRepositoryTypeDef = TypedDict(
    "_OptionalCodeRepositoryTypeDef",
    {
        "CodeConfiguration": CodeConfigurationTypeDef,
    },
    total=False,
)


class CodeRepositoryTypeDef(_RequiredCodeRepositoryTypeDef, _OptionalCodeRepositoryTypeDef):
    pass


CreateObservabilityConfigurationResponseTypeDef = TypedDict(
    "CreateObservabilityConfigurationResponseTypeDef",
    {
        "ObservabilityConfiguration": ObservabilityConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteObservabilityConfigurationResponseTypeDef = TypedDict(
    "DeleteObservabilityConfigurationResponseTypeDef",
    {
        "ObservabilityConfiguration": ObservabilityConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeObservabilityConfigurationResponseTypeDef = TypedDict(
    "DescribeObservabilityConfigurationResponseTypeDef",
    {
        "ObservabilityConfiguration": ObservabilityConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SourceConfigurationTypeDef = TypedDict(
    "SourceConfigurationTypeDef",
    {
        "CodeRepository": CodeRepositoryTypeDef,
        "ImageRepository": ImageRepositoryTypeDef,
        "AutoDeploymentsEnabled": bool,
        "AuthenticationConfiguration": AuthenticationConfigurationTypeDef,
    },
    total=False,
)

_RequiredCreateServiceRequestRequestTypeDef = TypedDict(
    "_RequiredCreateServiceRequestRequestTypeDef",
    {
        "ServiceName": str,
        "SourceConfiguration": SourceConfigurationTypeDef,
    },
)
_OptionalCreateServiceRequestRequestTypeDef = TypedDict(
    "_OptionalCreateServiceRequestRequestTypeDef",
    {
        "InstanceConfiguration": InstanceConfigurationTypeDef,
        "Tags": Sequence[TagTypeDef],
        "EncryptionConfiguration": EncryptionConfigurationTypeDef,
        "HealthCheckConfiguration": HealthCheckConfigurationTypeDef,
        "AutoScalingConfigurationArn": str,
        "NetworkConfiguration": NetworkConfigurationTypeDef,
        "ObservabilityConfiguration": ServiceObservabilityConfigurationTypeDef,
    },
    total=False,
)


class CreateServiceRequestRequestTypeDef(
    _RequiredCreateServiceRequestRequestTypeDef, _OptionalCreateServiceRequestRequestTypeDef
):
    pass


_RequiredServiceTypeDef = TypedDict(
    "_RequiredServiceTypeDef",
    {
        "ServiceName": str,
        "ServiceId": str,
        "ServiceArn": str,
        "ServiceUrl": str,
        "CreatedAt": datetime,
        "UpdatedAt": datetime,
        "Status": ServiceStatusType,
        "SourceConfiguration": SourceConfigurationTypeDef,
        "InstanceConfiguration": InstanceConfigurationTypeDef,
        "AutoScalingConfigurationSummary": AutoScalingConfigurationSummaryTypeDef,
        "NetworkConfiguration": NetworkConfigurationTypeDef,
    },
)
_OptionalServiceTypeDef = TypedDict(
    "_OptionalServiceTypeDef",
    {
        "DeletedAt": datetime,
        "EncryptionConfiguration": EncryptionConfigurationTypeDef,
        "HealthCheckConfiguration": HealthCheckConfigurationTypeDef,
        "ObservabilityConfiguration": ServiceObservabilityConfigurationTypeDef,
    },
    total=False,
)


class ServiceTypeDef(_RequiredServiceTypeDef, _OptionalServiceTypeDef):
    pass


_RequiredUpdateServiceRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateServiceRequestRequestTypeDef",
    {
        "ServiceArn": str,
    },
)
_OptionalUpdateServiceRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateServiceRequestRequestTypeDef",
    {
        "SourceConfiguration": SourceConfigurationTypeDef,
        "InstanceConfiguration": InstanceConfigurationTypeDef,
        "AutoScalingConfigurationArn": str,
        "HealthCheckConfiguration": HealthCheckConfigurationTypeDef,
        "NetworkConfiguration": NetworkConfigurationTypeDef,
        "ObservabilityConfiguration": ServiceObservabilityConfigurationTypeDef,
    },
    total=False,
)


class UpdateServiceRequestRequestTypeDef(
    _RequiredUpdateServiceRequestRequestTypeDef, _OptionalUpdateServiceRequestRequestTypeDef
):
    pass


CreateServiceResponseTypeDef = TypedDict(
    "CreateServiceResponseTypeDef",
    {
        "Service": ServiceTypeDef,
        "OperationId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteServiceResponseTypeDef = TypedDict(
    "DeleteServiceResponseTypeDef",
    {
        "Service": ServiceTypeDef,
        "OperationId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeServiceResponseTypeDef = TypedDict(
    "DescribeServiceResponseTypeDef",
    {
        "Service": ServiceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PauseServiceResponseTypeDef = TypedDict(
    "PauseServiceResponseTypeDef",
    {
        "Service": ServiceTypeDef,
        "OperationId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ResumeServiceResponseTypeDef = TypedDict(
    "ResumeServiceResponseTypeDef",
    {
        "Service": ServiceTypeDef,
        "OperationId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateServiceResponseTypeDef = TypedDict(
    "UpdateServiceResponseTypeDef",
    {
        "Service": ServiceTypeDef,
        "OperationId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
