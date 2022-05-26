"""
Type annotations for lightsail service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lightsail/type_defs/)

Usage::

    ```python
    from mypy_boto3_lightsail.type_defs import AccessKeyLastUsedTypeDef

    data: AccessKeyLastUsedTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence, Union

from .literals import (
    AccessDirectionType,
    AccessTypeType,
    AccountLevelBpaSyncStatusType,
    AlarmStateType,
    AutoSnapshotStatusType,
    BehaviorEnumType,
    BlueprintTypeType,
    BPAStatusMessageType,
    BucketMetricNameType,
    CertificateStatusType,
    ComparisonOperatorType,
    ContactMethodStatusType,
    ContactProtocolType,
    ContainerServiceDeploymentStateType,
    ContainerServiceMetricNameType,
    ContainerServicePowerNameType,
    ContainerServiceProtocolType,
    ContainerServiceStateDetailCodeType,
    ContainerServiceStateType,
    DiskSnapshotStateType,
    DiskStateType,
    DistributionMetricNameType,
    ExportSnapshotRecordSourceTypeType,
    ForwardValuesType,
    HeaderEnumType,
    InstanceAccessProtocolType,
    InstanceHealthReasonType,
    InstanceHealthStateType,
    InstanceMetricNameType,
    InstancePlatformType,
    InstanceSnapshotStateType,
    IpAddressTypeType,
    LoadBalancerAttributeNameType,
    LoadBalancerMetricNameType,
    LoadBalancerProtocolType,
    LoadBalancerStateType,
    LoadBalancerTlsCertificateDomainStatusType,
    LoadBalancerTlsCertificateFailureReasonType,
    LoadBalancerTlsCertificateRenewalStatusType,
    LoadBalancerTlsCertificateRevocationReasonType,
    LoadBalancerTlsCertificateStatusType,
    MetricNameType,
    MetricStatisticType,
    MetricUnitType,
    NetworkProtocolType,
    OperationStatusType,
    OperationTypeType,
    OriginProtocolPolicyEnumType,
    PortAccessTypeType,
    PortInfoSourceTypeType,
    PortStateType,
    RecordStateType,
    RegionNameType,
    RelationalDatabaseMetricNameType,
    RelationalDatabasePasswordVersionType,
    RenewalStatusType,
    ResourceBucketAccessType,
    ResourceTypeType,
    StatusTypeType,
    TreatMissingDataType,
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
    "AccessKeyLastUsedTypeDef",
    "AccessRulesTypeDef",
    "AccountLevelBpaSyncTypeDef",
    "AutoSnapshotAddOnRequestTypeDef",
    "AddOnTypeDef",
    "MonitoredResourceInfoTypeDef",
    "ResourceLocationTypeDef",
    "AllocateStaticIpRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "AttachCertificateToDistributionRequestRequestTypeDef",
    "AttachDiskRequestRequestTypeDef",
    "AttachInstancesToLoadBalancerRequestRequestTypeDef",
    "AttachLoadBalancerTlsCertificateRequestRequestTypeDef",
    "AttachStaticIpRequestRequestTypeDef",
    "AttachedDiskTypeDef",
    "AvailabilityZoneTypeDef",
    "BlueprintTypeDef",
    "BucketAccessLogConfigTypeDef",
    "BucketBundleTypeDef",
    "BucketStateTypeDef",
    "ResourceReceivingAccessTypeDef",
    "TagTypeDef",
    "BundleTypeDef",
    "CacheBehaviorPerPathTypeDef",
    "CacheBehaviorTypeDef",
    "CookieObjectTypeDef",
    "HeaderObjectTypeDef",
    "QueryStringObjectTypeDef",
    "PortInfoTypeDef",
    "CloudFormationStackRecordSourceInfoTypeDef",
    "DestinationInfoTypeDef",
    "ContainerImageTypeDef",
    "ContainerTypeDef",
    "ContainerServiceECRImagePullerRoleRequestTypeDef",
    "ContainerServiceECRImagePullerRoleTypeDef",
    "ContainerServiceHealthCheckConfigTypeDef",
    "ContainerServiceLogEventTypeDef",
    "ContainerServicePowerTypeDef",
    "ContainerServiceRegistryLoginTypeDef",
    "ContainerServiceStateDetailTypeDef",
    "CopySnapshotRequestRequestTypeDef",
    "CreateBucketAccessKeyRequestRequestTypeDef",
    "InstanceEntryTypeDef",
    "CreateContactMethodRequestRequestTypeDef",
    "InputOriginTypeDef",
    "DomainEntryTypeDef",
    "DiskMapTypeDef",
    "DeleteAlarmRequestRequestTypeDef",
    "DeleteAutoSnapshotRequestRequestTypeDef",
    "DeleteBucketAccessKeyRequestRequestTypeDef",
    "DeleteBucketRequestRequestTypeDef",
    "DeleteCertificateRequestRequestTypeDef",
    "DeleteContactMethodRequestRequestTypeDef",
    "DeleteContainerImageRequestRequestTypeDef",
    "DeleteContainerServiceRequestRequestTypeDef",
    "DeleteDiskRequestRequestTypeDef",
    "DeleteDiskSnapshotRequestRequestTypeDef",
    "DeleteDistributionRequestRequestTypeDef",
    "DeleteDomainRequestRequestTypeDef",
    "DeleteInstanceRequestRequestTypeDef",
    "DeleteInstanceSnapshotRequestRequestTypeDef",
    "DeleteKeyPairRequestRequestTypeDef",
    "DeleteKnownHostKeysRequestRequestTypeDef",
    "DeleteLoadBalancerRequestRequestTypeDef",
    "DeleteLoadBalancerTlsCertificateRequestRequestTypeDef",
    "DeleteRelationalDatabaseRequestRequestTypeDef",
    "DeleteRelationalDatabaseSnapshotRequestRequestTypeDef",
    "DetachCertificateFromDistributionRequestRequestTypeDef",
    "DetachDiskRequestRequestTypeDef",
    "DetachInstancesFromLoadBalancerRequestRequestTypeDef",
    "DetachStaticIpRequestRequestTypeDef",
    "DisableAddOnRequestRequestTypeDef",
    "DiskInfoTypeDef",
    "DiskSnapshotInfoTypeDef",
    "DistributionBundleTypeDef",
    "ResourceRecordTypeDef",
    "ExportSnapshotRequestRequestTypeDef",
    "PaginatorConfigTypeDef",
    "GetActiveNamesRequestRequestTypeDef",
    "GetAlarmsRequestRequestTypeDef",
    "GetAutoSnapshotsRequestRequestTypeDef",
    "GetBlueprintsRequestRequestTypeDef",
    "GetBucketAccessKeysRequestRequestTypeDef",
    "GetBucketBundlesRequestRequestTypeDef",
    "GetBucketMetricDataRequestRequestTypeDef",
    "MetricDatapointTypeDef",
    "GetBucketsRequestRequestTypeDef",
    "GetBundlesRequestRequestTypeDef",
    "GetCertificatesRequestRequestTypeDef",
    "GetCloudFormationStackRecordsRequestRequestTypeDef",
    "GetContactMethodsRequestRequestTypeDef",
    "GetContainerImagesRequestRequestTypeDef",
    "GetContainerLogRequestRequestTypeDef",
    "GetContainerServiceDeploymentsRequestRequestTypeDef",
    "GetContainerServiceMetricDataRequestRequestTypeDef",
    "GetContainerServicesRequestRequestTypeDef",
    "GetDiskRequestRequestTypeDef",
    "GetDiskSnapshotRequestRequestTypeDef",
    "GetDiskSnapshotsRequestRequestTypeDef",
    "GetDisksRequestRequestTypeDef",
    "GetDistributionLatestCacheResetRequestRequestTypeDef",
    "GetDistributionMetricDataRequestRequestTypeDef",
    "GetDistributionsRequestRequestTypeDef",
    "GetDomainRequestRequestTypeDef",
    "GetDomainsRequestRequestTypeDef",
    "GetExportSnapshotRecordsRequestRequestTypeDef",
    "GetInstanceAccessDetailsRequestRequestTypeDef",
    "GetInstanceMetricDataRequestRequestTypeDef",
    "GetInstancePortStatesRequestRequestTypeDef",
    "InstancePortStateTypeDef",
    "GetInstanceRequestRequestTypeDef",
    "GetInstanceSnapshotRequestRequestTypeDef",
    "GetInstanceSnapshotsRequestRequestTypeDef",
    "GetInstanceStateRequestRequestTypeDef",
    "InstanceStateTypeDef",
    "GetInstancesRequestRequestTypeDef",
    "GetKeyPairRequestRequestTypeDef",
    "GetKeyPairsRequestRequestTypeDef",
    "GetLoadBalancerMetricDataRequestRequestTypeDef",
    "GetLoadBalancerRequestRequestTypeDef",
    "GetLoadBalancerTlsCertificatesRequestRequestTypeDef",
    "GetLoadBalancerTlsPoliciesRequestRequestTypeDef",
    "LoadBalancerTlsPolicyTypeDef",
    "GetLoadBalancersRequestRequestTypeDef",
    "GetOperationRequestRequestTypeDef",
    "GetOperationsForResourceRequestRequestTypeDef",
    "GetOperationsRequestRequestTypeDef",
    "GetRegionsRequestRequestTypeDef",
    "GetRelationalDatabaseBlueprintsRequestRequestTypeDef",
    "RelationalDatabaseBlueprintTypeDef",
    "GetRelationalDatabaseBundlesRequestRequestTypeDef",
    "RelationalDatabaseBundleTypeDef",
    "GetRelationalDatabaseEventsRequestRequestTypeDef",
    "RelationalDatabaseEventTypeDef",
    "GetRelationalDatabaseLogEventsRequestRequestTypeDef",
    "LogEventTypeDef",
    "GetRelationalDatabaseLogStreamsRequestRequestTypeDef",
    "GetRelationalDatabaseMasterUserPasswordRequestRequestTypeDef",
    "GetRelationalDatabaseMetricDataRequestRequestTypeDef",
    "GetRelationalDatabaseParametersRequestRequestTypeDef",
    "RelationalDatabaseParameterTypeDef",
    "GetRelationalDatabaseRequestRequestTypeDef",
    "GetRelationalDatabaseSnapshotRequestRequestTypeDef",
    "GetRelationalDatabaseSnapshotsRequestRequestTypeDef",
    "GetRelationalDatabasesRequestRequestTypeDef",
    "GetStaticIpRequestRequestTypeDef",
    "GetStaticIpsRequestRequestTypeDef",
    "HostKeyAttributesTypeDef",
    "ImportKeyPairRequestRequestTypeDef",
    "PasswordDataTypeDef",
    "InstanceHealthSummaryTypeDef",
    "InstancePortInfoTypeDef",
    "MonthlyTransferTypeDef",
    "OriginTypeDef",
    "LoadBalancerTlsCertificateDomainValidationOptionTypeDef",
    "LoadBalancerTlsCertificateDomainValidationRecordTypeDef",
    "LoadBalancerTlsCertificateSummaryTypeDef",
    "PendingMaintenanceActionTypeDef",
    "PendingModifiedRelationalDatabaseValuesTypeDef",
    "PutAlarmRequestRequestTypeDef",
    "RebootInstanceRequestRequestTypeDef",
    "RebootRelationalDatabaseRequestRequestTypeDef",
    "RegisterContainerImageRequestRequestTypeDef",
    "RelationalDatabaseEndpointTypeDef",
    "RelationalDatabaseHardwareTypeDef",
    "ReleaseStaticIpRequestRequestTypeDef",
    "ResetDistributionCacheRequestRequestTypeDef",
    "SendContactMethodVerificationRequestRequestTypeDef",
    "SetIpAddressTypeRequestRequestTypeDef",
    "SetResourceAccessForBucketRequestRequestTypeDef",
    "StartInstanceRequestRequestTypeDef",
    "StartRelationalDatabaseRequestRequestTypeDef",
    "StopInstanceRequestRequestTypeDef",
    "StopRelationalDatabaseRequestRequestTypeDef",
    "TestAlarmRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateBucketBundleRequestRequestTypeDef",
    "UpdateDistributionBundleRequestRequestTypeDef",
    "UpdateLoadBalancerAttributeRequestRequestTypeDef",
    "UpdateRelationalDatabaseRequestRequestTypeDef",
    "AccessKeyTypeDef",
    "AddOnRequestTypeDef",
    "AlarmTypeDef",
    "ContactMethodTypeDef",
    "OperationTypeDef",
    "StaticIpTypeDef",
    "DownloadDefaultKeyPairResultTypeDef",
    "GetActiveNamesResultTypeDef",
    "GetContainerAPIMetadataResultTypeDef",
    "GetDistributionLatestCacheResetResultTypeDef",
    "GetRelationalDatabaseLogStreamsResultTypeDef",
    "GetRelationalDatabaseMasterUserPasswordResultTypeDef",
    "IsVpcPeeredResultTypeDef",
    "AutoSnapshotDetailsTypeDef",
    "RegionTypeDef",
    "GetBlueprintsResultTypeDef",
    "UpdateBucketRequestRequestTypeDef",
    "GetBucketBundlesResultTypeDef",
    "BucketTypeDef",
    "CreateBucketRequestRequestTypeDef",
    "CreateCertificateRequestRequestTypeDef",
    "CreateDiskSnapshotRequestRequestTypeDef",
    "CreateDomainRequestRequestTypeDef",
    "CreateInstanceSnapshotRequestRequestTypeDef",
    "CreateKeyPairRequestRequestTypeDef",
    "CreateLoadBalancerRequestRequestTypeDef",
    "CreateLoadBalancerTlsCertificateRequestRequestTypeDef",
    "CreateRelationalDatabaseFromSnapshotRequestRequestTypeDef",
    "CreateRelationalDatabaseRequestRequestTypeDef",
    "CreateRelationalDatabaseSnapshotRequestRequestTypeDef",
    "DiskSnapshotTypeDef",
    "DiskTypeDef",
    "KeyPairTypeDef",
    "RelationalDatabaseSnapshotTypeDef",
    "TagResourceRequestRequestTypeDef",
    "GetBundlesResultTypeDef",
    "CacheSettingsTypeDef",
    "CloseInstancePublicPortsRequestRequestTypeDef",
    "OpenInstancePublicPortsRequestRequestTypeDef",
    "PutInstancePublicPortsRequestRequestTypeDef",
    "CloudFormationStackRecordTypeDef",
    "GetContainerImagesResultTypeDef",
    "RegisterContainerImageResultTypeDef",
    "PrivateRegistryAccessRequestTypeDef",
    "PrivateRegistryAccessTypeDef",
    "ContainerServiceEndpointTypeDef",
    "EndpointRequestTypeDef",
    "GetContainerLogResultTypeDef",
    "GetContainerServicePowersResultTypeDef",
    "CreateContainerServiceRegistryLoginResultTypeDef",
    "CreateCloudFormationStackRequestRequestTypeDef",
    "CreateDomainEntryRequestRequestTypeDef",
    "DeleteDomainEntryRequestRequestTypeDef",
    "DomainTypeDef",
    "UpdateDomainEntryRequestRequestTypeDef",
    "InstanceSnapshotInfoTypeDef",
    "GetDistributionBundlesResultTypeDef",
    "DomainValidationRecordTypeDef",
    "GetActiveNamesRequestGetActiveNamesPaginateTypeDef",
    "GetBlueprintsRequestGetBlueprintsPaginateTypeDef",
    "GetBundlesRequestGetBundlesPaginateTypeDef",
    "GetCloudFormationStackRecordsRequestGetCloudFormationStackRecordsPaginateTypeDef",
    "GetDiskSnapshotsRequestGetDiskSnapshotsPaginateTypeDef",
    "GetDisksRequestGetDisksPaginateTypeDef",
    "GetDomainsRequestGetDomainsPaginateTypeDef",
    "GetExportSnapshotRecordsRequestGetExportSnapshotRecordsPaginateTypeDef",
    "GetInstanceSnapshotsRequestGetInstanceSnapshotsPaginateTypeDef",
    "GetInstancesRequestGetInstancesPaginateTypeDef",
    "GetKeyPairsRequestGetKeyPairsPaginateTypeDef",
    "GetLoadBalancersRequestGetLoadBalancersPaginateTypeDef",
    "GetOperationsRequestGetOperationsPaginateTypeDef",
    "GetRelationalDatabaseBlueprintsRequestGetRelationalDatabaseBlueprintsPaginateTypeDef",
    "GetRelationalDatabaseBundlesRequestGetRelationalDatabaseBundlesPaginateTypeDef",
    "GetRelationalDatabaseEventsRequestGetRelationalDatabaseEventsPaginateTypeDef",
    "GetRelationalDatabaseParametersRequestGetRelationalDatabaseParametersPaginateTypeDef",
    "GetRelationalDatabaseSnapshotsRequestGetRelationalDatabaseSnapshotsPaginateTypeDef",
    "GetRelationalDatabasesRequestGetRelationalDatabasesPaginateTypeDef",
    "GetStaticIpsRequestGetStaticIpsPaginateTypeDef",
    "GetBucketMetricDataResultTypeDef",
    "GetContainerServiceMetricDataResultTypeDef",
    "GetDistributionMetricDataResultTypeDef",
    "GetInstanceMetricDataResultTypeDef",
    "GetLoadBalancerMetricDataResultTypeDef",
    "GetRelationalDatabaseMetricDataResultTypeDef",
    "GetInstancePortStatesResultTypeDef",
    "GetInstanceStateResultTypeDef",
    "GetLoadBalancerTlsPoliciesResultTypeDef",
    "GetRelationalDatabaseBlueprintsResultTypeDef",
    "GetRelationalDatabaseBundlesResultTypeDef",
    "GetRelationalDatabaseEventsResultTypeDef",
    "GetRelationalDatabaseLogEventsResultTypeDef",
    "GetRelationalDatabaseParametersResultTypeDef",
    "UpdateRelationalDatabaseParametersRequestRequestTypeDef",
    "InstanceAccessDetailsTypeDef",
    "InstanceNetworkingTypeDef",
    "LoadBalancerTlsCertificateRenewalSummaryTypeDef",
    "LoadBalancerTypeDef",
    "RelationalDatabaseTypeDef",
    "GetBucketAccessKeysResultTypeDef",
    "CreateDiskFromSnapshotRequestRequestTypeDef",
    "CreateDiskRequestRequestTypeDef",
    "CreateInstancesFromSnapshotRequestRequestTypeDef",
    "CreateInstancesRequestRequestTypeDef",
    "EnableAddOnRequestRequestTypeDef",
    "GetAlarmsResultTypeDef",
    "GetContactMethodsResultTypeDef",
    "AllocateStaticIpResultTypeDef",
    "AttachCertificateToDistributionResultTypeDef",
    "AttachDiskResultTypeDef",
    "AttachInstancesToLoadBalancerResultTypeDef",
    "AttachLoadBalancerTlsCertificateResultTypeDef",
    "AttachStaticIpResultTypeDef",
    "CloseInstancePublicPortsResultTypeDef",
    "CopySnapshotResultTypeDef",
    "CreateBucketAccessKeyResultTypeDef",
    "CreateCloudFormationStackResultTypeDef",
    "CreateContactMethodResultTypeDef",
    "CreateDiskFromSnapshotResultTypeDef",
    "CreateDiskResultTypeDef",
    "CreateDiskSnapshotResultTypeDef",
    "CreateDomainEntryResultTypeDef",
    "CreateDomainResultTypeDef",
    "CreateInstanceSnapshotResultTypeDef",
    "CreateInstancesFromSnapshotResultTypeDef",
    "CreateInstancesResultTypeDef",
    "CreateLoadBalancerResultTypeDef",
    "CreateLoadBalancerTlsCertificateResultTypeDef",
    "CreateRelationalDatabaseFromSnapshotResultTypeDef",
    "CreateRelationalDatabaseResultTypeDef",
    "CreateRelationalDatabaseSnapshotResultTypeDef",
    "DeleteAlarmResultTypeDef",
    "DeleteAutoSnapshotResultTypeDef",
    "DeleteBucketAccessKeyResultTypeDef",
    "DeleteBucketResultTypeDef",
    "DeleteCertificateResultTypeDef",
    "DeleteContactMethodResultTypeDef",
    "DeleteDiskResultTypeDef",
    "DeleteDiskSnapshotResultTypeDef",
    "DeleteDistributionResultTypeDef",
    "DeleteDomainEntryResultTypeDef",
    "DeleteDomainResultTypeDef",
    "DeleteInstanceResultTypeDef",
    "DeleteInstanceSnapshotResultTypeDef",
    "DeleteKeyPairResultTypeDef",
    "DeleteKnownHostKeysResultTypeDef",
    "DeleteLoadBalancerResultTypeDef",
    "DeleteLoadBalancerTlsCertificateResultTypeDef",
    "DeleteRelationalDatabaseResultTypeDef",
    "DeleteRelationalDatabaseSnapshotResultTypeDef",
    "DetachCertificateFromDistributionResultTypeDef",
    "DetachDiskResultTypeDef",
    "DetachInstancesFromLoadBalancerResultTypeDef",
    "DetachStaticIpResultTypeDef",
    "DisableAddOnResultTypeDef",
    "EnableAddOnResultTypeDef",
    "ExportSnapshotResultTypeDef",
    "GetOperationResultTypeDef",
    "GetOperationsForResourceResultTypeDef",
    "GetOperationsResultTypeDef",
    "ImportKeyPairResultTypeDef",
    "OpenInstancePublicPortsResultTypeDef",
    "PeerVpcResultTypeDef",
    "PutAlarmResultTypeDef",
    "PutInstancePublicPortsResultTypeDef",
    "RebootInstanceResultTypeDef",
    "RebootRelationalDatabaseResultTypeDef",
    "ReleaseStaticIpResultTypeDef",
    "ResetDistributionCacheResultTypeDef",
    "SendContactMethodVerificationResultTypeDef",
    "SetIpAddressTypeResultTypeDef",
    "SetResourceAccessForBucketResultTypeDef",
    "StartInstanceResultTypeDef",
    "StartRelationalDatabaseResultTypeDef",
    "StopInstanceResultTypeDef",
    "StopRelationalDatabaseResultTypeDef",
    "TagResourceResultTypeDef",
    "TestAlarmResultTypeDef",
    "UnpeerVpcResultTypeDef",
    "UntagResourceResultTypeDef",
    "UpdateBucketBundleResultTypeDef",
    "UpdateDistributionBundleResultTypeDef",
    "UpdateDistributionResultTypeDef",
    "UpdateDomainEntryResultTypeDef",
    "UpdateLoadBalancerAttributeResultTypeDef",
    "UpdateRelationalDatabaseParametersResultTypeDef",
    "UpdateRelationalDatabaseResultTypeDef",
    "GetStaticIpResultTypeDef",
    "GetStaticIpsResultTypeDef",
    "GetAutoSnapshotsResultTypeDef",
    "GetRegionsResultTypeDef",
    "CreateBucketResultTypeDef",
    "GetBucketsResultTypeDef",
    "UpdateBucketResultTypeDef",
    "GetDiskSnapshotResultTypeDef",
    "GetDiskSnapshotsResultTypeDef",
    "GetDiskResultTypeDef",
    "GetDisksResultTypeDef",
    "InstanceHardwareTypeDef",
    "InstanceSnapshotTypeDef",
    "CreateKeyPairResultTypeDef",
    "GetKeyPairResultTypeDef",
    "GetKeyPairsResultTypeDef",
    "GetRelationalDatabaseSnapshotResultTypeDef",
    "GetRelationalDatabaseSnapshotsResultTypeDef",
    "CreateDistributionRequestRequestTypeDef",
    "LightsailDistributionTypeDef",
    "UpdateDistributionRequestRequestTypeDef",
    "GetCloudFormationStackRecordsResultTypeDef",
    "UpdateContainerServiceRequestRequestTypeDef",
    "ContainerServiceDeploymentTypeDef",
    "ContainerServiceDeploymentRequestTypeDef",
    "CreateContainerServiceDeploymentRequestRequestTypeDef",
    "GetDomainResultTypeDef",
    "GetDomainsResultTypeDef",
    "ExportSnapshotRecordSourceInfoTypeDef",
    "RenewalSummaryTypeDef",
    "GetInstanceAccessDetailsResultTypeDef",
    "LoadBalancerTlsCertificateTypeDef",
    "GetLoadBalancerResultTypeDef",
    "GetLoadBalancersResultTypeDef",
    "GetRelationalDatabaseResultTypeDef",
    "GetRelationalDatabasesResultTypeDef",
    "InstanceTypeDef",
    "GetInstanceSnapshotResultTypeDef",
    "GetInstanceSnapshotsResultTypeDef",
    "CreateDistributionResultTypeDef",
    "GetDistributionsResultTypeDef",
    "ContainerServiceTypeDef",
    "GetContainerServiceDeploymentsResultTypeDef",
    "CreateContainerServiceRequestRequestTypeDef",
    "ExportSnapshotRecordTypeDef",
    "CertificateTypeDef",
    "GetLoadBalancerTlsCertificatesResultTypeDef",
    "GetInstanceResultTypeDef",
    "GetInstancesResultTypeDef",
    "ContainerServicesListResultTypeDef",
    "CreateContainerServiceDeploymentResultTypeDef",
    "CreateContainerServiceResultTypeDef",
    "UpdateContainerServiceResultTypeDef",
    "GetExportSnapshotRecordsResultTypeDef",
    "CertificateSummaryTypeDef",
    "CreateCertificateResultTypeDef",
    "GetCertificatesResultTypeDef",
)

AccessKeyLastUsedTypeDef = TypedDict(
    "AccessKeyLastUsedTypeDef",
    {
        "lastUsedDate": datetime,
        "region": str,
        "serviceName": str,
    },
    total=False,
)

AccessRulesTypeDef = TypedDict(
    "AccessRulesTypeDef",
    {
        "getObject": AccessTypeType,
        "allowPublicOverrides": bool,
    },
    total=False,
)

AccountLevelBpaSyncTypeDef = TypedDict(
    "AccountLevelBpaSyncTypeDef",
    {
        "status": AccountLevelBpaSyncStatusType,
        "lastSyncedAt": datetime,
        "message": BPAStatusMessageType,
        "bpaImpactsLightsail": bool,
    },
    total=False,
)

AutoSnapshotAddOnRequestTypeDef = TypedDict(
    "AutoSnapshotAddOnRequestTypeDef",
    {
        "snapshotTimeOfDay": str,
    },
    total=False,
)

AddOnTypeDef = TypedDict(
    "AddOnTypeDef",
    {
        "name": str,
        "status": str,
        "snapshotTimeOfDay": str,
        "nextSnapshotTimeOfDay": str,
    },
    total=False,
)

MonitoredResourceInfoTypeDef = TypedDict(
    "MonitoredResourceInfoTypeDef",
    {
        "arn": str,
        "name": str,
        "resourceType": ResourceTypeType,
    },
    total=False,
)

ResourceLocationTypeDef = TypedDict(
    "ResourceLocationTypeDef",
    {
        "availabilityZone": str,
        "regionName": RegionNameType,
    },
    total=False,
)

AllocateStaticIpRequestRequestTypeDef = TypedDict(
    "AllocateStaticIpRequestRequestTypeDef",
    {
        "staticIpName": str,
    },
)

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

AttachCertificateToDistributionRequestRequestTypeDef = TypedDict(
    "AttachCertificateToDistributionRequestRequestTypeDef",
    {
        "distributionName": str,
        "certificateName": str,
    },
)

AttachDiskRequestRequestTypeDef = TypedDict(
    "AttachDiskRequestRequestTypeDef",
    {
        "diskName": str,
        "instanceName": str,
        "diskPath": str,
    },
)

AttachInstancesToLoadBalancerRequestRequestTypeDef = TypedDict(
    "AttachInstancesToLoadBalancerRequestRequestTypeDef",
    {
        "loadBalancerName": str,
        "instanceNames": Sequence[str],
    },
)

AttachLoadBalancerTlsCertificateRequestRequestTypeDef = TypedDict(
    "AttachLoadBalancerTlsCertificateRequestRequestTypeDef",
    {
        "loadBalancerName": str,
        "certificateName": str,
    },
)

AttachStaticIpRequestRequestTypeDef = TypedDict(
    "AttachStaticIpRequestRequestTypeDef",
    {
        "staticIpName": str,
        "instanceName": str,
    },
)

AttachedDiskTypeDef = TypedDict(
    "AttachedDiskTypeDef",
    {
        "path": str,
        "sizeInGb": int,
    },
    total=False,
)

AvailabilityZoneTypeDef = TypedDict(
    "AvailabilityZoneTypeDef",
    {
        "zoneName": str,
        "state": str,
    },
    total=False,
)

BlueprintTypeDef = TypedDict(
    "BlueprintTypeDef",
    {
        "blueprintId": str,
        "name": str,
        "group": str,
        "type": BlueprintTypeType,
        "description": str,
        "isActive": bool,
        "minPower": int,
        "version": str,
        "versionCode": str,
        "productUrl": str,
        "licenseUrl": str,
        "platform": InstancePlatformType,
    },
    total=False,
)

_RequiredBucketAccessLogConfigTypeDef = TypedDict(
    "_RequiredBucketAccessLogConfigTypeDef",
    {
        "enabled": bool,
    },
)
_OptionalBucketAccessLogConfigTypeDef = TypedDict(
    "_OptionalBucketAccessLogConfigTypeDef",
    {
        "destination": str,
        "prefix": str,
    },
    total=False,
)


class BucketAccessLogConfigTypeDef(
    _RequiredBucketAccessLogConfigTypeDef, _OptionalBucketAccessLogConfigTypeDef
):
    pass


BucketBundleTypeDef = TypedDict(
    "BucketBundleTypeDef",
    {
        "bundleId": str,
        "name": str,
        "price": float,
        "storagePerMonthInGb": int,
        "transferPerMonthInGb": int,
        "isActive": bool,
    },
    total=False,
)

BucketStateTypeDef = TypedDict(
    "BucketStateTypeDef",
    {
        "code": str,
        "message": str,
    },
    total=False,
)

ResourceReceivingAccessTypeDef = TypedDict(
    "ResourceReceivingAccessTypeDef",
    {
        "name": str,
        "resourceType": str,
    },
    total=False,
)

TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "key": str,
        "value": str,
    },
    total=False,
)

BundleTypeDef = TypedDict(
    "BundleTypeDef",
    {
        "price": float,
        "cpuCount": int,
        "diskSizeInGb": int,
        "bundleId": str,
        "instanceType": str,
        "isActive": bool,
        "name": str,
        "power": int,
        "ramSizeInGb": float,
        "transferPerMonthInGb": int,
        "supportedPlatforms": List[InstancePlatformType],
    },
    total=False,
)

CacheBehaviorPerPathTypeDef = TypedDict(
    "CacheBehaviorPerPathTypeDef",
    {
        "path": str,
        "behavior": BehaviorEnumType,
    },
    total=False,
)

CacheBehaviorTypeDef = TypedDict(
    "CacheBehaviorTypeDef",
    {
        "behavior": BehaviorEnumType,
    },
    total=False,
)

CookieObjectTypeDef = TypedDict(
    "CookieObjectTypeDef",
    {
        "option": ForwardValuesType,
        "cookiesAllowList": Sequence[str],
    },
    total=False,
)

HeaderObjectTypeDef = TypedDict(
    "HeaderObjectTypeDef",
    {
        "option": ForwardValuesType,
        "headersAllowList": Sequence[HeaderEnumType],
    },
    total=False,
)

QueryStringObjectTypeDef = TypedDict(
    "QueryStringObjectTypeDef",
    {
        "option": bool,
        "queryStringsAllowList": Sequence[str],
    },
    total=False,
)

PortInfoTypeDef = TypedDict(
    "PortInfoTypeDef",
    {
        "fromPort": int,
        "toPort": int,
        "protocol": NetworkProtocolType,
        "cidrs": Sequence[str],
        "ipv6Cidrs": Sequence[str],
        "cidrListAliases": Sequence[str],
    },
    total=False,
)

CloudFormationStackRecordSourceInfoTypeDef = TypedDict(
    "CloudFormationStackRecordSourceInfoTypeDef",
    {
        "resourceType": Literal["ExportSnapshotRecord"],
        "name": str,
        "arn": str,
    },
    total=False,
)

DestinationInfoTypeDef = TypedDict(
    "DestinationInfoTypeDef",
    {
        "id": str,
        "service": str,
    },
    total=False,
)

ContainerImageTypeDef = TypedDict(
    "ContainerImageTypeDef",
    {
        "image": str,
        "digest": str,
        "createdAt": datetime,
    },
    total=False,
)

ContainerTypeDef = TypedDict(
    "ContainerTypeDef",
    {
        "image": str,
        "command": Sequence[str],
        "environment": Mapping[str, str],
        "ports": Mapping[str, ContainerServiceProtocolType],
    },
    total=False,
)

ContainerServiceECRImagePullerRoleRequestTypeDef = TypedDict(
    "ContainerServiceECRImagePullerRoleRequestTypeDef",
    {
        "isActive": bool,
    },
    total=False,
)

ContainerServiceECRImagePullerRoleTypeDef = TypedDict(
    "ContainerServiceECRImagePullerRoleTypeDef",
    {
        "isActive": bool,
        "principalArn": str,
    },
    total=False,
)

ContainerServiceHealthCheckConfigTypeDef = TypedDict(
    "ContainerServiceHealthCheckConfigTypeDef",
    {
        "healthyThreshold": int,
        "unhealthyThreshold": int,
        "timeoutSeconds": int,
        "intervalSeconds": int,
        "path": str,
        "successCodes": str,
    },
    total=False,
)

ContainerServiceLogEventTypeDef = TypedDict(
    "ContainerServiceLogEventTypeDef",
    {
        "createdAt": datetime,
        "message": str,
    },
    total=False,
)

ContainerServicePowerTypeDef = TypedDict(
    "ContainerServicePowerTypeDef",
    {
        "powerId": str,
        "price": float,
        "cpuCount": float,
        "ramSizeInGb": float,
        "name": str,
        "isActive": bool,
    },
    total=False,
)

ContainerServiceRegistryLoginTypeDef = TypedDict(
    "ContainerServiceRegistryLoginTypeDef",
    {
        "username": str,
        "password": str,
        "expiresAt": datetime,
        "registry": str,
    },
    total=False,
)

ContainerServiceStateDetailTypeDef = TypedDict(
    "ContainerServiceStateDetailTypeDef",
    {
        "code": ContainerServiceStateDetailCodeType,
        "message": str,
    },
    total=False,
)

_RequiredCopySnapshotRequestRequestTypeDef = TypedDict(
    "_RequiredCopySnapshotRequestRequestTypeDef",
    {
        "targetSnapshotName": str,
        "sourceRegion": RegionNameType,
    },
)
_OptionalCopySnapshotRequestRequestTypeDef = TypedDict(
    "_OptionalCopySnapshotRequestRequestTypeDef",
    {
        "sourceSnapshotName": str,
        "sourceResourceName": str,
        "restoreDate": str,
        "useLatestRestorableAutoSnapshot": bool,
    },
    total=False,
)


class CopySnapshotRequestRequestTypeDef(
    _RequiredCopySnapshotRequestRequestTypeDef, _OptionalCopySnapshotRequestRequestTypeDef
):
    pass


CreateBucketAccessKeyRequestRequestTypeDef = TypedDict(
    "CreateBucketAccessKeyRequestRequestTypeDef",
    {
        "bucketName": str,
    },
)

_RequiredInstanceEntryTypeDef = TypedDict(
    "_RequiredInstanceEntryTypeDef",
    {
        "sourceName": str,
        "instanceType": str,
        "portInfoSource": PortInfoSourceTypeType,
        "availabilityZone": str,
    },
)
_OptionalInstanceEntryTypeDef = TypedDict(
    "_OptionalInstanceEntryTypeDef",
    {
        "userData": str,
    },
    total=False,
)


class InstanceEntryTypeDef(_RequiredInstanceEntryTypeDef, _OptionalInstanceEntryTypeDef):
    pass


CreateContactMethodRequestRequestTypeDef = TypedDict(
    "CreateContactMethodRequestRequestTypeDef",
    {
        "protocol": ContactProtocolType,
        "contactEndpoint": str,
    },
)

InputOriginTypeDef = TypedDict(
    "InputOriginTypeDef",
    {
        "name": str,
        "regionName": RegionNameType,
        "protocolPolicy": OriginProtocolPolicyEnumType,
    },
    total=False,
)

DomainEntryTypeDef = TypedDict(
    "DomainEntryTypeDef",
    {
        "id": str,
        "name": str,
        "target": str,
        "isAlias": bool,
        "type": str,
        "options": Mapping[str, str],
    },
    total=False,
)

DiskMapTypeDef = TypedDict(
    "DiskMapTypeDef",
    {
        "originalDiskPath": str,
        "newDiskName": str,
    },
    total=False,
)

DeleteAlarmRequestRequestTypeDef = TypedDict(
    "DeleteAlarmRequestRequestTypeDef",
    {
        "alarmName": str,
    },
)

DeleteAutoSnapshotRequestRequestTypeDef = TypedDict(
    "DeleteAutoSnapshotRequestRequestTypeDef",
    {
        "resourceName": str,
        "date": str,
    },
)

DeleteBucketAccessKeyRequestRequestTypeDef = TypedDict(
    "DeleteBucketAccessKeyRequestRequestTypeDef",
    {
        "bucketName": str,
        "accessKeyId": str,
    },
)

_RequiredDeleteBucketRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteBucketRequestRequestTypeDef",
    {
        "bucketName": str,
    },
)
_OptionalDeleteBucketRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteBucketRequestRequestTypeDef",
    {
        "forceDelete": bool,
    },
    total=False,
)


class DeleteBucketRequestRequestTypeDef(
    _RequiredDeleteBucketRequestRequestTypeDef, _OptionalDeleteBucketRequestRequestTypeDef
):
    pass


DeleteCertificateRequestRequestTypeDef = TypedDict(
    "DeleteCertificateRequestRequestTypeDef",
    {
        "certificateName": str,
    },
)

DeleteContactMethodRequestRequestTypeDef = TypedDict(
    "DeleteContactMethodRequestRequestTypeDef",
    {
        "protocol": ContactProtocolType,
    },
)

DeleteContainerImageRequestRequestTypeDef = TypedDict(
    "DeleteContainerImageRequestRequestTypeDef",
    {
        "serviceName": str,
        "image": str,
    },
)

DeleteContainerServiceRequestRequestTypeDef = TypedDict(
    "DeleteContainerServiceRequestRequestTypeDef",
    {
        "serviceName": str,
    },
)

_RequiredDeleteDiskRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteDiskRequestRequestTypeDef",
    {
        "diskName": str,
    },
)
_OptionalDeleteDiskRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteDiskRequestRequestTypeDef",
    {
        "forceDeleteAddOns": bool,
    },
    total=False,
)


class DeleteDiskRequestRequestTypeDef(
    _RequiredDeleteDiskRequestRequestTypeDef, _OptionalDeleteDiskRequestRequestTypeDef
):
    pass


DeleteDiskSnapshotRequestRequestTypeDef = TypedDict(
    "DeleteDiskSnapshotRequestRequestTypeDef",
    {
        "diskSnapshotName": str,
    },
)

DeleteDistributionRequestRequestTypeDef = TypedDict(
    "DeleteDistributionRequestRequestTypeDef",
    {
        "distributionName": str,
    },
    total=False,
)

DeleteDomainRequestRequestTypeDef = TypedDict(
    "DeleteDomainRequestRequestTypeDef",
    {
        "domainName": str,
    },
)

_RequiredDeleteInstanceRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteInstanceRequestRequestTypeDef",
    {
        "instanceName": str,
    },
)
_OptionalDeleteInstanceRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteInstanceRequestRequestTypeDef",
    {
        "forceDeleteAddOns": bool,
    },
    total=False,
)


class DeleteInstanceRequestRequestTypeDef(
    _RequiredDeleteInstanceRequestRequestTypeDef, _OptionalDeleteInstanceRequestRequestTypeDef
):
    pass


DeleteInstanceSnapshotRequestRequestTypeDef = TypedDict(
    "DeleteInstanceSnapshotRequestRequestTypeDef",
    {
        "instanceSnapshotName": str,
    },
)

_RequiredDeleteKeyPairRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteKeyPairRequestRequestTypeDef",
    {
        "keyPairName": str,
    },
)
_OptionalDeleteKeyPairRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteKeyPairRequestRequestTypeDef",
    {
        "expectedFingerprint": str,
    },
    total=False,
)


class DeleteKeyPairRequestRequestTypeDef(
    _RequiredDeleteKeyPairRequestRequestTypeDef, _OptionalDeleteKeyPairRequestRequestTypeDef
):
    pass


DeleteKnownHostKeysRequestRequestTypeDef = TypedDict(
    "DeleteKnownHostKeysRequestRequestTypeDef",
    {
        "instanceName": str,
    },
)

DeleteLoadBalancerRequestRequestTypeDef = TypedDict(
    "DeleteLoadBalancerRequestRequestTypeDef",
    {
        "loadBalancerName": str,
    },
)

_RequiredDeleteLoadBalancerTlsCertificateRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteLoadBalancerTlsCertificateRequestRequestTypeDef",
    {
        "loadBalancerName": str,
        "certificateName": str,
    },
)
_OptionalDeleteLoadBalancerTlsCertificateRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteLoadBalancerTlsCertificateRequestRequestTypeDef",
    {
        "force": bool,
    },
    total=False,
)


class DeleteLoadBalancerTlsCertificateRequestRequestTypeDef(
    _RequiredDeleteLoadBalancerTlsCertificateRequestRequestTypeDef,
    _OptionalDeleteLoadBalancerTlsCertificateRequestRequestTypeDef,
):
    pass


_RequiredDeleteRelationalDatabaseRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteRelationalDatabaseRequestRequestTypeDef",
    {
        "relationalDatabaseName": str,
    },
)
_OptionalDeleteRelationalDatabaseRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteRelationalDatabaseRequestRequestTypeDef",
    {
        "skipFinalSnapshot": bool,
        "finalRelationalDatabaseSnapshotName": str,
    },
    total=False,
)


class DeleteRelationalDatabaseRequestRequestTypeDef(
    _RequiredDeleteRelationalDatabaseRequestRequestTypeDef,
    _OptionalDeleteRelationalDatabaseRequestRequestTypeDef,
):
    pass


DeleteRelationalDatabaseSnapshotRequestRequestTypeDef = TypedDict(
    "DeleteRelationalDatabaseSnapshotRequestRequestTypeDef",
    {
        "relationalDatabaseSnapshotName": str,
    },
)

DetachCertificateFromDistributionRequestRequestTypeDef = TypedDict(
    "DetachCertificateFromDistributionRequestRequestTypeDef",
    {
        "distributionName": str,
    },
)

DetachDiskRequestRequestTypeDef = TypedDict(
    "DetachDiskRequestRequestTypeDef",
    {
        "diskName": str,
    },
)

DetachInstancesFromLoadBalancerRequestRequestTypeDef = TypedDict(
    "DetachInstancesFromLoadBalancerRequestRequestTypeDef",
    {
        "loadBalancerName": str,
        "instanceNames": Sequence[str],
    },
)

DetachStaticIpRequestRequestTypeDef = TypedDict(
    "DetachStaticIpRequestRequestTypeDef",
    {
        "staticIpName": str,
    },
)

DisableAddOnRequestRequestTypeDef = TypedDict(
    "DisableAddOnRequestRequestTypeDef",
    {
        "addOnType": Literal["AutoSnapshot"],
        "resourceName": str,
    },
)

DiskInfoTypeDef = TypedDict(
    "DiskInfoTypeDef",
    {
        "name": str,
        "path": str,
        "sizeInGb": int,
        "isSystemDisk": bool,
    },
    total=False,
)

DiskSnapshotInfoTypeDef = TypedDict(
    "DiskSnapshotInfoTypeDef",
    {
        "sizeInGb": int,
    },
    total=False,
)

DistributionBundleTypeDef = TypedDict(
    "DistributionBundleTypeDef",
    {
        "bundleId": str,
        "name": str,
        "price": float,
        "transferPerMonthInGb": int,
        "isActive": bool,
    },
    total=False,
)

ResourceRecordTypeDef = TypedDict(
    "ResourceRecordTypeDef",
    {
        "name": str,
        "type": str,
        "value": str,
    },
    total=False,
)

ExportSnapshotRequestRequestTypeDef = TypedDict(
    "ExportSnapshotRequestRequestTypeDef",
    {
        "sourceSnapshotName": str,
    },
)

PaginatorConfigTypeDef = TypedDict(
    "PaginatorConfigTypeDef",
    {
        "MaxItems": int,
        "PageSize": int,
        "StartingToken": str,
    },
    total=False,
)

GetActiveNamesRequestRequestTypeDef = TypedDict(
    "GetActiveNamesRequestRequestTypeDef",
    {
        "pageToken": str,
    },
    total=False,
)

GetAlarmsRequestRequestTypeDef = TypedDict(
    "GetAlarmsRequestRequestTypeDef",
    {
        "alarmName": str,
        "pageToken": str,
        "monitoredResourceName": str,
    },
    total=False,
)

GetAutoSnapshotsRequestRequestTypeDef = TypedDict(
    "GetAutoSnapshotsRequestRequestTypeDef",
    {
        "resourceName": str,
    },
)

GetBlueprintsRequestRequestTypeDef = TypedDict(
    "GetBlueprintsRequestRequestTypeDef",
    {
        "includeInactive": bool,
        "pageToken": str,
    },
    total=False,
)

GetBucketAccessKeysRequestRequestTypeDef = TypedDict(
    "GetBucketAccessKeysRequestRequestTypeDef",
    {
        "bucketName": str,
    },
)

GetBucketBundlesRequestRequestTypeDef = TypedDict(
    "GetBucketBundlesRequestRequestTypeDef",
    {
        "includeInactive": bool,
    },
    total=False,
)

GetBucketMetricDataRequestRequestTypeDef = TypedDict(
    "GetBucketMetricDataRequestRequestTypeDef",
    {
        "bucketName": str,
        "metricName": BucketMetricNameType,
        "startTime": Union[datetime, str],
        "endTime": Union[datetime, str],
        "period": int,
        "statistics": Sequence[MetricStatisticType],
        "unit": MetricUnitType,
    },
)

MetricDatapointTypeDef = TypedDict(
    "MetricDatapointTypeDef",
    {
        "average": float,
        "maximum": float,
        "minimum": float,
        "sampleCount": float,
        "sum": float,
        "timestamp": datetime,
        "unit": MetricUnitType,
    },
    total=False,
)

GetBucketsRequestRequestTypeDef = TypedDict(
    "GetBucketsRequestRequestTypeDef",
    {
        "bucketName": str,
        "pageToken": str,
        "includeConnectedResources": bool,
    },
    total=False,
)

GetBundlesRequestRequestTypeDef = TypedDict(
    "GetBundlesRequestRequestTypeDef",
    {
        "includeInactive": bool,
        "pageToken": str,
    },
    total=False,
)

GetCertificatesRequestRequestTypeDef = TypedDict(
    "GetCertificatesRequestRequestTypeDef",
    {
        "certificateStatuses": Sequence[CertificateStatusType],
        "includeCertificateDetails": bool,
        "certificateName": str,
    },
    total=False,
)

GetCloudFormationStackRecordsRequestRequestTypeDef = TypedDict(
    "GetCloudFormationStackRecordsRequestRequestTypeDef",
    {
        "pageToken": str,
    },
    total=False,
)

GetContactMethodsRequestRequestTypeDef = TypedDict(
    "GetContactMethodsRequestRequestTypeDef",
    {
        "protocols": Sequence[ContactProtocolType],
    },
    total=False,
)

GetContainerImagesRequestRequestTypeDef = TypedDict(
    "GetContainerImagesRequestRequestTypeDef",
    {
        "serviceName": str,
    },
)

_RequiredGetContainerLogRequestRequestTypeDef = TypedDict(
    "_RequiredGetContainerLogRequestRequestTypeDef",
    {
        "serviceName": str,
        "containerName": str,
    },
)
_OptionalGetContainerLogRequestRequestTypeDef = TypedDict(
    "_OptionalGetContainerLogRequestRequestTypeDef",
    {
        "startTime": Union[datetime, str],
        "endTime": Union[datetime, str],
        "filterPattern": str,
        "pageToken": str,
    },
    total=False,
)


class GetContainerLogRequestRequestTypeDef(
    _RequiredGetContainerLogRequestRequestTypeDef, _OptionalGetContainerLogRequestRequestTypeDef
):
    pass


GetContainerServiceDeploymentsRequestRequestTypeDef = TypedDict(
    "GetContainerServiceDeploymentsRequestRequestTypeDef",
    {
        "serviceName": str,
    },
)

GetContainerServiceMetricDataRequestRequestTypeDef = TypedDict(
    "GetContainerServiceMetricDataRequestRequestTypeDef",
    {
        "serviceName": str,
        "metricName": ContainerServiceMetricNameType,
        "startTime": Union[datetime, str],
        "endTime": Union[datetime, str],
        "period": int,
        "statistics": Sequence[MetricStatisticType],
    },
)

GetContainerServicesRequestRequestTypeDef = TypedDict(
    "GetContainerServicesRequestRequestTypeDef",
    {
        "serviceName": str,
    },
    total=False,
)

GetDiskRequestRequestTypeDef = TypedDict(
    "GetDiskRequestRequestTypeDef",
    {
        "diskName": str,
    },
)

GetDiskSnapshotRequestRequestTypeDef = TypedDict(
    "GetDiskSnapshotRequestRequestTypeDef",
    {
        "diskSnapshotName": str,
    },
)

GetDiskSnapshotsRequestRequestTypeDef = TypedDict(
    "GetDiskSnapshotsRequestRequestTypeDef",
    {
        "pageToken": str,
    },
    total=False,
)

GetDisksRequestRequestTypeDef = TypedDict(
    "GetDisksRequestRequestTypeDef",
    {
        "pageToken": str,
    },
    total=False,
)

GetDistributionLatestCacheResetRequestRequestTypeDef = TypedDict(
    "GetDistributionLatestCacheResetRequestRequestTypeDef",
    {
        "distributionName": str,
    },
    total=False,
)

GetDistributionMetricDataRequestRequestTypeDef = TypedDict(
    "GetDistributionMetricDataRequestRequestTypeDef",
    {
        "distributionName": str,
        "metricName": DistributionMetricNameType,
        "startTime": Union[datetime, str],
        "endTime": Union[datetime, str],
        "period": int,
        "unit": MetricUnitType,
        "statistics": Sequence[MetricStatisticType],
    },
)

GetDistributionsRequestRequestTypeDef = TypedDict(
    "GetDistributionsRequestRequestTypeDef",
    {
        "distributionName": str,
        "pageToken": str,
    },
    total=False,
)

GetDomainRequestRequestTypeDef = TypedDict(
    "GetDomainRequestRequestTypeDef",
    {
        "domainName": str,
    },
)

GetDomainsRequestRequestTypeDef = TypedDict(
    "GetDomainsRequestRequestTypeDef",
    {
        "pageToken": str,
    },
    total=False,
)

GetExportSnapshotRecordsRequestRequestTypeDef = TypedDict(
    "GetExportSnapshotRecordsRequestRequestTypeDef",
    {
        "pageToken": str,
    },
    total=False,
)

_RequiredGetInstanceAccessDetailsRequestRequestTypeDef = TypedDict(
    "_RequiredGetInstanceAccessDetailsRequestRequestTypeDef",
    {
        "instanceName": str,
    },
)
_OptionalGetInstanceAccessDetailsRequestRequestTypeDef = TypedDict(
    "_OptionalGetInstanceAccessDetailsRequestRequestTypeDef",
    {
        "protocol": InstanceAccessProtocolType,
    },
    total=False,
)


class GetInstanceAccessDetailsRequestRequestTypeDef(
    _RequiredGetInstanceAccessDetailsRequestRequestTypeDef,
    _OptionalGetInstanceAccessDetailsRequestRequestTypeDef,
):
    pass


GetInstanceMetricDataRequestRequestTypeDef = TypedDict(
    "GetInstanceMetricDataRequestRequestTypeDef",
    {
        "instanceName": str,
        "metricName": InstanceMetricNameType,
        "period": int,
        "startTime": Union[datetime, str],
        "endTime": Union[datetime, str],
        "unit": MetricUnitType,
        "statistics": Sequence[MetricStatisticType],
    },
)

GetInstancePortStatesRequestRequestTypeDef = TypedDict(
    "GetInstancePortStatesRequestRequestTypeDef",
    {
        "instanceName": str,
    },
)

InstancePortStateTypeDef = TypedDict(
    "InstancePortStateTypeDef",
    {
        "fromPort": int,
        "toPort": int,
        "protocol": NetworkProtocolType,
        "state": PortStateType,
        "cidrs": List[str],
        "ipv6Cidrs": List[str],
        "cidrListAliases": List[str],
    },
    total=False,
)

GetInstanceRequestRequestTypeDef = TypedDict(
    "GetInstanceRequestRequestTypeDef",
    {
        "instanceName": str,
    },
)

GetInstanceSnapshotRequestRequestTypeDef = TypedDict(
    "GetInstanceSnapshotRequestRequestTypeDef",
    {
        "instanceSnapshotName": str,
    },
)

GetInstanceSnapshotsRequestRequestTypeDef = TypedDict(
    "GetInstanceSnapshotsRequestRequestTypeDef",
    {
        "pageToken": str,
    },
    total=False,
)

GetInstanceStateRequestRequestTypeDef = TypedDict(
    "GetInstanceStateRequestRequestTypeDef",
    {
        "instanceName": str,
    },
)

InstanceStateTypeDef = TypedDict(
    "InstanceStateTypeDef",
    {
        "code": int,
        "name": str,
    },
    total=False,
)

GetInstancesRequestRequestTypeDef = TypedDict(
    "GetInstancesRequestRequestTypeDef",
    {
        "pageToken": str,
    },
    total=False,
)

GetKeyPairRequestRequestTypeDef = TypedDict(
    "GetKeyPairRequestRequestTypeDef",
    {
        "keyPairName": str,
    },
)

GetKeyPairsRequestRequestTypeDef = TypedDict(
    "GetKeyPairsRequestRequestTypeDef",
    {
        "pageToken": str,
        "includeDefaultKeyPair": bool,
    },
    total=False,
)

GetLoadBalancerMetricDataRequestRequestTypeDef = TypedDict(
    "GetLoadBalancerMetricDataRequestRequestTypeDef",
    {
        "loadBalancerName": str,
        "metricName": LoadBalancerMetricNameType,
        "period": int,
        "startTime": Union[datetime, str],
        "endTime": Union[datetime, str],
        "unit": MetricUnitType,
        "statistics": Sequence[MetricStatisticType],
    },
)

GetLoadBalancerRequestRequestTypeDef = TypedDict(
    "GetLoadBalancerRequestRequestTypeDef",
    {
        "loadBalancerName": str,
    },
)

GetLoadBalancerTlsCertificatesRequestRequestTypeDef = TypedDict(
    "GetLoadBalancerTlsCertificatesRequestRequestTypeDef",
    {
        "loadBalancerName": str,
    },
)

GetLoadBalancerTlsPoliciesRequestRequestTypeDef = TypedDict(
    "GetLoadBalancerTlsPoliciesRequestRequestTypeDef",
    {
        "pageToken": str,
    },
    total=False,
)

LoadBalancerTlsPolicyTypeDef = TypedDict(
    "LoadBalancerTlsPolicyTypeDef",
    {
        "name": str,
        "isDefault": bool,
        "description": str,
        "protocols": List[str],
        "ciphers": List[str],
    },
    total=False,
)

GetLoadBalancersRequestRequestTypeDef = TypedDict(
    "GetLoadBalancersRequestRequestTypeDef",
    {
        "pageToken": str,
    },
    total=False,
)

GetOperationRequestRequestTypeDef = TypedDict(
    "GetOperationRequestRequestTypeDef",
    {
        "operationId": str,
    },
)

_RequiredGetOperationsForResourceRequestRequestTypeDef = TypedDict(
    "_RequiredGetOperationsForResourceRequestRequestTypeDef",
    {
        "resourceName": str,
    },
)
_OptionalGetOperationsForResourceRequestRequestTypeDef = TypedDict(
    "_OptionalGetOperationsForResourceRequestRequestTypeDef",
    {
        "pageToken": str,
    },
    total=False,
)


class GetOperationsForResourceRequestRequestTypeDef(
    _RequiredGetOperationsForResourceRequestRequestTypeDef,
    _OptionalGetOperationsForResourceRequestRequestTypeDef,
):
    pass


GetOperationsRequestRequestTypeDef = TypedDict(
    "GetOperationsRequestRequestTypeDef",
    {
        "pageToken": str,
    },
    total=False,
)

GetRegionsRequestRequestTypeDef = TypedDict(
    "GetRegionsRequestRequestTypeDef",
    {
        "includeAvailabilityZones": bool,
        "includeRelationalDatabaseAvailabilityZones": bool,
    },
    total=False,
)

GetRelationalDatabaseBlueprintsRequestRequestTypeDef = TypedDict(
    "GetRelationalDatabaseBlueprintsRequestRequestTypeDef",
    {
        "pageToken": str,
    },
    total=False,
)

RelationalDatabaseBlueprintTypeDef = TypedDict(
    "RelationalDatabaseBlueprintTypeDef",
    {
        "blueprintId": str,
        "engine": Literal["mysql"],
        "engineVersion": str,
        "engineDescription": str,
        "engineVersionDescription": str,
        "isEngineDefault": bool,
    },
    total=False,
)

GetRelationalDatabaseBundlesRequestRequestTypeDef = TypedDict(
    "GetRelationalDatabaseBundlesRequestRequestTypeDef",
    {
        "pageToken": str,
        "includeInactive": bool,
    },
    total=False,
)

RelationalDatabaseBundleTypeDef = TypedDict(
    "RelationalDatabaseBundleTypeDef",
    {
        "bundleId": str,
        "name": str,
        "price": float,
        "ramSizeInGb": float,
        "diskSizeInGb": int,
        "transferPerMonthInGb": int,
        "cpuCount": int,
        "isEncrypted": bool,
        "isActive": bool,
    },
    total=False,
)

_RequiredGetRelationalDatabaseEventsRequestRequestTypeDef = TypedDict(
    "_RequiredGetRelationalDatabaseEventsRequestRequestTypeDef",
    {
        "relationalDatabaseName": str,
    },
)
_OptionalGetRelationalDatabaseEventsRequestRequestTypeDef = TypedDict(
    "_OptionalGetRelationalDatabaseEventsRequestRequestTypeDef",
    {
        "durationInMinutes": int,
        "pageToken": str,
    },
    total=False,
)


class GetRelationalDatabaseEventsRequestRequestTypeDef(
    _RequiredGetRelationalDatabaseEventsRequestRequestTypeDef,
    _OptionalGetRelationalDatabaseEventsRequestRequestTypeDef,
):
    pass


RelationalDatabaseEventTypeDef = TypedDict(
    "RelationalDatabaseEventTypeDef",
    {
        "resource": str,
        "createdAt": datetime,
        "message": str,
        "eventCategories": List[str],
    },
    total=False,
)

_RequiredGetRelationalDatabaseLogEventsRequestRequestTypeDef = TypedDict(
    "_RequiredGetRelationalDatabaseLogEventsRequestRequestTypeDef",
    {
        "relationalDatabaseName": str,
        "logStreamName": str,
    },
)
_OptionalGetRelationalDatabaseLogEventsRequestRequestTypeDef = TypedDict(
    "_OptionalGetRelationalDatabaseLogEventsRequestRequestTypeDef",
    {
        "startTime": Union[datetime, str],
        "endTime": Union[datetime, str],
        "startFromHead": bool,
        "pageToken": str,
    },
    total=False,
)


class GetRelationalDatabaseLogEventsRequestRequestTypeDef(
    _RequiredGetRelationalDatabaseLogEventsRequestRequestTypeDef,
    _OptionalGetRelationalDatabaseLogEventsRequestRequestTypeDef,
):
    pass


LogEventTypeDef = TypedDict(
    "LogEventTypeDef",
    {
        "createdAt": datetime,
        "message": str,
    },
    total=False,
)

GetRelationalDatabaseLogStreamsRequestRequestTypeDef = TypedDict(
    "GetRelationalDatabaseLogStreamsRequestRequestTypeDef",
    {
        "relationalDatabaseName": str,
    },
)

_RequiredGetRelationalDatabaseMasterUserPasswordRequestRequestTypeDef = TypedDict(
    "_RequiredGetRelationalDatabaseMasterUserPasswordRequestRequestTypeDef",
    {
        "relationalDatabaseName": str,
    },
)
_OptionalGetRelationalDatabaseMasterUserPasswordRequestRequestTypeDef = TypedDict(
    "_OptionalGetRelationalDatabaseMasterUserPasswordRequestRequestTypeDef",
    {
        "passwordVersion": RelationalDatabasePasswordVersionType,
    },
    total=False,
)


class GetRelationalDatabaseMasterUserPasswordRequestRequestTypeDef(
    _RequiredGetRelationalDatabaseMasterUserPasswordRequestRequestTypeDef,
    _OptionalGetRelationalDatabaseMasterUserPasswordRequestRequestTypeDef,
):
    pass


GetRelationalDatabaseMetricDataRequestRequestTypeDef = TypedDict(
    "GetRelationalDatabaseMetricDataRequestRequestTypeDef",
    {
        "relationalDatabaseName": str,
        "metricName": RelationalDatabaseMetricNameType,
        "period": int,
        "startTime": Union[datetime, str],
        "endTime": Union[datetime, str],
        "unit": MetricUnitType,
        "statistics": Sequence[MetricStatisticType],
    },
)

_RequiredGetRelationalDatabaseParametersRequestRequestTypeDef = TypedDict(
    "_RequiredGetRelationalDatabaseParametersRequestRequestTypeDef",
    {
        "relationalDatabaseName": str,
    },
)
_OptionalGetRelationalDatabaseParametersRequestRequestTypeDef = TypedDict(
    "_OptionalGetRelationalDatabaseParametersRequestRequestTypeDef",
    {
        "pageToken": str,
    },
    total=False,
)


class GetRelationalDatabaseParametersRequestRequestTypeDef(
    _RequiredGetRelationalDatabaseParametersRequestRequestTypeDef,
    _OptionalGetRelationalDatabaseParametersRequestRequestTypeDef,
):
    pass


RelationalDatabaseParameterTypeDef = TypedDict(
    "RelationalDatabaseParameterTypeDef",
    {
        "allowedValues": str,
        "applyMethod": str,
        "applyType": str,
        "dataType": str,
        "description": str,
        "isModifiable": bool,
        "parameterName": str,
        "parameterValue": str,
    },
    total=False,
)

GetRelationalDatabaseRequestRequestTypeDef = TypedDict(
    "GetRelationalDatabaseRequestRequestTypeDef",
    {
        "relationalDatabaseName": str,
    },
)

GetRelationalDatabaseSnapshotRequestRequestTypeDef = TypedDict(
    "GetRelationalDatabaseSnapshotRequestRequestTypeDef",
    {
        "relationalDatabaseSnapshotName": str,
    },
)

GetRelationalDatabaseSnapshotsRequestRequestTypeDef = TypedDict(
    "GetRelationalDatabaseSnapshotsRequestRequestTypeDef",
    {
        "pageToken": str,
    },
    total=False,
)

GetRelationalDatabasesRequestRequestTypeDef = TypedDict(
    "GetRelationalDatabasesRequestRequestTypeDef",
    {
        "pageToken": str,
    },
    total=False,
)

GetStaticIpRequestRequestTypeDef = TypedDict(
    "GetStaticIpRequestRequestTypeDef",
    {
        "staticIpName": str,
    },
)

GetStaticIpsRequestRequestTypeDef = TypedDict(
    "GetStaticIpsRequestRequestTypeDef",
    {
        "pageToken": str,
    },
    total=False,
)

HostKeyAttributesTypeDef = TypedDict(
    "HostKeyAttributesTypeDef",
    {
        "algorithm": str,
        "publicKey": str,
        "witnessedAt": datetime,
        "fingerprintSHA1": str,
        "fingerprintSHA256": str,
        "notValidBefore": datetime,
        "notValidAfter": datetime,
    },
    total=False,
)

ImportKeyPairRequestRequestTypeDef = TypedDict(
    "ImportKeyPairRequestRequestTypeDef",
    {
        "keyPairName": str,
        "publicKeyBase64": str,
    },
)

PasswordDataTypeDef = TypedDict(
    "PasswordDataTypeDef",
    {
        "ciphertext": str,
        "keyPairName": str,
    },
    total=False,
)

InstanceHealthSummaryTypeDef = TypedDict(
    "InstanceHealthSummaryTypeDef",
    {
        "instanceName": str,
        "instanceHealth": InstanceHealthStateType,
        "instanceHealthReason": InstanceHealthReasonType,
    },
    total=False,
)

InstancePortInfoTypeDef = TypedDict(
    "InstancePortInfoTypeDef",
    {
        "fromPort": int,
        "toPort": int,
        "protocol": NetworkProtocolType,
        "accessFrom": str,
        "accessType": PortAccessTypeType,
        "commonName": str,
        "accessDirection": AccessDirectionType,
        "cidrs": List[str],
        "ipv6Cidrs": List[str],
        "cidrListAliases": List[str],
    },
    total=False,
)

MonthlyTransferTypeDef = TypedDict(
    "MonthlyTransferTypeDef",
    {
        "gbPerMonthAllocated": int,
    },
    total=False,
)

OriginTypeDef = TypedDict(
    "OriginTypeDef",
    {
        "name": str,
        "resourceType": ResourceTypeType,
        "regionName": RegionNameType,
        "protocolPolicy": OriginProtocolPolicyEnumType,
    },
    total=False,
)

LoadBalancerTlsCertificateDomainValidationOptionTypeDef = TypedDict(
    "LoadBalancerTlsCertificateDomainValidationOptionTypeDef",
    {
        "domainName": str,
        "validationStatus": LoadBalancerTlsCertificateDomainStatusType,
    },
    total=False,
)

LoadBalancerTlsCertificateDomainValidationRecordTypeDef = TypedDict(
    "LoadBalancerTlsCertificateDomainValidationRecordTypeDef",
    {
        "name": str,
        "type": str,
        "value": str,
        "validationStatus": LoadBalancerTlsCertificateDomainStatusType,
        "domainName": str,
    },
    total=False,
)

LoadBalancerTlsCertificateSummaryTypeDef = TypedDict(
    "LoadBalancerTlsCertificateSummaryTypeDef",
    {
        "name": str,
        "isAttached": bool,
    },
    total=False,
)

PendingMaintenanceActionTypeDef = TypedDict(
    "PendingMaintenanceActionTypeDef",
    {
        "action": str,
        "description": str,
        "currentApplyDate": datetime,
    },
    total=False,
)

PendingModifiedRelationalDatabaseValuesTypeDef = TypedDict(
    "PendingModifiedRelationalDatabaseValuesTypeDef",
    {
        "masterUserPassword": str,
        "engineVersion": str,
        "backupRetentionEnabled": bool,
    },
    total=False,
)

_RequiredPutAlarmRequestRequestTypeDef = TypedDict(
    "_RequiredPutAlarmRequestRequestTypeDef",
    {
        "alarmName": str,
        "metricName": MetricNameType,
        "monitoredResourceName": str,
        "comparisonOperator": ComparisonOperatorType,
        "threshold": float,
        "evaluationPeriods": int,
    },
)
_OptionalPutAlarmRequestRequestTypeDef = TypedDict(
    "_OptionalPutAlarmRequestRequestTypeDef",
    {
        "datapointsToAlarm": int,
        "treatMissingData": TreatMissingDataType,
        "contactProtocols": Sequence[ContactProtocolType],
        "notificationTriggers": Sequence[AlarmStateType],
        "notificationEnabled": bool,
    },
    total=False,
)


class PutAlarmRequestRequestTypeDef(
    _RequiredPutAlarmRequestRequestTypeDef, _OptionalPutAlarmRequestRequestTypeDef
):
    pass


RebootInstanceRequestRequestTypeDef = TypedDict(
    "RebootInstanceRequestRequestTypeDef",
    {
        "instanceName": str,
    },
)

RebootRelationalDatabaseRequestRequestTypeDef = TypedDict(
    "RebootRelationalDatabaseRequestRequestTypeDef",
    {
        "relationalDatabaseName": str,
    },
)

RegisterContainerImageRequestRequestTypeDef = TypedDict(
    "RegisterContainerImageRequestRequestTypeDef",
    {
        "serviceName": str,
        "label": str,
        "digest": str,
    },
)

RelationalDatabaseEndpointTypeDef = TypedDict(
    "RelationalDatabaseEndpointTypeDef",
    {
        "port": int,
        "address": str,
    },
    total=False,
)

RelationalDatabaseHardwareTypeDef = TypedDict(
    "RelationalDatabaseHardwareTypeDef",
    {
        "cpuCount": int,
        "diskSizeInGb": int,
        "ramSizeInGb": float,
    },
    total=False,
)

ReleaseStaticIpRequestRequestTypeDef = TypedDict(
    "ReleaseStaticIpRequestRequestTypeDef",
    {
        "staticIpName": str,
    },
)

ResetDistributionCacheRequestRequestTypeDef = TypedDict(
    "ResetDistributionCacheRequestRequestTypeDef",
    {
        "distributionName": str,
    },
    total=False,
)

SendContactMethodVerificationRequestRequestTypeDef = TypedDict(
    "SendContactMethodVerificationRequestRequestTypeDef",
    {
        "protocol": Literal["Email"],
    },
)

SetIpAddressTypeRequestRequestTypeDef = TypedDict(
    "SetIpAddressTypeRequestRequestTypeDef",
    {
        "resourceType": ResourceTypeType,
        "resourceName": str,
        "ipAddressType": IpAddressTypeType,
    },
)

SetResourceAccessForBucketRequestRequestTypeDef = TypedDict(
    "SetResourceAccessForBucketRequestRequestTypeDef",
    {
        "resourceName": str,
        "bucketName": str,
        "access": ResourceBucketAccessType,
    },
)

StartInstanceRequestRequestTypeDef = TypedDict(
    "StartInstanceRequestRequestTypeDef",
    {
        "instanceName": str,
    },
)

StartRelationalDatabaseRequestRequestTypeDef = TypedDict(
    "StartRelationalDatabaseRequestRequestTypeDef",
    {
        "relationalDatabaseName": str,
    },
)

_RequiredStopInstanceRequestRequestTypeDef = TypedDict(
    "_RequiredStopInstanceRequestRequestTypeDef",
    {
        "instanceName": str,
    },
)
_OptionalStopInstanceRequestRequestTypeDef = TypedDict(
    "_OptionalStopInstanceRequestRequestTypeDef",
    {
        "force": bool,
    },
    total=False,
)


class StopInstanceRequestRequestTypeDef(
    _RequiredStopInstanceRequestRequestTypeDef, _OptionalStopInstanceRequestRequestTypeDef
):
    pass


_RequiredStopRelationalDatabaseRequestRequestTypeDef = TypedDict(
    "_RequiredStopRelationalDatabaseRequestRequestTypeDef",
    {
        "relationalDatabaseName": str,
    },
)
_OptionalStopRelationalDatabaseRequestRequestTypeDef = TypedDict(
    "_OptionalStopRelationalDatabaseRequestRequestTypeDef",
    {
        "relationalDatabaseSnapshotName": str,
    },
    total=False,
)


class StopRelationalDatabaseRequestRequestTypeDef(
    _RequiredStopRelationalDatabaseRequestRequestTypeDef,
    _OptionalStopRelationalDatabaseRequestRequestTypeDef,
):
    pass


TestAlarmRequestRequestTypeDef = TypedDict(
    "TestAlarmRequestRequestTypeDef",
    {
        "alarmName": str,
        "state": AlarmStateType,
    },
)

_RequiredUntagResourceRequestRequestTypeDef = TypedDict(
    "_RequiredUntagResourceRequestRequestTypeDef",
    {
        "resourceName": str,
        "tagKeys": Sequence[str],
    },
)
_OptionalUntagResourceRequestRequestTypeDef = TypedDict(
    "_OptionalUntagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
    total=False,
)


class UntagResourceRequestRequestTypeDef(
    _RequiredUntagResourceRequestRequestTypeDef, _OptionalUntagResourceRequestRequestTypeDef
):
    pass


UpdateBucketBundleRequestRequestTypeDef = TypedDict(
    "UpdateBucketBundleRequestRequestTypeDef",
    {
        "bucketName": str,
        "bundleId": str,
    },
)

UpdateDistributionBundleRequestRequestTypeDef = TypedDict(
    "UpdateDistributionBundleRequestRequestTypeDef",
    {
        "distributionName": str,
        "bundleId": str,
    },
    total=False,
)

UpdateLoadBalancerAttributeRequestRequestTypeDef = TypedDict(
    "UpdateLoadBalancerAttributeRequestRequestTypeDef",
    {
        "loadBalancerName": str,
        "attributeName": LoadBalancerAttributeNameType,
        "attributeValue": str,
    },
)

_RequiredUpdateRelationalDatabaseRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateRelationalDatabaseRequestRequestTypeDef",
    {
        "relationalDatabaseName": str,
    },
)
_OptionalUpdateRelationalDatabaseRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateRelationalDatabaseRequestRequestTypeDef",
    {
        "masterUserPassword": str,
        "rotateMasterUserPassword": bool,
        "preferredBackupWindow": str,
        "preferredMaintenanceWindow": str,
        "enableBackupRetention": bool,
        "disableBackupRetention": bool,
        "publiclyAccessible": bool,
        "applyImmediately": bool,
        "caCertificateIdentifier": str,
    },
    total=False,
)


class UpdateRelationalDatabaseRequestRequestTypeDef(
    _RequiredUpdateRelationalDatabaseRequestRequestTypeDef,
    _OptionalUpdateRelationalDatabaseRequestRequestTypeDef,
):
    pass


AccessKeyTypeDef = TypedDict(
    "AccessKeyTypeDef",
    {
        "accessKeyId": str,
        "secretAccessKey": str,
        "status": StatusTypeType,
        "createdAt": datetime,
        "lastUsed": AccessKeyLastUsedTypeDef,
    },
    total=False,
)

_RequiredAddOnRequestTypeDef = TypedDict(
    "_RequiredAddOnRequestTypeDef",
    {
        "addOnType": Literal["AutoSnapshot"],
    },
)
_OptionalAddOnRequestTypeDef = TypedDict(
    "_OptionalAddOnRequestTypeDef",
    {
        "autoSnapshotAddOnRequest": AutoSnapshotAddOnRequestTypeDef,
    },
    total=False,
)


class AddOnRequestTypeDef(_RequiredAddOnRequestTypeDef, _OptionalAddOnRequestTypeDef):
    pass


AlarmTypeDef = TypedDict(
    "AlarmTypeDef",
    {
        "name": str,
        "arn": str,
        "createdAt": datetime,
        "location": ResourceLocationTypeDef,
        "resourceType": ResourceTypeType,
        "supportCode": str,
        "monitoredResourceInfo": MonitoredResourceInfoTypeDef,
        "comparisonOperator": ComparisonOperatorType,
        "evaluationPeriods": int,
        "period": int,
        "threshold": float,
        "datapointsToAlarm": int,
        "treatMissingData": TreatMissingDataType,
        "statistic": MetricStatisticType,
        "metricName": MetricNameType,
        "state": AlarmStateType,
        "unit": MetricUnitType,
        "contactProtocols": List[ContactProtocolType],
        "notificationTriggers": List[AlarmStateType],
        "notificationEnabled": bool,
    },
    total=False,
)

ContactMethodTypeDef = TypedDict(
    "ContactMethodTypeDef",
    {
        "contactEndpoint": str,
        "status": ContactMethodStatusType,
        "protocol": ContactProtocolType,
        "name": str,
        "arn": str,
        "createdAt": datetime,
        "location": ResourceLocationTypeDef,
        "resourceType": ResourceTypeType,
        "supportCode": str,
    },
    total=False,
)

OperationTypeDef = TypedDict(
    "OperationTypeDef",
    {
        "id": str,
        "resourceName": str,
        "resourceType": ResourceTypeType,
        "createdAt": datetime,
        "location": ResourceLocationTypeDef,
        "isTerminal": bool,
        "operationDetails": str,
        "operationType": OperationTypeType,
        "status": OperationStatusType,
        "statusChangedAt": datetime,
        "errorCode": str,
        "errorDetails": str,
    },
    total=False,
)

StaticIpTypeDef = TypedDict(
    "StaticIpTypeDef",
    {
        "name": str,
        "arn": str,
        "supportCode": str,
        "createdAt": datetime,
        "location": ResourceLocationTypeDef,
        "resourceType": ResourceTypeType,
        "ipAddress": str,
        "attachedTo": str,
        "isAttached": bool,
    },
    total=False,
)

DownloadDefaultKeyPairResultTypeDef = TypedDict(
    "DownloadDefaultKeyPairResultTypeDef",
    {
        "publicKeyBase64": str,
        "privateKeyBase64": str,
        "createdAt": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetActiveNamesResultTypeDef = TypedDict(
    "GetActiveNamesResultTypeDef",
    {
        "activeNames": List[str],
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetContainerAPIMetadataResultTypeDef = TypedDict(
    "GetContainerAPIMetadataResultTypeDef",
    {
        "metadata": List[Dict[str, str]],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetDistributionLatestCacheResetResultTypeDef = TypedDict(
    "GetDistributionLatestCacheResetResultTypeDef",
    {
        "status": str,
        "createTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetRelationalDatabaseLogStreamsResultTypeDef = TypedDict(
    "GetRelationalDatabaseLogStreamsResultTypeDef",
    {
        "logStreams": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetRelationalDatabaseMasterUserPasswordResultTypeDef = TypedDict(
    "GetRelationalDatabaseMasterUserPasswordResultTypeDef",
    {
        "masterUserPassword": str,
        "createdAt": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

IsVpcPeeredResultTypeDef = TypedDict(
    "IsVpcPeeredResultTypeDef",
    {
        "isPeered": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AutoSnapshotDetailsTypeDef = TypedDict(
    "AutoSnapshotDetailsTypeDef",
    {
        "date": str,
        "createdAt": datetime,
        "status": AutoSnapshotStatusType,
        "fromAttachedDisks": List[AttachedDiskTypeDef],
    },
    total=False,
)

RegionTypeDef = TypedDict(
    "RegionTypeDef",
    {
        "continentCode": str,
        "description": str,
        "displayName": str,
        "name": RegionNameType,
        "availabilityZones": List[AvailabilityZoneTypeDef],
        "relationalDatabaseAvailabilityZones": List[AvailabilityZoneTypeDef],
    },
    total=False,
)

GetBlueprintsResultTypeDef = TypedDict(
    "GetBlueprintsResultTypeDef",
    {
        "blueprints": List[BlueprintTypeDef],
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredUpdateBucketRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateBucketRequestRequestTypeDef",
    {
        "bucketName": str,
    },
)
_OptionalUpdateBucketRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateBucketRequestRequestTypeDef",
    {
        "accessRules": AccessRulesTypeDef,
        "versioning": str,
        "readonlyAccessAccounts": Sequence[str],
        "accessLogConfig": BucketAccessLogConfigTypeDef,
    },
    total=False,
)


class UpdateBucketRequestRequestTypeDef(
    _RequiredUpdateBucketRequestRequestTypeDef, _OptionalUpdateBucketRequestRequestTypeDef
):
    pass


GetBucketBundlesResultTypeDef = TypedDict(
    "GetBucketBundlesResultTypeDef",
    {
        "bundles": List[BucketBundleTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

BucketTypeDef = TypedDict(
    "BucketTypeDef",
    {
        "resourceType": str,
        "accessRules": AccessRulesTypeDef,
        "arn": str,
        "bundleId": str,
        "createdAt": datetime,
        "url": str,
        "location": ResourceLocationTypeDef,
        "name": str,
        "supportCode": str,
        "tags": List[TagTypeDef],
        "objectVersioning": str,
        "ableToUpdateBundle": bool,
        "readonlyAccessAccounts": List[str],
        "resourcesReceivingAccess": List[ResourceReceivingAccessTypeDef],
        "state": BucketStateTypeDef,
        "accessLogConfig": BucketAccessLogConfigTypeDef,
    },
    total=False,
)

_RequiredCreateBucketRequestRequestTypeDef = TypedDict(
    "_RequiredCreateBucketRequestRequestTypeDef",
    {
        "bucketName": str,
        "bundleId": str,
    },
)
_OptionalCreateBucketRequestRequestTypeDef = TypedDict(
    "_OptionalCreateBucketRequestRequestTypeDef",
    {
        "tags": Sequence[TagTypeDef],
        "enableObjectVersioning": bool,
    },
    total=False,
)


class CreateBucketRequestRequestTypeDef(
    _RequiredCreateBucketRequestRequestTypeDef, _OptionalCreateBucketRequestRequestTypeDef
):
    pass


_RequiredCreateCertificateRequestRequestTypeDef = TypedDict(
    "_RequiredCreateCertificateRequestRequestTypeDef",
    {
        "certificateName": str,
        "domainName": str,
    },
)
_OptionalCreateCertificateRequestRequestTypeDef = TypedDict(
    "_OptionalCreateCertificateRequestRequestTypeDef",
    {
        "subjectAlternativeNames": Sequence[str],
        "tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateCertificateRequestRequestTypeDef(
    _RequiredCreateCertificateRequestRequestTypeDef, _OptionalCreateCertificateRequestRequestTypeDef
):
    pass


_RequiredCreateDiskSnapshotRequestRequestTypeDef = TypedDict(
    "_RequiredCreateDiskSnapshotRequestRequestTypeDef",
    {
        "diskSnapshotName": str,
    },
)
_OptionalCreateDiskSnapshotRequestRequestTypeDef = TypedDict(
    "_OptionalCreateDiskSnapshotRequestRequestTypeDef",
    {
        "diskName": str,
        "instanceName": str,
        "tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateDiskSnapshotRequestRequestTypeDef(
    _RequiredCreateDiskSnapshotRequestRequestTypeDef,
    _OptionalCreateDiskSnapshotRequestRequestTypeDef,
):
    pass


_RequiredCreateDomainRequestRequestTypeDef = TypedDict(
    "_RequiredCreateDomainRequestRequestTypeDef",
    {
        "domainName": str,
    },
)
_OptionalCreateDomainRequestRequestTypeDef = TypedDict(
    "_OptionalCreateDomainRequestRequestTypeDef",
    {
        "tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateDomainRequestRequestTypeDef(
    _RequiredCreateDomainRequestRequestTypeDef, _OptionalCreateDomainRequestRequestTypeDef
):
    pass


_RequiredCreateInstanceSnapshotRequestRequestTypeDef = TypedDict(
    "_RequiredCreateInstanceSnapshotRequestRequestTypeDef",
    {
        "instanceSnapshotName": str,
        "instanceName": str,
    },
)
_OptionalCreateInstanceSnapshotRequestRequestTypeDef = TypedDict(
    "_OptionalCreateInstanceSnapshotRequestRequestTypeDef",
    {
        "tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateInstanceSnapshotRequestRequestTypeDef(
    _RequiredCreateInstanceSnapshotRequestRequestTypeDef,
    _OptionalCreateInstanceSnapshotRequestRequestTypeDef,
):
    pass


_RequiredCreateKeyPairRequestRequestTypeDef = TypedDict(
    "_RequiredCreateKeyPairRequestRequestTypeDef",
    {
        "keyPairName": str,
    },
)
_OptionalCreateKeyPairRequestRequestTypeDef = TypedDict(
    "_OptionalCreateKeyPairRequestRequestTypeDef",
    {
        "tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateKeyPairRequestRequestTypeDef(
    _RequiredCreateKeyPairRequestRequestTypeDef, _OptionalCreateKeyPairRequestRequestTypeDef
):
    pass


_RequiredCreateLoadBalancerRequestRequestTypeDef = TypedDict(
    "_RequiredCreateLoadBalancerRequestRequestTypeDef",
    {
        "loadBalancerName": str,
        "instancePort": int,
    },
)
_OptionalCreateLoadBalancerRequestRequestTypeDef = TypedDict(
    "_OptionalCreateLoadBalancerRequestRequestTypeDef",
    {
        "healthCheckPath": str,
        "certificateName": str,
        "certificateDomainName": str,
        "certificateAlternativeNames": Sequence[str],
        "tags": Sequence[TagTypeDef],
        "ipAddressType": IpAddressTypeType,
        "tlsPolicyName": str,
    },
    total=False,
)


class CreateLoadBalancerRequestRequestTypeDef(
    _RequiredCreateLoadBalancerRequestRequestTypeDef,
    _OptionalCreateLoadBalancerRequestRequestTypeDef,
):
    pass


_RequiredCreateLoadBalancerTlsCertificateRequestRequestTypeDef = TypedDict(
    "_RequiredCreateLoadBalancerTlsCertificateRequestRequestTypeDef",
    {
        "loadBalancerName": str,
        "certificateName": str,
        "certificateDomainName": str,
    },
)
_OptionalCreateLoadBalancerTlsCertificateRequestRequestTypeDef = TypedDict(
    "_OptionalCreateLoadBalancerTlsCertificateRequestRequestTypeDef",
    {
        "certificateAlternativeNames": Sequence[str],
        "tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateLoadBalancerTlsCertificateRequestRequestTypeDef(
    _RequiredCreateLoadBalancerTlsCertificateRequestRequestTypeDef,
    _OptionalCreateLoadBalancerTlsCertificateRequestRequestTypeDef,
):
    pass


_RequiredCreateRelationalDatabaseFromSnapshotRequestRequestTypeDef = TypedDict(
    "_RequiredCreateRelationalDatabaseFromSnapshotRequestRequestTypeDef",
    {
        "relationalDatabaseName": str,
    },
)
_OptionalCreateRelationalDatabaseFromSnapshotRequestRequestTypeDef = TypedDict(
    "_OptionalCreateRelationalDatabaseFromSnapshotRequestRequestTypeDef",
    {
        "availabilityZone": str,
        "publiclyAccessible": bool,
        "relationalDatabaseSnapshotName": str,
        "relationalDatabaseBundleId": str,
        "sourceRelationalDatabaseName": str,
        "restoreTime": Union[datetime, str],
        "useLatestRestorableTime": bool,
        "tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateRelationalDatabaseFromSnapshotRequestRequestTypeDef(
    _RequiredCreateRelationalDatabaseFromSnapshotRequestRequestTypeDef,
    _OptionalCreateRelationalDatabaseFromSnapshotRequestRequestTypeDef,
):
    pass


_RequiredCreateRelationalDatabaseRequestRequestTypeDef = TypedDict(
    "_RequiredCreateRelationalDatabaseRequestRequestTypeDef",
    {
        "relationalDatabaseName": str,
        "relationalDatabaseBlueprintId": str,
        "relationalDatabaseBundleId": str,
        "masterDatabaseName": str,
        "masterUsername": str,
    },
)
_OptionalCreateRelationalDatabaseRequestRequestTypeDef = TypedDict(
    "_OptionalCreateRelationalDatabaseRequestRequestTypeDef",
    {
        "availabilityZone": str,
        "masterUserPassword": str,
        "preferredBackupWindow": str,
        "preferredMaintenanceWindow": str,
        "publiclyAccessible": bool,
        "tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateRelationalDatabaseRequestRequestTypeDef(
    _RequiredCreateRelationalDatabaseRequestRequestTypeDef,
    _OptionalCreateRelationalDatabaseRequestRequestTypeDef,
):
    pass


_RequiredCreateRelationalDatabaseSnapshotRequestRequestTypeDef = TypedDict(
    "_RequiredCreateRelationalDatabaseSnapshotRequestRequestTypeDef",
    {
        "relationalDatabaseName": str,
        "relationalDatabaseSnapshotName": str,
    },
)
_OptionalCreateRelationalDatabaseSnapshotRequestRequestTypeDef = TypedDict(
    "_OptionalCreateRelationalDatabaseSnapshotRequestRequestTypeDef",
    {
        "tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateRelationalDatabaseSnapshotRequestRequestTypeDef(
    _RequiredCreateRelationalDatabaseSnapshotRequestRequestTypeDef,
    _OptionalCreateRelationalDatabaseSnapshotRequestRequestTypeDef,
):
    pass


DiskSnapshotTypeDef = TypedDict(
    "DiskSnapshotTypeDef",
    {
        "name": str,
        "arn": str,
        "supportCode": str,
        "createdAt": datetime,
        "location": ResourceLocationTypeDef,
        "resourceType": ResourceTypeType,
        "tags": List[TagTypeDef],
        "sizeInGb": int,
        "state": DiskSnapshotStateType,
        "progress": str,
        "fromDiskName": str,
        "fromDiskArn": str,
        "fromInstanceName": str,
        "fromInstanceArn": str,
        "isFromAutoSnapshot": bool,
    },
    total=False,
)

DiskTypeDef = TypedDict(
    "DiskTypeDef",
    {
        "name": str,
        "arn": str,
        "supportCode": str,
        "createdAt": datetime,
        "location": ResourceLocationTypeDef,
        "resourceType": ResourceTypeType,
        "tags": List[TagTypeDef],
        "addOns": List[AddOnTypeDef],
        "sizeInGb": int,
        "isSystemDisk": bool,
        "iops": int,
        "path": str,
        "state": DiskStateType,
        "attachedTo": str,
        "isAttached": bool,
        "attachmentState": str,
        "gbInUse": int,
    },
    total=False,
)

KeyPairTypeDef = TypedDict(
    "KeyPairTypeDef",
    {
        "name": str,
        "arn": str,
        "supportCode": str,
        "createdAt": datetime,
        "location": ResourceLocationTypeDef,
        "resourceType": ResourceTypeType,
        "tags": List[TagTypeDef],
        "fingerprint": str,
    },
    total=False,
)

RelationalDatabaseSnapshotTypeDef = TypedDict(
    "RelationalDatabaseSnapshotTypeDef",
    {
        "name": str,
        "arn": str,
        "supportCode": str,
        "createdAt": datetime,
        "location": ResourceLocationTypeDef,
        "resourceType": ResourceTypeType,
        "tags": List[TagTypeDef],
        "engine": str,
        "engineVersion": str,
        "sizeInGb": int,
        "state": str,
        "fromRelationalDatabaseName": str,
        "fromRelationalDatabaseArn": str,
        "fromRelationalDatabaseBundleId": str,
        "fromRelationalDatabaseBlueprintId": str,
    },
    total=False,
)

_RequiredTagResourceRequestRequestTypeDef = TypedDict(
    "_RequiredTagResourceRequestRequestTypeDef",
    {
        "resourceName": str,
        "tags": Sequence[TagTypeDef],
    },
)
_OptionalTagResourceRequestRequestTypeDef = TypedDict(
    "_OptionalTagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
    total=False,
)


class TagResourceRequestRequestTypeDef(
    _RequiredTagResourceRequestRequestTypeDef, _OptionalTagResourceRequestRequestTypeDef
):
    pass


GetBundlesResultTypeDef = TypedDict(
    "GetBundlesResultTypeDef",
    {
        "bundles": List[BundleTypeDef],
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CacheSettingsTypeDef = TypedDict(
    "CacheSettingsTypeDef",
    {
        "defaultTTL": int,
        "minimumTTL": int,
        "maximumTTL": int,
        "allowedHTTPMethods": str,
        "cachedHTTPMethods": str,
        "forwardedCookies": CookieObjectTypeDef,
        "forwardedHeaders": HeaderObjectTypeDef,
        "forwardedQueryStrings": QueryStringObjectTypeDef,
    },
    total=False,
)

CloseInstancePublicPortsRequestRequestTypeDef = TypedDict(
    "CloseInstancePublicPortsRequestRequestTypeDef",
    {
        "portInfo": PortInfoTypeDef,
        "instanceName": str,
    },
)

OpenInstancePublicPortsRequestRequestTypeDef = TypedDict(
    "OpenInstancePublicPortsRequestRequestTypeDef",
    {
        "portInfo": PortInfoTypeDef,
        "instanceName": str,
    },
)

PutInstancePublicPortsRequestRequestTypeDef = TypedDict(
    "PutInstancePublicPortsRequestRequestTypeDef",
    {
        "portInfos": Sequence[PortInfoTypeDef],
        "instanceName": str,
    },
)

CloudFormationStackRecordTypeDef = TypedDict(
    "CloudFormationStackRecordTypeDef",
    {
        "name": str,
        "arn": str,
        "createdAt": datetime,
        "location": ResourceLocationTypeDef,
        "resourceType": ResourceTypeType,
        "state": RecordStateType,
        "sourceInfo": List[CloudFormationStackRecordSourceInfoTypeDef],
        "destinationInfo": DestinationInfoTypeDef,
    },
    total=False,
)

GetContainerImagesResultTypeDef = TypedDict(
    "GetContainerImagesResultTypeDef",
    {
        "containerImages": List[ContainerImageTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RegisterContainerImageResultTypeDef = TypedDict(
    "RegisterContainerImageResultTypeDef",
    {
        "containerImage": ContainerImageTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PrivateRegistryAccessRequestTypeDef = TypedDict(
    "PrivateRegistryAccessRequestTypeDef",
    {
        "ecrImagePullerRole": ContainerServiceECRImagePullerRoleRequestTypeDef,
    },
    total=False,
)

PrivateRegistryAccessTypeDef = TypedDict(
    "PrivateRegistryAccessTypeDef",
    {
        "ecrImagePullerRole": ContainerServiceECRImagePullerRoleTypeDef,
    },
    total=False,
)

ContainerServiceEndpointTypeDef = TypedDict(
    "ContainerServiceEndpointTypeDef",
    {
        "containerName": str,
        "containerPort": int,
        "healthCheck": ContainerServiceHealthCheckConfigTypeDef,
    },
    total=False,
)

_RequiredEndpointRequestTypeDef = TypedDict(
    "_RequiredEndpointRequestTypeDef",
    {
        "containerName": str,
        "containerPort": int,
    },
)
_OptionalEndpointRequestTypeDef = TypedDict(
    "_OptionalEndpointRequestTypeDef",
    {
        "healthCheck": ContainerServiceHealthCheckConfigTypeDef,
    },
    total=False,
)


class EndpointRequestTypeDef(_RequiredEndpointRequestTypeDef, _OptionalEndpointRequestTypeDef):
    pass


GetContainerLogResultTypeDef = TypedDict(
    "GetContainerLogResultTypeDef",
    {
        "logEvents": List[ContainerServiceLogEventTypeDef],
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetContainerServicePowersResultTypeDef = TypedDict(
    "GetContainerServicePowersResultTypeDef",
    {
        "powers": List[ContainerServicePowerTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateContainerServiceRegistryLoginResultTypeDef = TypedDict(
    "CreateContainerServiceRegistryLoginResultTypeDef",
    {
        "registryLogin": ContainerServiceRegistryLoginTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateCloudFormationStackRequestRequestTypeDef = TypedDict(
    "CreateCloudFormationStackRequestRequestTypeDef",
    {
        "instances": Sequence[InstanceEntryTypeDef],
    },
)

CreateDomainEntryRequestRequestTypeDef = TypedDict(
    "CreateDomainEntryRequestRequestTypeDef",
    {
        "domainName": str,
        "domainEntry": DomainEntryTypeDef,
    },
)

DeleteDomainEntryRequestRequestTypeDef = TypedDict(
    "DeleteDomainEntryRequestRequestTypeDef",
    {
        "domainName": str,
        "domainEntry": DomainEntryTypeDef,
    },
)

DomainTypeDef = TypedDict(
    "DomainTypeDef",
    {
        "name": str,
        "arn": str,
        "supportCode": str,
        "createdAt": datetime,
        "location": ResourceLocationTypeDef,
        "resourceType": ResourceTypeType,
        "tags": List[TagTypeDef],
        "domainEntries": List[DomainEntryTypeDef],
    },
    total=False,
)

UpdateDomainEntryRequestRequestTypeDef = TypedDict(
    "UpdateDomainEntryRequestRequestTypeDef",
    {
        "domainName": str,
        "domainEntry": DomainEntryTypeDef,
    },
)

InstanceSnapshotInfoTypeDef = TypedDict(
    "InstanceSnapshotInfoTypeDef",
    {
        "fromBundleId": str,
        "fromBlueprintId": str,
        "fromDiskInfo": List[DiskInfoTypeDef],
    },
    total=False,
)

GetDistributionBundlesResultTypeDef = TypedDict(
    "GetDistributionBundlesResultTypeDef",
    {
        "bundles": List[DistributionBundleTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DomainValidationRecordTypeDef = TypedDict(
    "DomainValidationRecordTypeDef",
    {
        "domainName": str,
        "resourceRecord": ResourceRecordTypeDef,
    },
    total=False,
)

GetActiveNamesRequestGetActiveNamesPaginateTypeDef = TypedDict(
    "GetActiveNamesRequestGetActiveNamesPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

GetBlueprintsRequestGetBlueprintsPaginateTypeDef = TypedDict(
    "GetBlueprintsRequestGetBlueprintsPaginateTypeDef",
    {
        "includeInactive": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

GetBundlesRequestGetBundlesPaginateTypeDef = TypedDict(
    "GetBundlesRequestGetBundlesPaginateTypeDef",
    {
        "includeInactive": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

GetCloudFormationStackRecordsRequestGetCloudFormationStackRecordsPaginateTypeDef = TypedDict(
    "GetCloudFormationStackRecordsRequestGetCloudFormationStackRecordsPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

GetDiskSnapshotsRequestGetDiskSnapshotsPaginateTypeDef = TypedDict(
    "GetDiskSnapshotsRequestGetDiskSnapshotsPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

GetDisksRequestGetDisksPaginateTypeDef = TypedDict(
    "GetDisksRequestGetDisksPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

GetDomainsRequestGetDomainsPaginateTypeDef = TypedDict(
    "GetDomainsRequestGetDomainsPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

GetExportSnapshotRecordsRequestGetExportSnapshotRecordsPaginateTypeDef = TypedDict(
    "GetExportSnapshotRecordsRequestGetExportSnapshotRecordsPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

GetInstanceSnapshotsRequestGetInstanceSnapshotsPaginateTypeDef = TypedDict(
    "GetInstanceSnapshotsRequestGetInstanceSnapshotsPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

GetInstancesRequestGetInstancesPaginateTypeDef = TypedDict(
    "GetInstancesRequestGetInstancesPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

GetKeyPairsRequestGetKeyPairsPaginateTypeDef = TypedDict(
    "GetKeyPairsRequestGetKeyPairsPaginateTypeDef",
    {
        "includeDefaultKeyPair": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

GetLoadBalancersRequestGetLoadBalancersPaginateTypeDef = TypedDict(
    "GetLoadBalancersRequestGetLoadBalancersPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

GetOperationsRequestGetOperationsPaginateTypeDef = TypedDict(
    "GetOperationsRequestGetOperationsPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

GetRelationalDatabaseBlueprintsRequestGetRelationalDatabaseBlueprintsPaginateTypeDef = TypedDict(
    "GetRelationalDatabaseBlueprintsRequestGetRelationalDatabaseBlueprintsPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

GetRelationalDatabaseBundlesRequestGetRelationalDatabaseBundlesPaginateTypeDef = TypedDict(
    "GetRelationalDatabaseBundlesRequestGetRelationalDatabaseBundlesPaginateTypeDef",
    {
        "includeInactive": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

_RequiredGetRelationalDatabaseEventsRequestGetRelationalDatabaseEventsPaginateTypeDef = TypedDict(
    "_RequiredGetRelationalDatabaseEventsRequestGetRelationalDatabaseEventsPaginateTypeDef",
    {
        "relationalDatabaseName": str,
    },
)
_OptionalGetRelationalDatabaseEventsRequestGetRelationalDatabaseEventsPaginateTypeDef = TypedDict(
    "_OptionalGetRelationalDatabaseEventsRequestGetRelationalDatabaseEventsPaginateTypeDef",
    {
        "durationInMinutes": int,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetRelationalDatabaseEventsRequestGetRelationalDatabaseEventsPaginateTypeDef(
    _RequiredGetRelationalDatabaseEventsRequestGetRelationalDatabaseEventsPaginateTypeDef,
    _OptionalGetRelationalDatabaseEventsRequestGetRelationalDatabaseEventsPaginateTypeDef,
):
    pass


_RequiredGetRelationalDatabaseParametersRequestGetRelationalDatabaseParametersPaginateTypeDef = TypedDict(
    "_RequiredGetRelationalDatabaseParametersRequestGetRelationalDatabaseParametersPaginateTypeDef",
    {
        "relationalDatabaseName": str,
    },
)
_OptionalGetRelationalDatabaseParametersRequestGetRelationalDatabaseParametersPaginateTypeDef = TypedDict(
    "_OptionalGetRelationalDatabaseParametersRequestGetRelationalDatabaseParametersPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class GetRelationalDatabaseParametersRequestGetRelationalDatabaseParametersPaginateTypeDef(
    _RequiredGetRelationalDatabaseParametersRequestGetRelationalDatabaseParametersPaginateTypeDef,
    _OptionalGetRelationalDatabaseParametersRequestGetRelationalDatabaseParametersPaginateTypeDef,
):
    pass


GetRelationalDatabaseSnapshotsRequestGetRelationalDatabaseSnapshotsPaginateTypeDef = TypedDict(
    "GetRelationalDatabaseSnapshotsRequestGetRelationalDatabaseSnapshotsPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

GetRelationalDatabasesRequestGetRelationalDatabasesPaginateTypeDef = TypedDict(
    "GetRelationalDatabasesRequestGetRelationalDatabasesPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

GetStaticIpsRequestGetStaticIpsPaginateTypeDef = TypedDict(
    "GetStaticIpsRequestGetStaticIpsPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

GetBucketMetricDataResultTypeDef = TypedDict(
    "GetBucketMetricDataResultTypeDef",
    {
        "metricName": BucketMetricNameType,
        "metricData": List[MetricDatapointTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetContainerServiceMetricDataResultTypeDef = TypedDict(
    "GetContainerServiceMetricDataResultTypeDef",
    {
        "metricName": ContainerServiceMetricNameType,
        "metricData": List[MetricDatapointTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetDistributionMetricDataResultTypeDef = TypedDict(
    "GetDistributionMetricDataResultTypeDef",
    {
        "metricName": DistributionMetricNameType,
        "metricData": List[MetricDatapointTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetInstanceMetricDataResultTypeDef = TypedDict(
    "GetInstanceMetricDataResultTypeDef",
    {
        "metricName": InstanceMetricNameType,
        "metricData": List[MetricDatapointTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetLoadBalancerMetricDataResultTypeDef = TypedDict(
    "GetLoadBalancerMetricDataResultTypeDef",
    {
        "metricName": LoadBalancerMetricNameType,
        "metricData": List[MetricDatapointTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetRelationalDatabaseMetricDataResultTypeDef = TypedDict(
    "GetRelationalDatabaseMetricDataResultTypeDef",
    {
        "metricName": RelationalDatabaseMetricNameType,
        "metricData": List[MetricDatapointTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetInstancePortStatesResultTypeDef = TypedDict(
    "GetInstancePortStatesResultTypeDef",
    {
        "portStates": List[InstancePortStateTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetInstanceStateResultTypeDef = TypedDict(
    "GetInstanceStateResultTypeDef",
    {
        "state": InstanceStateTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetLoadBalancerTlsPoliciesResultTypeDef = TypedDict(
    "GetLoadBalancerTlsPoliciesResultTypeDef",
    {
        "tlsPolicies": List[LoadBalancerTlsPolicyTypeDef],
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetRelationalDatabaseBlueprintsResultTypeDef = TypedDict(
    "GetRelationalDatabaseBlueprintsResultTypeDef",
    {
        "blueprints": List[RelationalDatabaseBlueprintTypeDef],
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetRelationalDatabaseBundlesResultTypeDef = TypedDict(
    "GetRelationalDatabaseBundlesResultTypeDef",
    {
        "bundles": List[RelationalDatabaseBundleTypeDef],
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetRelationalDatabaseEventsResultTypeDef = TypedDict(
    "GetRelationalDatabaseEventsResultTypeDef",
    {
        "relationalDatabaseEvents": List[RelationalDatabaseEventTypeDef],
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetRelationalDatabaseLogEventsResultTypeDef = TypedDict(
    "GetRelationalDatabaseLogEventsResultTypeDef",
    {
        "resourceLogEvents": List[LogEventTypeDef],
        "nextBackwardToken": str,
        "nextForwardToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetRelationalDatabaseParametersResultTypeDef = TypedDict(
    "GetRelationalDatabaseParametersResultTypeDef",
    {
        "parameters": List[RelationalDatabaseParameterTypeDef],
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateRelationalDatabaseParametersRequestRequestTypeDef = TypedDict(
    "UpdateRelationalDatabaseParametersRequestRequestTypeDef",
    {
        "relationalDatabaseName": str,
        "parameters": Sequence[RelationalDatabaseParameterTypeDef],
    },
)

InstanceAccessDetailsTypeDef = TypedDict(
    "InstanceAccessDetailsTypeDef",
    {
        "certKey": str,
        "expiresAt": datetime,
        "ipAddress": str,
        "password": str,
        "passwordData": PasswordDataTypeDef,
        "privateKey": str,
        "protocol": InstanceAccessProtocolType,
        "instanceName": str,
        "username": str,
        "hostKeys": List[HostKeyAttributesTypeDef],
    },
    total=False,
)

InstanceNetworkingTypeDef = TypedDict(
    "InstanceNetworkingTypeDef",
    {
        "monthlyTransfer": MonthlyTransferTypeDef,
        "ports": List[InstancePortInfoTypeDef],
    },
    total=False,
)

LoadBalancerTlsCertificateRenewalSummaryTypeDef = TypedDict(
    "LoadBalancerTlsCertificateRenewalSummaryTypeDef",
    {
        "renewalStatus": LoadBalancerTlsCertificateRenewalStatusType,
        "domainValidationOptions": List[LoadBalancerTlsCertificateDomainValidationOptionTypeDef],
    },
    total=False,
)

LoadBalancerTypeDef = TypedDict(
    "LoadBalancerTypeDef",
    {
        "name": str,
        "arn": str,
        "supportCode": str,
        "createdAt": datetime,
        "location": ResourceLocationTypeDef,
        "resourceType": ResourceTypeType,
        "tags": List[TagTypeDef],
        "dnsName": str,
        "state": LoadBalancerStateType,
        "protocol": LoadBalancerProtocolType,
        "publicPorts": List[int],
        "healthCheckPath": str,
        "instancePort": int,
        "instanceHealthSummary": List[InstanceHealthSummaryTypeDef],
        "tlsCertificateSummaries": List[LoadBalancerTlsCertificateSummaryTypeDef],
        "configurationOptions": Dict[LoadBalancerAttributeNameType, str],
        "ipAddressType": IpAddressTypeType,
        "httpsRedirectionEnabled": bool,
        "tlsPolicyName": str,
    },
    total=False,
)

RelationalDatabaseTypeDef = TypedDict(
    "RelationalDatabaseTypeDef",
    {
        "name": str,
        "arn": str,
        "supportCode": str,
        "createdAt": datetime,
        "location": ResourceLocationTypeDef,
        "resourceType": ResourceTypeType,
        "tags": List[TagTypeDef],
        "relationalDatabaseBlueprintId": str,
        "relationalDatabaseBundleId": str,
        "masterDatabaseName": str,
        "hardware": RelationalDatabaseHardwareTypeDef,
        "state": str,
        "secondaryAvailabilityZone": str,
        "backupRetentionEnabled": bool,
        "pendingModifiedValues": PendingModifiedRelationalDatabaseValuesTypeDef,
        "engine": str,
        "engineVersion": str,
        "latestRestorableTime": datetime,
        "masterUsername": str,
        "parameterApplyStatus": str,
        "preferredBackupWindow": str,
        "preferredMaintenanceWindow": str,
        "publiclyAccessible": bool,
        "masterEndpoint": RelationalDatabaseEndpointTypeDef,
        "pendingMaintenanceActions": List[PendingMaintenanceActionTypeDef],
        "caCertificateIdentifier": str,
    },
    total=False,
)

GetBucketAccessKeysResultTypeDef = TypedDict(
    "GetBucketAccessKeysResultTypeDef",
    {
        "accessKeys": List[AccessKeyTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredCreateDiskFromSnapshotRequestRequestTypeDef = TypedDict(
    "_RequiredCreateDiskFromSnapshotRequestRequestTypeDef",
    {
        "diskName": str,
        "availabilityZone": str,
        "sizeInGb": int,
    },
)
_OptionalCreateDiskFromSnapshotRequestRequestTypeDef = TypedDict(
    "_OptionalCreateDiskFromSnapshotRequestRequestTypeDef",
    {
        "diskSnapshotName": str,
        "tags": Sequence[TagTypeDef],
        "addOns": Sequence[AddOnRequestTypeDef],
        "sourceDiskName": str,
        "restoreDate": str,
        "useLatestRestorableAutoSnapshot": bool,
    },
    total=False,
)


class CreateDiskFromSnapshotRequestRequestTypeDef(
    _RequiredCreateDiskFromSnapshotRequestRequestTypeDef,
    _OptionalCreateDiskFromSnapshotRequestRequestTypeDef,
):
    pass


_RequiredCreateDiskRequestRequestTypeDef = TypedDict(
    "_RequiredCreateDiskRequestRequestTypeDef",
    {
        "diskName": str,
        "availabilityZone": str,
        "sizeInGb": int,
    },
)
_OptionalCreateDiskRequestRequestTypeDef = TypedDict(
    "_OptionalCreateDiskRequestRequestTypeDef",
    {
        "tags": Sequence[TagTypeDef],
        "addOns": Sequence[AddOnRequestTypeDef],
    },
    total=False,
)


class CreateDiskRequestRequestTypeDef(
    _RequiredCreateDiskRequestRequestTypeDef, _OptionalCreateDiskRequestRequestTypeDef
):
    pass


_RequiredCreateInstancesFromSnapshotRequestRequestTypeDef = TypedDict(
    "_RequiredCreateInstancesFromSnapshotRequestRequestTypeDef",
    {
        "instanceNames": Sequence[str],
        "availabilityZone": str,
        "bundleId": str,
    },
)
_OptionalCreateInstancesFromSnapshotRequestRequestTypeDef = TypedDict(
    "_OptionalCreateInstancesFromSnapshotRequestRequestTypeDef",
    {
        "attachedDiskMapping": Mapping[str, Sequence[DiskMapTypeDef]],
        "instanceSnapshotName": str,
        "userData": str,
        "keyPairName": str,
        "tags": Sequence[TagTypeDef],
        "addOns": Sequence[AddOnRequestTypeDef],
        "ipAddressType": IpAddressTypeType,
        "sourceInstanceName": str,
        "restoreDate": str,
        "useLatestRestorableAutoSnapshot": bool,
    },
    total=False,
)


class CreateInstancesFromSnapshotRequestRequestTypeDef(
    _RequiredCreateInstancesFromSnapshotRequestRequestTypeDef,
    _OptionalCreateInstancesFromSnapshotRequestRequestTypeDef,
):
    pass


_RequiredCreateInstancesRequestRequestTypeDef = TypedDict(
    "_RequiredCreateInstancesRequestRequestTypeDef",
    {
        "instanceNames": Sequence[str],
        "availabilityZone": str,
        "blueprintId": str,
        "bundleId": str,
    },
)
_OptionalCreateInstancesRequestRequestTypeDef = TypedDict(
    "_OptionalCreateInstancesRequestRequestTypeDef",
    {
        "customImageName": str,
        "userData": str,
        "keyPairName": str,
        "tags": Sequence[TagTypeDef],
        "addOns": Sequence[AddOnRequestTypeDef],
        "ipAddressType": IpAddressTypeType,
    },
    total=False,
)


class CreateInstancesRequestRequestTypeDef(
    _RequiredCreateInstancesRequestRequestTypeDef, _OptionalCreateInstancesRequestRequestTypeDef
):
    pass


EnableAddOnRequestRequestTypeDef = TypedDict(
    "EnableAddOnRequestRequestTypeDef",
    {
        "resourceName": str,
        "addOnRequest": AddOnRequestTypeDef,
    },
)

GetAlarmsResultTypeDef = TypedDict(
    "GetAlarmsResultTypeDef",
    {
        "alarms": List[AlarmTypeDef],
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetContactMethodsResultTypeDef = TypedDict(
    "GetContactMethodsResultTypeDef",
    {
        "contactMethods": List[ContactMethodTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AllocateStaticIpResultTypeDef = TypedDict(
    "AllocateStaticIpResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AttachCertificateToDistributionResultTypeDef = TypedDict(
    "AttachCertificateToDistributionResultTypeDef",
    {
        "operation": OperationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AttachDiskResultTypeDef = TypedDict(
    "AttachDiskResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AttachInstancesToLoadBalancerResultTypeDef = TypedDict(
    "AttachInstancesToLoadBalancerResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AttachLoadBalancerTlsCertificateResultTypeDef = TypedDict(
    "AttachLoadBalancerTlsCertificateResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AttachStaticIpResultTypeDef = TypedDict(
    "AttachStaticIpResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CloseInstancePublicPortsResultTypeDef = TypedDict(
    "CloseInstancePublicPortsResultTypeDef",
    {
        "operation": OperationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CopySnapshotResultTypeDef = TypedDict(
    "CopySnapshotResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateBucketAccessKeyResultTypeDef = TypedDict(
    "CreateBucketAccessKeyResultTypeDef",
    {
        "accessKey": AccessKeyTypeDef,
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateCloudFormationStackResultTypeDef = TypedDict(
    "CreateCloudFormationStackResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateContactMethodResultTypeDef = TypedDict(
    "CreateContactMethodResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateDiskFromSnapshotResultTypeDef = TypedDict(
    "CreateDiskFromSnapshotResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateDiskResultTypeDef = TypedDict(
    "CreateDiskResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateDiskSnapshotResultTypeDef = TypedDict(
    "CreateDiskSnapshotResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateDomainEntryResultTypeDef = TypedDict(
    "CreateDomainEntryResultTypeDef",
    {
        "operation": OperationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateDomainResultTypeDef = TypedDict(
    "CreateDomainResultTypeDef",
    {
        "operation": OperationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateInstanceSnapshotResultTypeDef = TypedDict(
    "CreateInstanceSnapshotResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateInstancesFromSnapshotResultTypeDef = TypedDict(
    "CreateInstancesFromSnapshotResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateInstancesResultTypeDef = TypedDict(
    "CreateInstancesResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateLoadBalancerResultTypeDef = TypedDict(
    "CreateLoadBalancerResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateLoadBalancerTlsCertificateResultTypeDef = TypedDict(
    "CreateLoadBalancerTlsCertificateResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateRelationalDatabaseFromSnapshotResultTypeDef = TypedDict(
    "CreateRelationalDatabaseFromSnapshotResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateRelationalDatabaseResultTypeDef = TypedDict(
    "CreateRelationalDatabaseResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateRelationalDatabaseSnapshotResultTypeDef = TypedDict(
    "CreateRelationalDatabaseSnapshotResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteAlarmResultTypeDef = TypedDict(
    "DeleteAlarmResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteAutoSnapshotResultTypeDef = TypedDict(
    "DeleteAutoSnapshotResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteBucketAccessKeyResultTypeDef = TypedDict(
    "DeleteBucketAccessKeyResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteBucketResultTypeDef = TypedDict(
    "DeleteBucketResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteCertificateResultTypeDef = TypedDict(
    "DeleteCertificateResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteContactMethodResultTypeDef = TypedDict(
    "DeleteContactMethodResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteDiskResultTypeDef = TypedDict(
    "DeleteDiskResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteDiskSnapshotResultTypeDef = TypedDict(
    "DeleteDiskSnapshotResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteDistributionResultTypeDef = TypedDict(
    "DeleteDistributionResultTypeDef",
    {
        "operation": OperationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteDomainEntryResultTypeDef = TypedDict(
    "DeleteDomainEntryResultTypeDef",
    {
        "operation": OperationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteDomainResultTypeDef = TypedDict(
    "DeleteDomainResultTypeDef",
    {
        "operation": OperationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteInstanceResultTypeDef = TypedDict(
    "DeleteInstanceResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteInstanceSnapshotResultTypeDef = TypedDict(
    "DeleteInstanceSnapshotResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteKeyPairResultTypeDef = TypedDict(
    "DeleteKeyPairResultTypeDef",
    {
        "operation": OperationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteKnownHostKeysResultTypeDef = TypedDict(
    "DeleteKnownHostKeysResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteLoadBalancerResultTypeDef = TypedDict(
    "DeleteLoadBalancerResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteLoadBalancerTlsCertificateResultTypeDef = TypedDict(
    "DeleteLoadBalancerTlsCertificateResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteRelationalDatabaseResultTypeDef = TypedDict(
    "DeleteRelationalDatabaseResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteRelationalDatabaseSnapshotResultTypeDef = TypedDict(
    "DeleteRelationalDatabaseSnapshotResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DetachCertificateFromDistributionResultTypeDef = TypedDict(
    "DetachCertificateFromDistributionResultTypeDef",
    {
        "operation": OperationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DetachDiskResultTypeDef = TypedDict(
    "DetachDiskResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DetachInstancesFromLoadBalancerResultTypeDef = TypedDict(
    "DetachInstancesFromLoadBalancerResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DetachStaticIpResultTypeDef = TypedDict(
    "DetachStaticIpResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisableAddOnResultTypeDef = TypedDict(
    "DisableAddOnResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EnableAddOnResultTypeDef = TypedDict(
    "EnableAddOnResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ExportSnapshotResultTypeDef = TypedDict(
    "ExportSnapshotResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetOperationResultTypeDef = TypedDict(
    "GetOperationResultTypeDef",
    {
        "operation": OperationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetOperationsForResourceResultTypeDef = TypedDict(
    "GetOperationsForResourceResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "nextPageCount": str,
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetOperationsResultTypeDef = TypedDict(
    "GetOperationsResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ImportKeyPairResultTypeDef = TypedDict(
    "ImportKeyPairResultTypeDef",
    {
        "operation": OperationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

OpenInstancePublicPortsResultTypeDef = TypedDict(
    "OpenInstancePublicPortsResultTypeDef",
    {
        "operation": OperationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PeerVpcResultTypeDef = TypedDict(
    "PeerVpcResultTypeDef",
    {
        "operation": OperationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PutAlarmResultTypeDef = TypedDict(
    "PutAlarmResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PutInstancePublicPortsResultTypeDef = TypedDict(
    "PutInstancePublicPortsResultTypeDef",
    {
        "operation": OperationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RebootInstanceResultTypeDef = TypedDict(
    "RebootInstanceResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RebootRelationalDatabaseResultTypeDef = TypedDict(
    "RebootRelationalDatabaseResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ReleaseStaticIpResultTypeDef = TypedDict(
    "ReleaseStaticIpResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ResetDistributionCacheResultTypeDef = TypedDict(
    "ResetDistributionCacheResultTypeDef",
    {
        "status": str,
        "createTime": datetime,
        "operation": OperationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SendContactMethodVerificationResultTypeDef = TypedDict(
    "SendContactMethodVerificationResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SetIpAddressTypeResultTypeDef = TypedDict(
    "SetIpAddressTypeResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SetResourceAccessForBucketResultTypeDef = TypedDict(
    "SetResourceAccessForBucketResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartInstanceResultTypeDef = TypedDict(
    "StartInstanceResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartRelationalDatabaseResultTypeDef = TypedDict(
    "StartRelationalDatabaseResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StopInstanceResultTypeDef = TypedDict(
    "StopInstanceResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StopRelationalDatabaseResultTypeDef = TypedDict(
    "StopRelationalDatabaseResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TagResourceResultTypeDef = TypedDict(
    "TagResourceResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TestAlarmResultTypeDef = TypedDict(
    "TestAlarmResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UnpeerVpcResultTypeDef = TypedDict(
    "UnpeerVpcResultTypeDef",
    {
        "operation": OperationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UntagResourceResultTypeDef = TypedDict(
    "UntagResourceResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateBucketBundleResultTypeDef = TypedDict(
    "UpdateBucketBundleResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateDistributionBundleResultTypeDef = TypedDict(
    "UpdateDistributionBundleResultTypeDef",
    {
        "operation": OperationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateDistributionResultTypeDef = TypedDict(
    "UpdateDistributionResultTypeDef",
    {
        "operation": OperationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateDomainEntryResultTypeDef = TypedDict(
    "UpdateDomainEntryResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateLoadBalancerAttributeResultTypeDef = TypedDict(
    "UpdateLoadBalancerAttributeResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateRelationalDatabaseParametersResultTypeDef = TypedDict(
    "UpdateRelationalDatabaseParametersResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateRelationalDatabaseResultTypeDef = TypedDict(
    "UpdateRelationalDatabaseResultTypeDef",
    {
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetStaticIpResultTypeDef = TypedDict(
    "GetStaticIpResultTypeDef",
    {
        "staticIp": StaticIpTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetStaticIpsResultTypeDef = TypedDict(
    "GetStaticIpsResultTypeDef",
    {
        "staticIps": List[StaticIpTypeDef],
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetAutoSnapshotsResultTypeDef = TypedDict(
    "GetAutoSnapshotsResultTypeDef",
    {
        "resourceName": str,
        "resourceType": ResourceTypeType,
        "autoSnapshots": List[AutoSnapshotDetailsTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetRegionsResultTypeDef = TypedDict(
    "GetRegionsResultTypeDef",
    {
        "regions": List[RegionTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateBucketResultTypeDef = TypedDict(
    "CreateBucketResultTypeDef",
    {
        "bucket": BucketTypeDef,
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetBucketsResultTypeDef = TypedDict(
    "GetBucketsResultTypeDef",
    {
        "buckets": List[BucketTypeDef],
        "nextPageToken": str,
        "accountLevelBpaSync": AccountLevelBpaSyncTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateBucketResultTypeDef = TypedDict(
    "UpdateBucketResultTypeDef",
    {
        "bucket": BucketTypeDef,
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetDiskSnapshotResultTypeDef = TypedDict(
    "GetDiskSnapshotResultTypeDef",
    {
        "diskSnapshot": DiskSnapshotTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetDiskSnapshotsResultTypeDef = TypedDict(
    "GetDiskSnapshotsResultTypeDef",
    {
        "diskSnapshots": List[DiskSnapshotTypeDef],
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetDiskResultTypeDef = TypedDict(
    "GetDiskResultTypeDef",
    {
        "disk": DiskTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetDisksResultTypeDef = TypedDict(
    "GetDisksResultTypeDef",
    {
        "disks": List[DiskTypeDef],
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

InstanceHardwareTypeDef = TypedDict(
    "InstanceHardwareTypeDef",
    {
        "cpuCount": int,
        "disks": List[DiskTypeDef],
        "ramSizeInGb": float,
    },
    total=False,
)

InstanceSnapshotTypeDef = TypedDict(
    "InstanceSnapshotTypeDef",
    {
        "name": str,
        "arn": str,
        "supportCode": str,
        "createdAt": datetime,
        "location": ResourceLocationTypeDef,
        "resourceType": ResourceTypeType,
        "tags": List[TagTypeDef],
        "state": InstanceSnapshotStateType,
        "progress": str,
        "fromAttachedDisks": List[DiskTypeDef],
        "fromInstanceName": str,
        "fromInstanceArn": str,
        "fromBlueprintId": str,
        "fromBundleId": str,
        "isFromAutoSnapshot": bool,
        "sizeInGb": int,
    },
    total=False,
)

CreateKeyPairResultTypeDef = TypedDict(
    "CreateKeyPairResultTypeDef",
    {
        "keyPair": KeyPairTypeDef,
        "publicKeyBase64": str,
        "privateKeyBase64": str,
        "operation": OperationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetKeyPairResultTypeDef = TypedDict(
    "GetKeyPairResultTypeDef",
    {
        "keyPair": KeyPairTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetKeyPairsResultTypeDef = TypedDict(
    "GetKeyPairsResultTypeDef",
    {
        "keyPairs": List[KeyPairTypeDef],
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetRelationalDatabaseSnapshotResultTypeDef = TypedDict(
    "GetRelationalDatabaseSnapshotResultTypeDef",
    {
        "relationalDatabaseSnapshot": RelationalDatabaseSnapshotTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetRelationalDatabaseSnapshotsResultTypeDef = TypedDict(
    "GetRelationalDatabaseSnapshotsResultTypeDef",
    {
        "relationalDatabaseSnapshots": List[RelationalDatabaseSnapshotTypeDef],
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredCreateDistributionRequestRequestTypeDef = TypedDict(
    "_RequiredCreateDistributionRequestRequestTypeDef",
    {
        "distributionName": str,
        "origin": InputOriginTypeDef,
        "defaultCacheBehavior": CacheBehaviorTypeDef,
        "bundleId": str,
    },
)
_OptionalCreateDistributionRequestRequestTypeDef = TypedDict(
    "_OptionalCreateDistributionRequestRequestTypeDef",
    {
        "cacheBehaviorSettings": CacheSettingsTypeDef,
        "cacheBehaviors": Sequence[CacheBehaviorPerPathTypeDef],
        "ipAddressType": IpAddressTypeType,
        "tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateDistributionRequestRequestTypeDef(
    _RequiredCreateDistributionRequestRequestTypeDef,
    _OptionalCreateDistributionRequestRequestTypeDef,
):
    pass


LightsailDistributionTypeDef = TypedDict(
    "LightsailDistributionTypeDef",
    {
        "name": str,
        "arn": str,
        "supportCode": str,
        "createdAt": datetime,
        "location": ResourceLocationTypeDef,
        "resourceType": ResourceTypeType,
        "alternativeDomainNames": List[str],
        "status": str,
        "isEnabled": bool,
        "domainName": str,
        "bundleId": str,
        "certificateName": str,
        "origin": OriginTypeDef,
        "originPublicDNS": str,
        "defaultCacheBehavior": CacheBehaviorTypeDef,
        "cacheBehaviorSettings": CacheSettingsTypeDef,
        "cacheBehaviors": List[CacheBehaviorPerPathTypeDef],
        "ableToUpdateBundle": bool,
        "ipAddressType": IpAddressTypeType,
        "tags": List[TagTypeDef],
    },
    total=False,
)

_RequiredUpdateDistributionRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateDistributionRequestRequestTypeDef",
    {
        "distributionName": str,
    },
)
_OptionalUpdateDistributionRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateDistributionRequestRequestTypeDef",
    {
        "origin": InputOriginTypeDef,
        "defaultCacheBehavior": CacheBehaviorTypeDef,
        "cacheBehaviorSettings": CacheSettingsTypeDef,
        "cacheBehaviors": Sequence[CacheBehaviorPerPathTypeDef],
        "isEnabled": bool,
    },
    total=False,
)


class UpdateDistributionRequestRequestTypeDef(
    _RequiredUpdateDistributionRequestRequestTypeDef,
    _OptionalUpdateDistributionRequestRequestTypeDef,
):
    pass


GetCloudFormationStackRecordsResultTypeDef = TypedDict(
    "GetCloudFormationStackRecordsResultTypeDef",
    {
        "cloudFormationStackRecords": List[CloudFormationStackRecordTypeDef],
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredUpdateContainerServiceRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateContainerServiceRequestRequestTypeDef",
    {
        "serviceName": str,
    },
)
_OptionalUpdateContainerServiceRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateContainerServiceRequestRequestTypeDef",
    {
        "power": ContainerServicePowerNameType,
        "scale": int,
        "isDisabled": bool,
        "publicDomainNames": Mapping[str, Sequence[str]],
        "privateRegistryAccess": PrivateRegistryAccessRequestTypeDef,
    },
    total=False,
)


class UpdateContainerServiceRequestRequestTypeDef(
    _RequiredUpdateContainerServiceRequestRequestTypeDef,
    _OptionalUpdateContainerServiceRequestRequestTypeDef,
):
    pass


ContainerServiceDeploymentTypeDef = TypedDict(
    "ContainerServiceDeploymentTypeDef",
    {
        "version": int,
        "state": ContainerServiceDeploymentStateType,
        "containers": Dict[str, ContainerTypeDef],
        "publicEndpoint": ContainerServiceEndpointTypeDef,
        "createdAt": datetime,
    },
    total=False,
)

ContainerServiceDeploymentRequestTypeDef = TypedDict(
    "ContainerServiceDeploymentRequestTypeDef",
    {
        "containers": Mapping[str, ContainerTypeDef],
        "publicEndpoint": EndpointRequestTypeDef,
    },
    total=False,
)

_RequiredCreateContainerServiceDeploymentRequestRequestTypeDef = TypedDict(
    "_RequiredCreateContainerServiceDeploymentRequestRequestTypeDef",
    {
        "serviceName": str,
    },
)
_OptionalCreateContainerServiceDeploymentRequestRequestTypeDef = TypedDict(
    "_OptionalCreateContainerServiceDeploymentRequestRequestTypeDef",
    {
        "containers": Mapping[str, ContainerTypeDef],
        "publicEndpoint": EndpointRequestTypeDef,
    },
    total=False,
)


class CreateContainerServiceDeploymentRequestRequestTypeDef(
    _RequiredCreateContainerServiceDeploymentRequestRequestTypeDef,
    _OptionalCreateContainerServiceDeploymentRequestRequestTypeDef,
):
    pass


GetDomainResultTypeDef = TypedDict(
    "GetDomainResultTypeDef",
    {
        "domain": DomainTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetDomainsResultTypeDef = TypedDict(
    "GetDomainsResultTypeDef",
    {
        "domains": List[DomainTypeDef],
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ExportSnapshotRecordSourceInfoTypeDef = TypedDict(
    "ExportSnapshotRecordSourceInfoTypeDef",
    {
        "resourceType": ExportSnapshotRecordSourceTypeType,
        "createdAt": datetime,
        "name": str,
        "arn": str,
        "fromResourceName": str,
        "fromResourceArn": str,
        "instanceSnapshotInfo": InstanceSnapshotInfoTypeDef,
        "diskSnapshotInfo": DiskSnapshotInfoTypeDef,
    },
    total=False,
)

RenewalSummaryTypeDef = TypedDict(
    "RenewalSummaryTypeDef",
    {
        "domainValidationRecords": List[DomainValidationRecordTypeDef],
        "renewalStatus": RenewalStatusType,
        "renewalStatusReason": str,
        "updatedAt": datetime,
    },
    total=False,
)

GetInstanceAccessDetailsResultTypeDef = TypedDict(
    "GetInstanceAccessDetailsResultTypeDef",
    {
        "accessDetails": InstanceAccessDetailsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

LoadBalancerTlsCertificateTypeDef = TypedDict(
    "LoadBalancerTlsCertificateTypeDef",
    {
        "name": str,
        "arn": str,
        "supportCode": str,
        "createdAt": datetime,
        "location": ResourceLocationTypeDef,
        "resourceType": ResourceTypeType,
        "tags": List[TagTypeDef],
        "loadBalancerName": str,
        "isAttached": bool,
        "status": LoadBalancerTlsCertificateStatusType,
        "domainName": str,
        "domainValidationRecords": List[LoadBalancerTlsCertificateDomainValidationRecordTypeDef],
        "failureReason": LoadBalancerTlsCertificateFailureReasonType,
        "issuedAt": datetime,
        "issuer": str,
        "keyAlgorithm": str,
        "notAfter": datetime,
        "notBefore": datetime,
        "renewalSummary": LoadBalancerTlsCertificateRenewalSummaryTypeDef,
        "revocationReason": LoadBalancerTlsCertificateRevocationReasonType,
        "revokedAt": datetime,
        "serial": str,
        "signatureAlgorithm": str,
        "subject": str,
        "subjectAlternativeNames": List[str],
    },
    total=False,
)

GetLoadBalancerResultTypeDef = TypedDict(
    "GetLoadBalancerResultTypeDef",
    {
        "loadBalancer": LoadBalancerTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetLoadBalancersResultTypeDef = TypedDict(
    "GetLoadBalancersResultTypeDef",
    {
        "loadBalancers": List[LoadBalancerTypeDef],
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetRelationalDatabaseResultTypeDef = TypedDict(
    "GetRelationalDatabaseResultTypeDef",
    {
        "relationalDatabase": RelationalDatabaseTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetRelationalDatabasesResultTypeDef = TypedDict(
    "GetRelationalDatabasesResultTypeDef",
    {
        "relationalDatabases": List[RelationalDatabaseTypeDef],
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

InstanceTypeDef = TypedDict(
    "InstanceTypeDef",
    {
        "name": str,
        "arn": str,
        "supportCode": str,
        "createdAt": datetime,
        "location": ResourceLocationTypeDef,
        "resourceType": ResourceTypeType,
        "tags": List[TagTypeDef],
        "blueprintId": str,
        "blueprintName": str,
        "bundleId": str,
        "addOns": List[AddOnTypeDef],
        "isStaticIp": bool,
        "privateIpAddress": str,
        "publicIpAddress": str,
        "ipv6Addresses": List[str],
        "ipAddressType": IpAddressTypeType,
        "hardware": InstanceHardwareTypeDef,
        "networking": InstanceNetworkingTypeDef,
        "state": InstanceStateTypeDef,
        "username": str,
        "sshKeyName": str,
    },
    total=False,
)

GetInstanceSnapshotResultTypeDef = TypedDict(
    "GetInstanceSnapshotResultTypeDef",
    {
        "instanceSnapshot": InstanceSnapshotTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetInstanceSnapshotsResultTypeDef = TypedDict(
    "GetInstanceSnapshotsResultTypeDef",
    {
        "instanceSnapshots": List[InstanceSnapshotTypeDef],
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateDistributionResultTypeDef = TypedDict(
    "CreateDistributionResultTypeDef",
    {
        "distribution": LightsailDistributionTypeDef,
        "operation": OperationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetDistributionsResultTypeDef = TypedDict(
    "GetDistributionsResultTypeDef",
    {
        "distributions": List[LightsailDistributionTypeDef],
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ContainerServiceTypeDef = TypedDict(
    "ContainerServiceTypeDef",
    {
        "containerServiceName": str,
        "arn": str,
        "createdAt": datetime,
        "location": ResourceLocationTypeDef,
        "resourceType": ResourceTypeType,
        "tags": List[TagTypeDef],
        "power": ContainerServicePowerNameType,
        "powerId": str,
        "state": ContainerServiceStateType,
        "stateDetail": ContainerServiceStateDetailTypeDef,
        "scale": int,
        "currentDeployment": ContainerServiceDeploymentTypeDef,
        "nextDeployment": ContainerServiceDeploymentTypeDef,
        "isDisabled": bool,
        "principalArn": str,
        "privateDomainName": str,
        "publicDomainNames": Dict[str, List[str]],
        "url": str,
        "privateRegistryAccess": PrivateRegistryAccessTypeDef,
    },
    total=False,
)

GetContainerServiceDeploymentsResultTypeDef = TypedDict(
    "GetContainerServiceDeploymentsResultTypeDef",
    {
        "deployments": List[ContainerServiceDeploymentTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredCreateContainerServiceRequestRequestTypeDef = TypedDict(
    "_RequiredCreateContainerServiceRequestRequestTypeDef",
    {
        "serviceName": str,
        "power": ContainerServicePowerNameType,
        "scale": int,
    },
)
_OptionalCreateContainerServiceRequestRequestTypeDef = TypedDict(
    "_OptionalCreateContainerServiceRequestRequestTypeDef",
    {
        "tags": Sequence[TagTypeDef],
        "publicDomainNames": Mapping[str, Sequence[str]],
        "deployment": ContainerServiceDeploymentRequestTypeDef,
        "privateRegistryAccess": PrivateRegistryAccessRequestTypeDef,
    },
    total=False,
)


class CreateContainerServiceRequestRequestTypeDef(
    _RequiredCreateContainerServiceRequestRequestTypeDef,
    _OptionalCreateContainerServiceRequestRequestTypeDef,
):
    pass


ExportSnapshotRecordTypeDef = TypedDict(
    "ExportSnapshotRecordTypeDef",
    {
        "name": str,
        "arn": str,
        "createdAt": datetime,
        "location": ResourceLocationTypeDef,
        "resourceType": ResourceTypeType,
        "state": RecordStateType,
        "sourceInfo": ExportSnapshotRecordSourceInfoTypeDef,
        "destinationInfo": DestinationInfoTypeDef,
    },
    total=False,
)

CertificateTypeDef = TypedDict(
    "CertificateTypeDef",
    {
        "arn": str,
        "name": str,
        "domainName": str,
        "status": CertificateStatusType,
        "serialNumber": str,
        "subjectAlternativeNames": List[str],
        "domainValidationRecords": List[DomainValidationRecordTypeDef],
        "requestFailureReason": str,
        "inUseResourceCount": int,
        "keyAlgorithm": str,
        "createdAt": datetime,
        "issuedAt": datetime,
        "issuerCA": str,
        "notBefore": datetime,
        "notAfter": datetime,
        "eligibleToRenew": str,
        "renewalSummary": RenewalSummaryTypeDef,
        "revokedAt": datetime,
        "revocationReason": str,
        "tags": List[TagTypeDef],
        "supportCode": str,
    },
    total=False,
)

GetLoadBalancerTlsCertificatesResultTypeDef = TypedDict(
    "GetLoadBalancerTlsCertificatesResultTypeDef",
    {
        "tlsCertificates": List[LoadBalancerTlsCertificateTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetInstanceResultTypeDef = TypedDict(
    "GetInstanceResultTypeDef",
    {
        "instance": InstanceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetInstancesResultTypeDef = TypedDict(
    "GetInstancesResultTypeDef",
    {
        "instances": List[InstanceTypeDef],
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ContainerServicesListResultTypeDef = TypedDict(
    "ContainerServicesListResultTypeDef",
    {
        "containerServices": List[ContainerServiceTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateContainerServiceDeploymentResultTypeDef = TypedDict(
    "CreateContainerServiceDeploymentResultTypeDef",
    {
        "containerService": ContainerServiceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateContainerServiceResultTypeDef = TypedDict(
    "CreateContainerServiceResultTypeDef",
    {
        "containerService": ContainerServiceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateContainerServiceResultTypeDef = TypedDict(
    "UpdateContainerServiceResultTypeDef",
    {
        "containerService": ContainerServiceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetExportSnapshotRecordsResultTypeDef = TypedDict(
    "GetExportSnapshotRecordsResultTypeDef",
    {
        "exportSnapshotRecords": List[ExportSnapshotRecordTypeDef],
        "nextPageToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CertificateSummaryTypeDef = TypedDict(
    "CertificateSummaryTypeDef",
    {
        "certificateArn": str,
        "certificateName": str,
        "domainName": str,
        "certificateDetail": CertificateTypeDef,
        "tags": List[TagTypeDef],
    },
    total=False,
)

CreateCertificateResultTypeDef = TypedDict(
    "CreateCertificateResultTypeDef",
    {
        "certificate": CertificateSummaryTypeDef,
        "operations": List[OperationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetCertificatesResultTypeDef = TypedDict(
    "GetCertificatesResultTypeDef",
    {
        "certificates": List[CertificateSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
