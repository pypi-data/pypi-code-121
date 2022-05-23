"""
Type annotations for elasticache service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/type_defs/)

Usage::

    ```python
    from mypy_boto3_elasticache.type_defs import TagTypeDef

    data: TagTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Sequence, Union

from .literals import (
    AuthenticationTypeType,
    AuthTokenUpdateStatusType,
    AuthTokenUpdateStrategyTypeType,
    AutomaticFailoverStatusType,
    AZModeType,
    ChangeTypeType,
    DataTieringStatusType,
    DestinationTypeType,
    LogDeliveryConfigurationStatusType,
    LogFormatType,
    LogTypeType,
    MultiAZStatusType,
    NodeUpdateInitiatedByType,
    NodeUpdateStatusType,
    OutpostModeType,
    PendingAutomaticFailoverStatusType,
    ServiceUpdateSeverityType,
    ServiceUpdateStatusType,
    SlaMetType,
    SourceTypeType,
    UpdateActionStatusType,
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
    "TagTypeDef",
    "ResponseMetadataTypeDef",
    "AuthenticationTypeDef",
    "AuthorizeCacheSecurityGroupIngressMessageRequestTypeDef",
    "AvailabilityZoneTypeDef",
    "BatchApplyUpdateActionMessageRequestTypeDef",
    "BatchStopUpdateActionMessageRequestTypeDef",
    "CacheParameterGroupStatusTypeDef",
    "CacheSecurityGroupMembershipTypeDef",
    "EndpointTypeDef",
    "NotificationConfigurationTypeDef",
    "SecurityGroupMembershipTypeDef",
    "CacheEngineVersionTypeDef",
    "CacheNodeTypeSpecificValueTypeDef",
    "CacheNodeUpdateStatusTypeDef",
    "ParameterTypeDef",
    "CacheParameterGroupTypeDef",
    "EC2SecurityGroupTypeDef",
    "CloudWatchLogsDestinationDetailsTypeDef",
    "CompleteMigrationMessageRequestTypeDef",
    "ConfigureShardTypeDef",
    "CreateGlobalReplicationGroupMessageRequestTypeDef",
    "NodeGroupConfigurationTypeDef",
    "CustomerNodeEndpointTypeDef",
    "DecreaseNodeGroupsInGlobalReplicationGroupMessageRequestTypeDef",
    "DeleteCacheClusterMessageRequestTypeDef",
    "DeleteCacheParameterGroupMessageRequestTypeDef",
    "DeleteCacheSecurityGroupMessageRequestTypeDef",
    "DeleteCacheSubnetGroupMessageRequestTypeDef",
    "DeleteGlobalReplicationGroupMessageRequestTypeDef",
    "DeleteReplicationGroupMessageRequestTypeDef",
    "DeleteSnapshotMessageRequestTypeDef",
    "DeleteUserGroupMessageRequestTypeDef",
    "DeleteUserMessageRequestTypeDef",
    "WaiterConfigTypeDef",
    "PaginatorConfigTypeDef",
    "DescribeCacheClustersMessageRequestTypeDef",
    "DescribeCacheEngineVersionsMessageRequestTypeDef",
    "DescribeCacheParameterGroupsMessageRequestTypeDef",
    "DescribeCacheParametersMessageRequestTypeDef",
    "DescribeCacheSecurityGroupsMessageRequestTypeDef",
    "DescribeCacheSubnetGroupsMessageRequestTypeDef",
    "DescribeEngineDefaultParametersMessageRequestTypeDef",
    "DescribeEventsMessageRequestTypeDef",
    "DescribeGlobalReplicationGroupsMessageRequestTypeDef",
    "DescribeReplicationGroupsMessageRequestTypeDef",
    "DescribeReservedCacheNodesMessageRequestTypeDef",
    "DescribeReservedCacheNodesOfferingsMessageRequestTypeDef",
    "DescribeServiceUpdatesMessageRequestTypeDef",
    "DescribeSnapshotsMessageRequestTypeDef",
    "TimeRangeFilterTypeDef",
    "DescribeUserGroupsMessageRequestTypeDef",
    "FilterTypeDef",
    "KinesisFirehoseDestinationDetailsTypeDef",
    "DisassociateGlobalReplicationGroupMessageRequestTypeDef",
    "EventTypeDef",
    "FailoverGlobalReplicationGroupMessageRequestTypeDef",
    "GlobalNodeGroupTypeDef",
    "GlobalReplicationGroupInfoTypeDef",
    "GlobalReplicationGroupMemberTypeDef",
    "ListAllowedNodeTypeModificationsMessageRequestTypeDef",
    "ListTagsForResourceMessageRequestTypeDef",
    "ParameterNameValueTypeDef",
    "ModifyCacheSubnetGroupMessageRequestTypeDef",
    "ModifyGlobalReplicationGroupMessageRequestTypeDef",
    "ReshardingConfigurationTypeDef",
    "ModifyUserGroupMessageRequestTypeDef",
    "ModifyUserMessageRequestTypeDef",
    "NodeGroupMemberUpdateStatusTypeDef",
    "ProcessedUpdateActionTypeDef",
    "RebalanceSlotsInGlobalReplicationGroupMessageRequestTypeDef",
    "RebootCacheClusterMessageRequestTypeDef",
    "RecurringChargeTypeDef",
    "RemoveTagsFromResourceMessageRequestTypeDef",
    "UserGroupsUpdateStatusTypeDef",
    "SlotMigrationTypeDef",
    "RevokeCacheSecurityGroupIngressMessageRequestTypeDef",
    "ServiceUpdateTypeDef",
    "SubnetOutpostTypeDef",
    "TestFailoverMessageRequestTypeDef",
    "UnprocessedUpdateActionTypeDef",
    "UserGroupPendingChangesTypeDef",
    "AddTagsToResourceMessageRequestTypeDef",
    "CopySnapshotMessageRequestTypeDef",
    "CreateCacheParameterGroupMessageRequestTypeDef",
    "CreateCacheSecurityGroupMessageRequestTypeDef",
    "CreateCacheSubnetGroupMessageRequestTypeDef",
    "CreateSnapshotMessageRequestTypeDef",
    "CreateUserGroupMessageRequestTypeDef",
    "CreateUserMessageRequestTypeDef",
    "PurchaseReservedCacheNodesOfferingMessageRequestTypeDef",
    "AllowedNodeTypeModificationsMessageTypeDef",
    "CacheParameterGroupNameMessageTypeDef",
    "TagListMessageTypeDef",
    "UserResponseMetadataTypeDef",
    "UserTypeDef",
    "CacheNodeTypeDef",
    "NodeGroupMemberTypeDef",
    "CacheEngineVersionMessageTypeDef",
    "CacheNodeTypeSpecificParameterTypeDef",
    "CacheParameterGroupsMessageTypeDef",
    "CreateCacheParameterGroupResultTypeDef",
    "CacheSecurityGroupTypeDef",
    "DecreaseReplicaCountMessageRequestTypeDef",
    "IncreaseReplicaCountMessageRequestTypeDef",
    "NodeSnapshotTypeDef",
    "StartMigrationMessageRequestTypeDef",
    "DescribeCacheClustersMessageCacheClusterAvailableWaitTypeDef",
    "DescribeCacheClustersMessageCacheClusterDeletedWaitTypeDef",
    "DescribeReplicationGroupsMessageReplicationGroupAvailableWaitTypeDef",
    "DescribeReplicationGroupsMessageReplicationGroupDeletedWaitTypeDef",
    "DescribeCacheClustersMessageDescribeCacheClustersPaginateTypeDef",
    "DescribeCacheEngineVersionsMessageDescribeCacheEngineVersionsPaginateTypeDef",
    "DescribeCacheParameterGroupsMessageDescribeCacheParameterGroupsPaginateTypeDef",
    "DescribeCacheParametersMessageDescribeCacheParametersPaginateTypeDef",
    "DescribeCacheSecurityGroupsMessageDescribeCacheSecurityGroupsPaginateTypeDef",
    "DescribeCacheSubnetGroupsMessageDescribeCacheSubnetGroupsPaginateTypeDef",
    "DescribeEngineDefaultParametersMessageDescribeEngineDefaultParametersPaginateTypeDef",
    "DescribeEventsMessageDescribeEventsPaginateTypeDef",
    "DescribeGlobalReplicationGroupsMessageDescribeGlobalReplicationGroupsPaginateTypeDef",
    "DescribeReplicationGroupsMessageDescribeReplicationGroupsPaginateTypeDef",
    "DescribeReservedCacheNodesMessageDescribeReservedCacheNodesPaginateTypeDef",
    "DescribeReservedCacheNodesOfferingsMessageDescribeReservedCacheNodesOfferingsPaginateTypeDef",
    "DescribeServiceUpdatesMessageDescribeServiceUpdatesPaginateTypeDef",
    "DescribeSnapshotsMessageDescribeSnapshotsPaginateTypeDef",
    "DescribeUserGroupsMessageDescribeUserGroupsPaginateTypeDef",
    "DescribeUpdateActionsMessageDescribeUpdateActionsPaginateTypeDef",
    "DescribeUpdateActionsMessageRequestTypeDef",
    "DescribeUsersMessageDescribeUsersPaginateTypeDef",
    "DescribeUsersMessageRequestTypeDef",
    "DestinationDetailsTypeDef",
    "EventsMessageTypeDef",
    "GlobalReplicationGroupTypeDef",
    "ModifyCacheParameterGroupMessageRequestTypeDef",
    "ResetCacheParameterGroupMessageRequestTypeDef",
    "ModifyReplicationGroupShardConfigurationMessageRequestTypeDef",
    "RegionalConfigurationTypeDef",
    "NodeGroupUpdateStatusTypeDef",
    "ReservedCacheNodeTypeDef",
    "ReservedCacheNodesOfferingTypeDef",
    "ReshardingStatusTypeDef",
    "ServiceUpdatesMessageTypeDef",
    "SubnetTypeDef",
    "UpdateActionResultsMessageTypeDef",
    "UserGroupResponseMetadataTypeDef",
    "UserGroupTypeDef",
    "DescribeUsersResultTypeDef",
    "NodeGroupTypeDef",
    "CacheParameterGroupDetailsTypeDef",
    "EngineDefaultsTypeDef",
    "AuthorizeCacheSecurityGroupIngressResultTypeDef",
    "CacheSecurityGroupMessageTypeDef",
    "CreateCacheSecurityGroupResultTypeDef",
    "RevokeCacheSecurityGroupIngressResultTypeDef",
    "SnapshotTypeDef",
    "LogDeliveryConfigurationRequestTypeDef",
    "LogDeliveryConfigurationTypeDef",
    "PendingLogDeliveryConfigurationTypeDef",
    "CreateGlobalReplicationGroupResultTypeDef",
    "DecreaseNodeGroupsInGlobalReplicationGroupResultTypeDef",
    "DeleteGlobalReplicationGroupResultTypeDef",
    "DescribeGlobalReplicationGroupsResultTypeDef",
    "DisassociateGlobalReplicationGroupResultTypeDef",
    "FailoverGlobalReplicationGroupResultTypeDef",
    "IncreaseNodeGroupsInGlobalReplicationGroupResultTypeDef",
    "ModifyGlobalReplicationGroupResultTypeDef",
    "RebalanceSlotsInGlobalReplicationGroupResultTypeDef",
    "IncreaseNodeGroupsInGlobalReplicationGroupMessageRequestTypeDef",
    "UpdateActionTypeDef",
    "PurchaseReservedCacheNodesOfferingResultTypeDef",
    "ReservedCacheNodeMessageTypeDef",
    "ReservedCacheNodesOfferingMessageTypeDef",
    "CacheSubnetGroupTypeDef",
    "DescribeUserGroupsResultTypeDef",
    "DescribeEngineDefaultParametersResultTypeDef",
    "CopySnapshotResultTypeDef",
    "CreateSnapshotResultTypeDef",
    "DeleteSnapshotResultTypeDef",
    "DescribeSnapshotsListMessageTypeDef",
    "CreateCacheClusterMessageRequestTypeDef",
    "CreateReplicationGroupMessageRequestTypeDef",
    "ModifyCacheClusterMessageRequestTypeDef",
    "ModifyReplicationGroupMessageRequestTypeDef",
    "PendingModifiedValuesTypeDef",
    "ReplicationGroupPendingModifiedValuesTypeDef",
    "UpdateActionsMessageTypeDef",
    "CacheSubnetGroupMessageTypeDef",
    "CreateCacheSubnetGroupResultTypeDef",
    "ModifyCacheSubnetGroupResultTypeDef",
    "CacheClusterTypeDef",
    "ReplicationGroupTypeDef",
    "CacheClusterMessageTypeDef",
    "CreateCacheClusterResultTypeDef",
    "DeleteCacheClusterResultTypeDef",
    "ModifyCacheClusterResultTypeDef",
    "RebootCacheClusterResultTypeDef",
    "CompleteMigrationResponseTypeDef",
    "CreateReplicationGroupResultTypeDef",
    "DecreaseReplicaCountResultTypeDef",
    "DeleteReplicationGroupResultTypeDef",
    "IncreaseReplicaCountResultTypeDef",
    "ModifyReplicationGroupResultTypeDef",
    "ModifyReplicationGroupShardConfigurationResultTypeDef",
    "ReplicationGroupMessageTypeDef",
    "StartMigrationResponseTypeDef",
    "TestFailoverResultTypeDef",
)

TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": str,
    },
    total=False,
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

AuthenticationTypeDef = TypedDict(
    "AuthenticationTypeDef",
    {
        "Type": AuthenticationTypeType,
        "PasswordCount": int,
    },
    total=False,
)

AuthorizeCacheSecurityGroupIngressMessageRequestTypeDef = TypedDict(
    "AuthorizeCacheSecurityGroupIngressMessageRequestTypeDef",
    {
        "CacheSecurityGroupName": str,
        "EC2SecurityGroupName": str,
        "EC2SecurityGroupOwnerId": str,
    },
)

AvailabilityZoneTypeDef = TypedDict(
    "AvailabilityZoneTypeDef",
    {
        "Name": str,
    },
    total=False,
)

_RequiredBatchApplyUpdateActionMessageRequestTypeDef = TypedDict(
    "_RequiredBatchApplyUpdateActionMessageRequestTypeDef",
    {
        "ServiceUpdateName": str,
    },
)
_OptionalBatchApplyUpdateActionMessageRequestTypeDef = TypedDict(
    "_OptionalBatchApplyUpdateActionMessageRequestTypeDef",
    {
        "ReplicationGroupIds": Sequence[str],
        "CacheClusterIds": Sequence[str],
    },
    total=False,
)


class BatchApplyUpdateActionMessageRequestTypeDef(
    _RequiredBatchApplyUpdateActionMessageRequestTypeDef,
    _OptionalBatchApplyUpdateActionMessageRequestTypeDef,
):
    pass


_RequiredBatchStopUpdateActionMessageRequestTypeDef = TypedDict(
    "_RequiredBatchStopUpdateActionMessageRequestTypeDef",
    {
        "ServiceUpdateName": str,
    },
)
_OptionalBatchStopUpdateActionMessageRequestTypeDef = TypedDict(
    "_OptionalBatchStopUpdateActionMessageRequestTypeDef",
    {
        "ReplicationGroupIds": Sequence[str],
        "CacheClusterIds": Sequence[str],
    },
    total=False,
)


class BatchStopUpdateActionMessageRequestTypeDef(
    _RequiredBatchStopUpdateActionMessageRequestTypeDef,
    _OptionalBatchStopUpdateActionMessageRequestTypeDef,
):
    pass


CacheParameterGroupStatusTypeDef = TypedDict(
    "CacheParameterGroupStatusTypeDef",
    {
        "CacheParameterGroupName": str,
        "ParameterApplyStatus": str,
        "CacheNodeIdsToReboot": List[str],
    },
    total=False,
)

CacheSecurityGroupMembershipTypeDef = TypedDict(
    "CacheSecurityGroupMembershipTypeDef",
    {
        "CacheSecurityGroupName": str,
        "Status": str,
    },
    total=False,
)

EndpointTypeDef = TypedDict(
    "EndpointTypeDef",
    {
        "Address": str,
        "Port": int,
    },
    total=False,
)

NotificationConfigurationTypeDef = TypedDict(
    "NotificationConfigurationTypeDef",
    {
        "TopicArn": str,
        "TopicStatus": str,
    },
    total=False,
)

SecurityGroupMembershipTypeDef = TypedDict(
    "SecurityGroupMembershipTypeDef",
    {
        "SecurityGroupId": str,
        "Status": str,
    },
    total=False,
)

CacheEngineVersionTypeDef = TypedDict(
    "CacheEngineVersionTypeDef",
    {
        "Engine": str,
        "EngineVersion": str,
        "CacheParameterGroupFamily": str,
        "CacheEngineDescription": str,
        "CacheEngineVersionDescription": str,
    },
    total=False,
)

CacheNodeTypeSpecificValueTypeDef = TypedDict(
    "CacheNodeTypeSpecificValueTypeDef",
    {
        "CacheNodeType": str,
        "Value": str,
    },
    total=False,
)

CacheNodeUpdateStatusTypeDef = TypedDict(
    "CacheNodeUpdateStatusTypeDef",
    {
        "CacheNodeId": str,
        "NodeUpdateStatus": NodeUpdateStatusType,
        "NodeDeletionDate": datetime,
        "NodeUpdateStartDate": datetime,
        "NodeUpdateEndDate": datetime,
        "NodeUpdateInitiatedBy": NodeUpdateInitiatedByType,
        "NodeUpdateInitiatedDate": datetime,
        "NodeUpdateStatusModifiedDate": datetime,
    },
    total=False,
)

ParameterTypeDef = TypedDict(
    "ParameterTypeDef",
    {
        "ParameterName": str,
        "ParameterValue": str,
        "Description": str,
        "Source": str,
        "DataType": str,
        "AllowedValues": str,
        "IsModifiable": bool,
        "MinimumEngineVersion": str,
        "ChangeType": ChangeTypeType,
    },
    total=False,
)

CacheParameterGroupTypeDef = TypedDict(
    "CacheParameterGroupTypeDef",
    {
        "CacheParameterGroupName": str,
        "CacheParameterGroupFamily": str,
        "Description": str,
        "IsGlobal": bool,
        "ARN": str,
    },
    total=False,
)

EC2SecurityGroupTypeDef = TypedDict(
    "EC2SecurityGroupTypeDef",
    {
        "Status": str,
        "EC2SecurityGroupName": str,
        "EC2SecurityGroupOwnerId": str,
    },
    total=False,
)

CloudWatchLogsDestinationDetailsTypeDef = TypedDict(
    "CloudWatchLogsDestinationDetailsTypeDef",
    {
        "LogGroup": str,
    },
    total=False,
)

_RequiredCompleteMigrationMessageRequestTypeDef = TypedDict(
    "_RequiredCompleteMigrationMessageRequestTypeDef",
    {
        "ReplicationGroupId": str,
    },
)
_OptionalCompleteMigrationMessageRequestTypeDef = TypedDict(
    "_OptionalCompleteMigrationMessageRequestTypeDef",
    {
        "Force": bool,
    },
    total=False,
)


class CompleteMigrationMessageRequestTypeDef(
    _RequiredCompleteMigrationMessageRequestTypeDef, _OptionalCompleteMigrationMessageRequestTypeDef
):
    pass


_RequiredConfigureShardTypeDef = TypedDict(
    "_RequiredConfigureShardTypeDef",
    {
        "NodeGroupId": str,
        "NewReplicaCount": int,
    },
)
_OptionalConfigureShardTypeDef = TypedDict(
    "_OptionalConfigureShardTypeDef",
    {
        "PreferredAvailabilityZones": Sequence[str],
        "PreferredOutpostArns": Sequence[str],
    },
    total=False,
)


class ConfigureShardTypeDef(_RequiredConfigureShardTypeDef, _OptionalConfigureShardTypeDef):
    pass


_RequiredCreateGlobalReplicationGroupMessageRequestTypeDef = TypedDict(
    "_RequiredCreateGlobalReplicationGroupMessageRequestTypeDef",
    {
        "GlobalReplicationGroupIdSuffix": str,
        "PrimaryReplicationGroupId": str,
    },
)
_OptionalCreateGlobalReplicationGroupMessageRequestTypeDef = TypedDict(
    "_OptionalCreateGlobalReplicationGroupMessageRequestTypeDef",
    {
        "GlobalReplicationGroupDescription": str,
    },
    total=False,
)


class CreateGlobalReplicationGroupMessageRequestTypeDef(
    _RequiredCreateGlobalReplicationGroupMessageRequestTypeDef,
    _OptionalCreateGlobalReplicationGroupMessageRequestTypeDef,
):
    pass


NodeGroupConfigurationTypeDef = TypedDict(
    "NodeGroupConfigurationTypeDef",
    {
        "NodeGroupId": str,
        "Slots": str,
        "ReplicaCount": int,
        "PrimaryAvailabilityZone": str,
        "ReplicaAvailabilityZones": List[str],
        "PrimaryOutpostArn": str,
        "ReplicaOutpostArns": List[str],
    },
    total=False,
)

CustomerNodeEndpointTypeDef = TypedDict(
    "CustomerNodeEndpointTypeDef",
    {
        "Address": str,
        "Port": int,
    },
    total=False,
)

_RequiredDecreaseNodeGroupsInGlobalReplicationGroupMessageRequestTypeDef = TypedDict(
    "_RequiredDecreaseNodeGroupsInGlobalReplicationGroupMessageRequestTypeDef",
    {
        "GlobalReplicationGroupId": str,
        "NodeGroupCount": int,
        "ApplyImmediately": bool,
    },
)
_OptionalDecreaseNodeGroupsInGlobalReplicationGroupMessageRequestTypeDef = TypedDict(
    "_OptionalDecreaseNodeGroupsInGlobalReplicationGroupMessageRequestTypeDef",
    {
        "GlobalNodeGroupsToRemove": Sequence[str],
        "GlobalNodeGroupsToRetain": Sequence[str],
    },
    total=False,
)


class DecreaseNodeGroupsInGlobalReplicationGroupMessageRequestTypeDef(
    _RequiredDecreaseNodeGroupsInGlobalReplicationGroupMessageRequestTypeDef,
    _OptionalDecreaseNodeGroupsInGlobalReplicationGroupMessageRequestTypeDef,
):
    pass


_RequiredDeleteCacheClusterMessageRequestTypeDef = TypedDict(
    "_RequiredDeleteCacheClusterMessageRequestTypeDef",
    {
        "CacheClusterId": str,
    },
)
_OptionalDeleteCacheClusterMessageRequestTypeDef = TypedDict(
    "_OptionalDeleteCacheClusterMessageRequestTypeDef",
    {
        "FinalSnapshotIdentifier": str,
    },
    total=False,
)


class DeleteCacheClusterMessageRequestTypeDef(
    _RequiredDeleteCacheClusterMessageRequestTypeDef,
    _OptionalDeleteCacheClusterMessageRequestTypeDef,
):
    pass


DeleteCacheParameterGroupMessageRequestTypeDef = TypedDict(
    "DeleteCacheParameterGroupMessageRequestTypeDef",
    {
        "CacheParameterGroupName": str,
    },
)

DeleteCacheSecurityGroupMessageRequestTypeDef = TypedDict(
    "DeleteCacheSecurityGroupMessageRequestTypeDef",
    {
        "CacheSecurityGroupName": str,
    },
)

DeleteCacheSubnetGroupMessageRequestTypeDef = TypedDict(
    "DeleteCacheSubnetGroupMessageRequestTypeDef",
    {
        "CacheSubnetGroupName": str,
    },
)

DeleteGlobalReplicationGroupMessageRequestTypeDef = TypedDict(
    "DeleteGlobalReplicationGroupMessageRequestTypeDef",
    {
        "GlobalReplicationGroupId": str,
        "RetainPrimaryReplicationGroup": bool,
    },
)

_RequiredDeleteReplicationGroupMessageRequestTypeDef = TypedDict(
    "_RequiredDeleteReplicationGroupMessageRequestTypeDef",
    {
        "ReplicationGroupId": str,
    },
)
_OptionalDeleteReplicationGroupMessageRequestTypeDef = TypedDict(
    "_OptionalDeleteReplicationGroupMessageRequestTypeDef",
    {
        "RetainPrimaryCluster": bool,
        "FinalSnapshotIdentifier": str,
    },
    total=False,
)


class DeleteReplicationGroupMessageRequestTypeDef(
    _RequiredDeleteReplicationGroupMessageRequestTypeDef,
    _OptionalDeleteReplicationGroupMessageRequestTypeDef,
):
    pass


DeleteSnapshotMessageRequestTypeDef = TypedDict(
    "DeleteSnapshotMessageRequestTypeDef",
    {
        "SnapshotName": str,
    },
)

DeleteUserGroupMessageRequestTypeDef = TypedDict(
    "DeleteUserGroupMessageRequestTypeDef",
    {
        "UserGroupId": str,
    },
)

DeleteUserMessageRequestTypeDef = TypedDict(
    "DeleteUserMessageRequestTypeDef",
    {
        "UserId": str,
    },
)

WaiterConfigTypeDef = TypedDict(
    "WaiterConfigTypeDef",
    {
        "Delay": int,
        "MaxAttempts": int,
    },
    total=False,
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

DescribeCacheClustersMessageRequestTypeDef = TypedDict(
    "DescribeCacheClustersMessageRequestTypeDef",
    {
        "CacheClusterId": str,
        "MaxRecords": int,
        "Marker": str,
        "ShowCacheNodeInfo": bool,
        "ShowCacheClustersNotInReplicationGroups": bool,
    },
    total=False,
)

DescribeCacheEngineVersionsMessageRequestTypeDef = TypedDict(
    "DescribeCacheEngineVersionsMessageRequestTypeDef",
    {
        "Engine": str,
        "EngineVersion": str,
        "CacheParameterGroupFamily": str,
        "MaxRecords": int,
        "Marker": str,
        "DefaultOnly": bool,
    },
    total=False,
)

DescribeCacheParameterGroupsMessageRequestTypeDef = TypedDict(
    "DescribeCacheParameterGroupsMessageRequestTypeDef",
    {
        "CacheParameterGroupName": str,
        "MaxRecords": int,
        "Marker": str,
    },
    total=False,
)

_RequiredDescribeCacheParametersMessageRequestTypeDef = TypedDict(
    "_RequiredDescribeCacheParametersMessageRequestTypeDef",
    {
        "CacheParameterGroupName": str,
    },
)
_OptionalDescribeCacheParametersMessageRequestTypeDef = TypedDict(
    "_OptionalDescribeCacheParametersMessageRequestTypeDef",
    {
        "Source": str,
        "MaxRecords": int,
        "Marker": str,
    },
    total=False,
)


class DescribeCacheParametersMessageRequestTypeDef(
    _RequiredDescribeCacheParametersMessageRequestTypeDef,
    _OptionalDescribeCacheParametersMessageRequestTypeDef,
):
    pass


DescribeCacheSecurityGroupsMessageRequestTypeDef = TypedDict(
    "DescribeCacheSecurityGroupsMessageRequestTypeDef",
    {
        "CacheSecurityGroupName": str,
        "MaxRecords": int,
        "Marker": str,
    },
    total=False,
)

DescribeCacheSubnetGroupsMessageRequestTypeDef = TypedDict(
    "DescribeCacheSubnetGroupsMessageRequestTypeDef",
    {
        "CacheSubnetGroupName": str,
        "MaxRecords": int,
        "Marker": str,
    },
    total=False,
)

_RequiredDescribeEngineDefaultParametersMessageRequestTypeDef = TypedDict(
    "_RequiredDescribeEngineDefaultParametersMessageRequestTypeDef",
    {
        "CacheParameterGroupFamily": str,
    },
)
_OptionalDescribeEngineDefaultParametersMessageRequestTypeDef = TypedDict(
    "_OptionalDescribeEngineDefaultParametersMessageRequestTypeDef",
    {
        "MaxRecords": int,
        "Marker": str,
    },
    total=False,
)


class DescribeEngineDefaultParametersMessageRequestTypeDef(
    _RequiredDescribeEngineDefaultParametersMessageRequestTypeDef,
    _OptionalDescribeEngineDefaultParametersMessageRequestTypeDef,
):
    pass


DescribeEventsMessageRequestTypeDef = TypedDict(
    "DescribeEventsMessageRequestTypeDef",
    {
        "SourceIdentifier": str,
        "SourceType": SourceTypeType,
        "StartTime": Union[datetime, str],
        "EndTime": Union[datetime, str],
        "Duration": int,
        "MaxRecords": int,
        "Marker": str,
    },
    total=False,
)

DescribeGlobalReplicationGroupsMessageRequestTypeDef = TypedDict(
    "DescribeGlobalReplicationGroupsMessageRequestTypeDef",
    {
        "GlobalReplicationGroupId": str,
        "MaxRecords": int,
        "Marker": str,
        "ShowMemberInfo": bool,
    },
    total=False,
)

DescribeReplicationGroupsMessageRequestTypeDef = TypedDict(
    "DescribeReplicationGroupsMessageRequestTypeDef",
    {
        "ReplicationGroupId": str,
        "MaxRecords": int,
        "Marker": str,
    },
    total=False,
)

DescribeReservedCacheNodesMessageRequestTypeDef = TypedDict(
    "DescribeReservedCacheNodesMessageRequestTypeDef",
    {
        "ReservedCacheNodeId": str,
        "ReservedCacheNodesOfferingId": str,
        "CacheNodeType": str,
        "Duration": str,
        "ProductDescription": str,
        "OfferingType": str,
        "MaxRecords": int,
        "Marker": str,
    },
    total=False,
)

DescribeReservedCacheNodesOfferingsMessageRequestTypeDef = TypedDict(
    "DescribeReservedCacheNodesOfferingsMessageRequestTypeDef",
    {
        "ReservedCacheNodesOfferingId": str,
        "CacheNodeType": str,
        "Duration": str,
        "ProductDescription": str,
        "OfferingType": str,
        "MaxRecords": int,
        "Marker": str,
    },
    total=False,
)

DescribeServiceUpdatesMessageRequestTypeDef = TypedDict(
    "DescribeServiceUpdatesMessageRequestTypeDef",
    {
        "ServiceUpdateName": str,
        "ServiceUpdateStatus": Sequence[ServiceUpdateStatusType],
        "MaxRecords": int,
        "Marker": str,
    },
    total=False,
)

DescribeSnapshotsMessageRequestTypeDef = TypedDict(
    "DescribeSnapshotsMessageRequestTypeDef",
    {
        "ReplicationGroupId": str,
        "CacheClusterId": str,
        "SnapshotName": str,
        "SnapshotSource": str,
        "Marker": str,
        "MaxRecords": int,
        "ShowNodeGroupConfig": bool,
    },
    total=False,
)

TimeRangeFilterTypeDef = TypedDict(
    "TimeRangeFilterTypeDef",
    {
        "StartTime": Union[datetime, str],
        "EndTime": Union[datetime, str],
    },
    total=False,
)

DescribeUserGroupsMessageRequestTypeDef = TypedDict(
    "DescribeUserGroupsMessageRequestTypeDef",
    {
        "UserGroupId": str,
        "MaxRecords": int,
        "Marker": str,
    },
    total=False,
)

FilterTypeDef = TypedDict(
    "FilterTypeDef",
    {
        "Name": str,
        "Values": Sequence[str],
    },
)

KinesisFirehoseDestinationDetailsTypeDef = TypedDict(
    "KinesisFirehoseDestinationDetailsTypeDef",
    {
        "DeliveryStream": str,
    },
    total=False,
)

DisassociateGlobalReplicationGroupMessageRequestTypeDef = TypedDict(
    "DisassociateGlobalReplicationGroupMessageRequestTypeDef",
    {
        "GlobalReplicationGroupId": str,
        "ReplicationGroupId": str,
        "ReplicationGroupRegion": str,
    },
)

EventTypeDef = TypedDict(
    "EventTypeDef",
    {
        "SourceIdentifier": str,
        "SourceType": SourceTypeType,
        "Message": str,
        "Date": datetime,
    },
    total=False,
)

FailoverGlobalReplicationGroupMessageRequestTypeDef = TypedDict(
    "FailoverGlobalReplicationGroupMessageRequestTypeDef",
    {
        "GlobalReplicationGroupId": str,
        "PrimaryRegion": str,
        "PrimaryReplicationGroupId": str,
    },
)

GlobalNodeGroupTypeDef = TypedDict(
    "GlobalNodeGroupTypeDef",
    {
        "GlobalNodeGroupId": str,
        "Slots": str,
    },
    total=False,
)

GlobalReplicationGroupInfoTypeDef = TypedDict(
    "GlobalReplicationGroupInfoTypeDef",
    {
        "GlobalReplicationGroupId": str,
        "GlobalReplicationGroupMemberRole": str,
    },
    total=False,
)

GlobalReplicationGroupMemberTypeDef = TypedDict(
    "GlobalReplicationGroupMemberTypeDef",
    {
        "ReplicationGroupId": str,
        "ReplicationGroupRegion": str,
        "Role": str,
        "AutomaticFailover": AutomaticFailoverStatusType,
        "Status": str,
    },
    total=False,
)

ListAllowedNodeTypeModificationsMessageRequestTypeDef = TypedDict(
    "ListAllowedNodeTypeModificationsMessageRequestTypeDef",
    {
        "CacheClusterId": str,
        "ReplicationGroupId": str,
    },
    total=False,
)

ListTagsForResourceMessageRequestTypeDef = TypedDict(
    "ListTagsForResourceMessageRequestTypeDef",
    {
        "ResourceName": str,
    },
)

ParameterNameValueTypeDef = TypedDict(
    "ParameterNameValueTypeDef",
    {
        "ParameterName": str,
        "ParameterValue": str,
    },
    total=False,
)

_RequiredModifyCacheSubnetGroupMessageRequestTypeDef = TypedDict(
    "_RequiredModifyCacheSubnetGroupMessageRequestTypeDef",
    {
        "CacheSubnetGroupName": str,
    },
)
_OptionalModifyCacheSubnetGroupMessageRequestTypeDef = TypedDict(
    "_OptionalModifyCacheSubnetGroupMessageRequestTypeDef",
    {
        "CacheSubnetGroupDescription": str,
        "SubnetIds": Sequence[str],
    },
    total=False,
)


class ModifyCacheSubnetGroupMessageRequestTypeDef(
    _RequiredModifyCacheSubnetGroupMessageRequestTypeDef,
    _OptionalModifyCacheSubnetGroupMessageRequestTypeDef,
):
    pass


_RequiredModifyGlobalReplicationGroupMessageRequestTypeDef = TypedDict(
    "_RequiredModifyGlobalReplicationGroupMessageRequestTypeDef",
    {
        "GlobalReplicationGroupId": str,
        "ApplyImmediately": bool,
    },
)
_OptionalModifyGlobalReplicationGroupMessageRequestTypeDef = TypedDict(
    "_OptionalModifyGlobalReplicationGroupMessageRequestTypeDef",
    {
        "CacheNodeType": str,
        "EngineVersion": str,
        "CacheParameterGroupName": str,
        "GlobalReplicationGroupDescription": str,
        "AutomaticFailoverEnabled": bool,
    },
    total=False,
)


class ModifyGlobalReplicationGroupMessageRequestTypeDef(
    _RequiredModifyGlobalReplicationGroupMessageRequestTypeDef,
    _OptionalModifyGlobalReplicationGroupMessageRequestTypeDef,
):
    pass


ReshardingConfigurationTypeDef = TypedDict(
    "ReshardingConfigurationTypeDef",
    {
        "NodeGroupId": str,
        "PreferredAvailabilityZones": Sequence[str],
    },
    total=False,
)

_RequiredModifyUserGroupMessageRequestTypeDef = TypedDict(
    "_RequiredModifyUserGroupMessageRequestTypeDef",
    {
        "UserGroupId": str,
    },
)
_OptionalModifyUserGroupMessageRequestTypeDef = TypedDict(
    "_OptionalModifyUserGroupMessageRequestTypeDef",
    {
        "UserIdsToAdd": Sequence[str],
        "UserIdsToRemove": Sequence[str],
    },
    total=False,
)


class ModifyUserGroupMessageRequestTypeDef(
    _RequiredModifyUserGroupMessageRequestTypeDef, _OptionalModifyUserGroupMessageRequestTypeDef
):
    pass


_RequiredModifyUserMessageRequestTypeDef = TypedDict(
    "_RequiredModifyUserMessageRequestTypeDef",
    {
        "UserId": str,
    },
)
_OptionalModifyUserMessageRequestTypeDef = TypedDict(
    "_OptionalModifyUserMessageRequestTypeDef",
    {
        "AccessString": str,
        "AppendAccessString": str,
        "Passwords": Sequence[str],
        "NoPasswordRequired": bool,
    },
    total=False,
)


class ModifyUserMessageRequestTypeDef(
    _RequiredModifyUserMessageRequestTypeDef, _OptionalModifyUserMessageRequestTypeDef
):
    pass


NodeGroupMemberUpdateStatusTypeDef = TypedDict(
    "NodeGroupMemberUpdateStatusTypeDef",
    {
        "CacheClusterId": str,
        "CacheNodeId": str,
        "NodeUpdateStatus": NodeUpdateStatusType,
        "NodeDeletionDate": datetime,
        "NodeUpdateStartDate": datetime,
        "NodeUpdateEndDate": datetime,
        "NodeUpdateInitiatedBy": NodeUpdateInitiatedByType,
        "NodeUpdateInitiatedDate": datetime,
        "NodeUpdateStatusModifiedDate": datetime,
    },
    total=False,
)

ProcessedUpdateActionTypeDef = TypedDict(
    "ProcessedUpdateActionTypeDef",
    {
        "ReplicationGroupId": str,
        "CacheClusterId": str,
        "ServiceUpdateName": str,
        "UpdateActionStatus": UpdateActionStatusType,
    },
    total=False,
)

RebalanceSlotsInGlobalReplicationGroupMessageRequestTypeDef = TypedDict(
    "RebalanceSlotsInGlobalReplicationGroupMessageRequestTypeDef",
    {
        "GlobalReplicationGroupId": str,
        "ApplyImmediately": bool,
    },
)

RebootCacheClusterMessageRequestTypeDef = TypedDict(
    "RebootCacheClusterMessageRequestTypeDef",
    {
        "CacheClusterId": str,
        "CacheNodeIdsToReboot": Sequence[str],
    },
)

RecurringChargeTypeDef = TypedDict(
    "RecurringChargeTypeDef",
    {
        "RecurringChargeAmount": float,
        "RecurringChargeFrequency": str,
    },
    total=False,
)

RemoveTagsFromResourceMessageRequestTypeDef = TypedDict(
    "RemoveTagsFromResourceMessageRequestTypeDef",
    {
        "ResourceName": str,
        "TagKeys": Sequence[str],
    },
)

UserGroupsUpdateStatusTypeDef = TypedDict(
    "UserGroupsUpdateStatusTypeDef",
    {
        "UserGroupIdsToAdd": List[str],
        "UserGroupIdsToRemove": List[str],
    },
    total=False,
)

SlotMigrationTypeDef = TypedDict(
    "SlotMigrationTypeDef",
    {
        "ProgressPercentage": float,
    },
    total=False,
)

RevokeCacheSecurityGroupIngressMessageRequestTypeDef = TypedDict(
    "RevokeCacheSecurityGroupIngressMessageRequestTypeDef",
    {
        "CacheSecurityGroupName": str,
        "EC2SecurityGroupName": str,
        "EC2SecurityGroupOwnerId": str,
    },
)

ServiceUpdateTypeDef = TypedDict(
    "ServiceUpdateTypeDef",
    {
        "ServiceUpdateName": str,
        "ServiceUpdateReleaseDate": datetime,
        "ServiceUpdateEndDate": datetime,
        "ServiceUpdateSeverity": ServiceUpdateSeverityType,
        "ServiceUpdateRecommendedApplyByDate": datetime,
        "ServiceUpdateStatus": ServiceUpdateStatusType,
        "ServiceUpdateDescription": str,
        "ServiceUpdateType": Literal["security-update"],
        "Engine": str,
        "EngineVersion": str,
        "AutoUpdateAfterRecommendedApplyByDate": bool,
        "EstimatedUpdateTime": str,
    },
    total=False,
)

SubnetOutpostTypeDef = TypedDict(
    "SubnetOutpostTypeDef",
    {
        "SubnetOutpostArn": str,
    },
    total=False,
)

TestFailoverMessageRequestTypeDef = TypedDict(
    "TestFailoverMessageRequestTypeDef",
    {
        "ReplicationGroupId": str,
        "NodeGroupId": str,
    },
)

UnprocessedUpdateActionTypeDef = TypedDict(
    "UnprocessedUpdateActionTypeDef",
    {
        "ReplicationGroupId": str,
        "CacheClusterId": str,
        "ServiceUpdateName": str,
        "ErrorType": str,
        "ErrorMessage": str,
    },
    total=False,
)

UserGroupPendingChangesTypeDef = TypedDict(
    "UserGroupPendingChangesTypeDef",
    {
        "UserIdsToRemove": List[str],
        "UserIdsToAdd": List[str],
    },
    total=False,
)

AddTagsToResourceMessageRequestTypeDef = TypedDict(
    "AddTagsToResourceMessageRequestTypeDef",
    {
        "ResourceName": str,
        "Tags": Sequence[TagTypeDef],
    },
)

_RequiredCopySnapshotMessageRequestTypeDef = TypedDict(
    "_RequiredCopySnapshotMessageRequestTypeDef",
    {
        "SourceSnapshotName": str,
        "TargetSnapshotName": str,
    },
)
_OptionalCopySnapshotMessageRequestTypeDef = TypedDict(
    "_OptionalCopySnapshotMessageRequestTypeDef",
    {
        "TargetBucket": str,
        "KmsKeyId": str,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CopySnapshotMessageRequestTypeDef(
    _RequiredCopySnapshotMessageRequestTypeDef, _OptionalCopySnapshotMessageRequestTypeDef
):
    pass


_RequiredCreateCacheParameterGroupMessageRequestTypeDef = TypedDict(
    "_RequiredCreateCacheParameterGroupMessageRequestTypeDef",
    {
        "CacheParameterGroupName": str,
        "CacheParameterGroupFamily": str,
        "Description": str,
    },
)
_OptionalCreateCacheParameterGroupMessageRequestTypeDef = TypedDict(
    "_OptionalCreateCacheParameterGroupMessageRequestTypeDef",
    {
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateCacheParameterGroupMessageRequestTypeDef(
    _RequiredCreateCacheParameterGroupMessageRequestTypeDef,
    _OptionalCreateCacheParameterGroupMessageRequestTypeDef,
):
    pass


_RequiredCreateCacheSecurityGroupMessageRequestTypeDef = TypedDict(
    "_RequiredCreateCacheSecurityGroupMessageRequestTypeDef",
    {
        "CacheSecurityGroupName": str,
        "Description": str,
    },
)
_OptionalCreateCacheSecurityGroupMessageRequestTypeDef = TypedDict(
    "_OptionalCreateCacheSecurityGroupMessageRequestTypeDef",
    {
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateCacheSecurityGroupMessageRequestTypeDef(
    _RequiredCreateCacheSecurityGroupMessageRequestTypeDef,
    _OptionalCreateCacheSecurityGroupMessageRequestTypeDef,
):
    pass


_RequiredCreateCacheSubnetGroupMessageRequestTypeDef = TypedDict(
    "_RequiredCreateCacheSubnetGroupMessageRequestTypeDef",
    {
        "CacheSubnetGroupName": str,
        "CacheSubnetGroupDescription": str,
        "SubnetIds": Sequence[str],
    },
)
_OptionalCreateCacheSubnetGroupMessageRequestTypeDef = TypedDict(
    "_OptionalCreateCacheSubnetGroupMessageRequestTypeDef",
    {
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateCacheSubnetGroupMessageRequestTypeDef(
    _RequiredCreateCacheSubnetGroupMessageRequestTypeDef,
    _OptionalCreateCacheSubnetGroupMessageRequestTypeDef,
):
    pass


_RequiredCreateSnapshotMessageRequestTypeDef = TypedDict(
    "_RequiredCreateSnapshotMessageRequestTypeDef",
    {
        "SnapshotName": str,
    },
)
_OptionalCreateSnapshotMessageRequestTypeDef = TypedDict(
    "_OptionalCreateSnapshotMessageRequestTypeDef",
    {
        "ReplicationGroupId": str,
        "CacheClusterId": str,
        "KmsKeyId": str,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateSnapshotMessageRequestTypeDef(
    _RequiredCreateSnapshotMessageRequestTypeDef, _OptionalCreateSnapshotMessageRequestTypeDef
):
    pass


_RequiredCreateUserGroupMessageRequestTypeDef = TypedDict(
    "_RequiredCreateUserGroupMessageRequestTypeDef",
    {
        "UserGroupId": str,
        "Engine": str,
    },
)
_OptionalCreateUserGroupMessageRequestTypeDef = TypedDict(
    "_OptionalCreateUserGroupMessageRequestTypeDef",
    {
        "UserIds": Sequence[str],
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateUserGroupMessageRequestTypeDef(
    _RequiredCreateUserGroupMessageRequestTypeDef, _OptionalCreateUserGroupMessageRequestTypeDef
):
    pass


_RequiredCreateUserMessageRequestTypeDef = TypedDict(
    "_RequiredCreateUserMessageRequestTypeDef",
    {
        "UserId": str,
        "UserName": str,
        "Engine": str,
        "AccessString": str,
    },
)
_OptionalCreateUserMessageRequestTypeDef = TypedDict(
    "_OptionalCreateUserMessageRequestTypeDef",
    {
        "Passwords": Sequence[str],
        "NoPasswordRequired": bool,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateUserMessageRequestTypeDef(
    _RequiredCreateUserMessageRequestTypeDef, _OptionalCreateUserMessageRequestTypeDef
):
    pass


_RequiredPurchaseReservedCacheNodesOfferingMessageRequestTypeDef = TypedDict(
    "_RequiredPurchaseReservedCacheNodesOfferingMessageRequestTypeDef",
    {
        "ReservedCacheNodesOfferingId": str,
    },
)
_OptionalPurchaseReservedCacheNodesOfferingMessageRequestTypeDef = TypedDict(
    "_OptionalPurchaseReservedCacheNodesOfferingMessageRequestTypeDef",
    {
        "ReservedCacheNodeId": str,
        "CacheNodeCount": int,
        "Tags": Sequence[TagTypeDef],
    },
    total=False,
)


class PurchaseReservedCacheNodesOfferingMessageRequestTypeDef(
    _RequiredPurchaseReservedCacheNodesOfferingMessageRequestTypeDef,
    _OptionalPurchaseReservedCacheNodesOfferingMessageRequestTypeDef,
):
    pass


AllowedNodeTypeModificationsMessageTypeDef = TypedDict(
    "AllowedNodeTypeModificationsMessageTypeDef",
    {
        "ScaleUpModifications": List[str],
        "ScaleDownModifications": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CacheParameterGroupNameMessageTypeDef = TypedDict(
    "CacheParameterGroupNameMessageTypeDef",
    {
        "CacheParameterGroupName": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TagListMessageTypeDef = TypedDict(
    "TagListMessageTypeDef",
    {
        "TagList": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UserResponseMetadataTypeDef = TypedDict(
    "UserResponseMetadataTypeDef",
    {
        "UserId": str,
        "UserName": str,
        "Status": str,
        "Engine": str,
        "MinimumEngineVersion": str,
        "AccessString": str,
        "UserGroupIds": List[str],
        "Authentication": AuthenticationTypeDef,
        "ARN": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UserTypeDef = TypedDict(
    "UserTypeDef",
    {
        "UserId": str,
        "UserName": str,
        "Status": str,
        "Engine": str,
        "MinimumEngineVersion": str,
        "AccessString": str,
        "UserGroupIds": List[str],
        "Authentication": AuthenticationTypeDef,
        "ARN": str,
    },
    total=False,
)

CacheNodeTypeDef = TypedDict(
    "CacheNodeTypeDef",
    {
        "CacheNodeId": str,
        "CacheNodeStatus": str,
        "CacheNodeCreateTime": datetime,
        "Endpoint": EndpointTypeDef,
        "ParameterGroupStatus": str,
        "SourceCacheNodeId": str,
        "CustomerAvailabilityZone": str,
        "CustomerOutpostArn": str,
    },
    total=False,
)

NodeGroupMemberTypeDef = TypedDict(
    "NodeGroupMemberTypeDef",
    {
        "CacheClusterId": str,
        "CacheNodeId": str,
        "ReadEndpoint": EndpointTypeDef,
        "PreferredAvailabilityZone": str,
        "PreferredOutpostArn": str,
        "CurrentRole": str,
    },
    total=False,
)

CacheEngineVersionMessageTypeDef = TypedDict(
    "CacheEngineVersionMessageTypeDef",
    {
        "Marker": str,
        "CacheEngineVersions": List[CacheEngineVersionTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CacheNodeTypeSpecificParameterTypeDef = TypedDict(
    "CacheNodeTypeSpecificParameterTypeDef",
    {
        "ParameterName": str,
        "Description": str,
        "Source": str,
        "DataType": str,
        "AllowedValues": str,
        "IsModifiable": bool,
        "MinimumEngineVersion": str,
        "CacheNodeTypeSpecificValues": List[CacheNodeTypeSpecificValueTypeDef],
        "ChangeType": ChangeTypeType,
    },
    total=False,
)

CacheParameterGroupsMessageTypeDef = TypedDict(
    "CacheParameterGroupsMessageTypeDef",
    {
        "Marker": str,
        "CacheParameterGroups": List[CacheParameterGroupTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateCacheParameterGroupResultTypeDef = TypedDict(
    "CreateCacheParameterGroupResultTypeDef",
    {
        "CacheParameterGroup": CacheParameterGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CacheSecurityGroupTypeDef = TypedDict(
    "CacheSecurityGroupTypeDef",
    {
        "OwnerId": str,
        "CacheSecurityGroupName": str,
        "Description": str,
        "EC2SecurityGroups": List[EC2SecurityGroupTypeDef],
        "ARN": str,
    },
    total=False,
)

_RequiredDecreaseReplicaCountMessageRequestTypeDef = TypedDict(
    "_RequiredDecreaseReplicaCountMessageRequestTypeDef",
    {
        "ReplicationGroupId": str,
        "ApplyImmediately": bool,
    },
)
_OptionalDecreaseReplicaCountMessageRequestTypeDef = TypedDict(
    "_OptionalDecreaseReplicaCountMessageRequestTypeDef",
    {
        "NewReplicaCount": int,
        "ReplicaConfiguration": Sequence[ConfigureShardTypeDef],
        "ReplicasToRemove": Sequence[str],
    },
    total=False,
)


class DecreaseReplicaCountMessageRequestTypeDef(
    _RequiredDecreaseReplicaCountMessageRequestTypeDef,
    _OptionalDecreaseReplicaCountMessageRequestTypeDef,
):
    pass


_RequiredIncreaseReplicaCountMessageRequestTypeDef = TypedDict(
    "_RequiredIncreaseReplicaCountMessageRequestTypeDef",
    {
        "ReplicationGroupId": str,
        "ApplyImmediately": bool,
    },
)
_OptionalIncreaseReplicaCountMessageRequestTypeDef = TypedDict(
    "_OptionalIncreaseReplicaCountMessageRequestTypeDef",
    {
        "NewReplicaCount": int,
        "ReplicaConfiguration": Sequence[ConfigureShardTypeDef],
    },
    total=False,
)


class IncreaseReplicaCountMessageRequestTypeDef(
    _RequiredIncreaseReplicaCountMessageRequestTypeDef,
    _OptionalIncreaseReplicaCountMessageRequestTypeDef,
):
    pass


NodeSnapshotTypeDef = TypedDict(
    "NodeSnapshotTypeDef",
    {
        "CacheClusterId": str,
        "NodeGroupId": str,
        "CacheNodeId": str,
        "NodeGroupConfiguration": NodeGroupConfigurationTypeDef,
        "CacheSize": str,
        "CacheNodeCreateTime": datetime,
        "SnapshotCreateTime": datetime,
    },
    total=False,
)

StartMigrationMessageRequestTypeDef = TypedDict(
    "StartMigrationMessageRequestTypeDef",
    {
        "ReplicationGroupId": str,
        "CustomerNodeEndpointList": Sequence[CustomerNodeEndpointTypeDef],
    },
)

DescribeCacheClustersMessageCacheClusterAvailableWaitTypeDef = TypedDict(
    "DescribeCacheClustersMessageCacheClusterAvailableWaitTypeDef",
    {
        "CacheClusterId": str,
        "MaxRecords": int,
        "Marker": str,
        "ShowCacheNodeInfo": bool,
        "ShowCacheClustersNotInReplicationGroups": bool,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeCacheClustersMessageCacheClusterDeletedWaitTypeDef = TypedDict(
    "DescribeCacheClustersMessageCacheClusterDeletedWaitTypeDef",
    {
        "CacheClusterId": str,
        "MaxRecords": int,
        "Marker": str,
        "ShowCacheNodeInfo": bool,
        "ShowCacheClustersNotInReplicationGroups": bool,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeReplicationGroupsMessageReplicationGroupAvailableWaitTypeDef = TypedDict(
    "DescribeReplicationGroupsMessageReplicationGroupAvailableWaitTypeDef",
    {
        "ReplicationGroupId": str,
        "MaxRecords": int,
        "Marker": str,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeReplicationGroupsMessageReplicationGroupDeletedWaitTypeDef = TypedDict(
    "DescribeReplicationGroupsMessageReplicationGroupDeletedWaitTypeDef",
    {
        "ReplicationGroupId": str,
        "MaxRecords": int,
        "Marker": str,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeCacheClustersMessageDescribeCacheClustersPaginateTypeDef = TypedDict(
    "DescribeCacheClustersMessageDescribeCacheClustersPaginateTypeDef",
    {
        "CacheClusterId": str,
        "ShowCacheNodeInfo": bool,
        "ShowCacheClustersNotInReplicationGroups": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeCacheEngineVersionsMessageDescribeCacheEngineVersionsPaginateTypeDef = TypedDict(
    "DescribeCacheEngineVersionsMessageDescribeCacheEngineVersionsPaginateTypeDef",
    {
        "Engine": str,
        "EngineVersion": str,
        "CacheParameterGroupFamily": str,
        "DefaultOnly": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeCacheParameterGroupsMessageDescribeCacheParameterGroupsPaginateTypeDef = TypedDict(
    "DescribeCacheParameterGroupsMessageDescribeCacheParameterGroupsPaginateTypeDef",
    {
        "CacheParameterGroupName": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

_RequiredDescribeCacheParametersMessageDescribeCacheParametersPaginateTypeDef = TypedDict(
    "_RequiredDescribeCacheParametersMessageDescribeCacheParametersPaginateTypeDef",
    {
        "CacheParameterGroupName": str,
    },
)
_OptionalDescribeCacheParametersMessageDescribeCacheParametersPaginateTypeDef = TypedDict(
    "_OptionalDescribeCacheParametersMessageDescribeCacheParametersPaginateTypeDef",
    {
        "Source": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class DescribeCacheParametersMessageDescribeCacheParametersPaginateTypeDef(
    _RequiredDescribeCacheParametersMessageDescribeCacheParametersPaginateTypeDef,
    _OptionalDescribeCacheParametersMessageDescribeCacheParametersPaginateTypeDef,
):
    pass


DescribeCacheSecurityGroupsMessageDescribeCacheSecurityGroupsPaginateTypeDef = TypedDict(
    "DescribeCacheSecurityGroupsMessageDescribeCacheSecurityGroupsPaginateTypeDef",
    {
        "CacheSecurityGroupName": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeCacheSubnetGroupsMessageDescribeCacheSubnetGroupsPaginateTypeDef = TypedDict(
    "DescribeCacheSubnetGroupsMessageDescribeCacheSubnetGroupsPaginateTypeDef",
    {
        "CacheSubnetGroupName": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

_RequiredDescribeEngineDefaultParametersMessageDescribeEngineDefaultParametersPaginateTypeDef = TypedDict(
    "_RequiredDescribeEngineDefaultParametersMessageDescribeEngineDefaultParametersPaginateTypeDef",
    {
        "CacheParameterGroupFamily": str,
    },
)
_OptionalDescribeEngineDefaultParametersMessageDescribeEngineDefaultParametersPaginateTypeDef = TypedDict(
    "_OptionalDescribeEngineDefaultParametersMessageDescribeEngineDefaultParametersPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class DescribeEngineDefaultParametersMessageDescribeEngineDefaultParametersPaginateTypeDef(
    _RequiredDescribeEngineDefaultParametersMessageDescribeEngineDefaultParametersPaginateTypeDef,
    _OptionalDescribeEngineDefaultParametersMessageDescribeEngineDefaultParametersPaginateTypeDef,
):
    pass


DescribeEventsMessageDescribeEventsPaginateTypeDef = TypedDict(
    "DescribeEventsMessageDescribeEventsPaginateTypeDef",
    {
        "SourceIdentifier": str,
        "SourceType": SourceTypeType,
        "StartTime": Union[datetime, str],
        "EndTime": Union[datetime, str],
        "Duration": int,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeGlobalReplicationGroupsMessageDescribeGlobalReplicationGroupsPaginateTypeDef = TypedDict(
    "DescribeGlobalReplicationGroupsMessageDescribeGlobalReplicationGroupsPaginateTypeDef",
    {
        "GlobalReplicationGroupId": str,
        "ShowMemberInfo": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeReplicationGroupsMessageDescribeReplicationGroupsPaginateTypeDef = TypedDict(
    "DescribeReplicationGroupsMessageDescribeReplicationGroupsPaginateTypeDef",
    {
        "ReplicationGroupId": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeReservedCacheNodesMessageDescribeReservedCacheNodesPaginateTypeDef = TypedDict(
    "DescribeReservedCacheNodesMessageDescribeReservedCacheNodesPaginateTypeDef",
    {
        "ReservedCacheNodeId": str,
        "ReservedCacheNodesOfferingId": str,
        "CacheNodeType": str,
        "Duration": str,
        "ProductDescription": str,
        "OfferingType": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeReservedCacheNodesOfferingsMessageDescribeReservedCacheNodesOfferingsPaginateTypeDef = TypedDict(
    "DescribeReservedCacheNodesOfferingsMessageDescribeReservedCacheNodesOfferingsPaginateTypeDef",
    {
        "ReservedCacheNodesOfferingId": str,
        "CacheNodeType": str,
        "Duration": str,
        "ProductDescription": str,
        "OfferingType": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeServiceUpdatesMessageDescribeServiceUpdatesPaginateTypeDef = TypedDict(
    "DescribeServiceUpdatesMessageDescribeServiceUpdatesPaginateTypeDef",
    {
        "ServiceUpdateName": str,
        "ServiceUpdateStatus": Sequence[ServiceUpdateStatusType],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeSnapshotsMessageDescribeSnapshotsPaginateTypeDef = TypedDict(
    "DescribeSnapshotsMessageDescribeSnapshotsPaginateTypeDef",
    {
        "ReplicationGroupId": str,
        "CacheClusterId": str,
        "SnapshotName": str,
        "SnapshotSource": str,
        "ShowNodeGroupConfig": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeUserGroupsMessageDescribeUserGroupsPaginateTypeDef = TypedDict(
    "DescribeUserGroupsMessageDescribeUserGroupsPaginateTypeDef",
    {
        "UserGroupId": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeUpdateActionsMessageDescribeUpdateActionsPaginateTypeDef = TypedDict(
    "DescribeUpdateActionsMessageDescribeUpdateActionsPaginateTypeDef",
    {
        "ServiceUpdateName": str,
        "ReplicationGroupIds": Sequence[str],
        "CacheClusterIds": Sequence[str],
        "Engine": str,
        "ServiceUpdateStatus": Sequence[ServiceUpdateStatusType],
        "ServiceUpdateTimeRange": TimeRangeFilterTypeDef,
        "UpdateActionStatus": Sequence[UpdateActionStatusType],
        "ShowNodeLevelUpdateStatus": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeUpdateActionsMessageRequestTypeDef = TypedDict(
    "DescribeUpdateActionsMessageRequestTypeDef",
    {
        "ServiceUpdateName": str,
        "ReplicationGroupIds": Sequence[str],
        "CacheClusterIds": Sequence[str],
        "Engine": str,
        "ServiceUpdateStatus": Sequence[ServiceUpdateStatusType],
        "ServiceUpdateTimeRange": TimeRangeFilterTypeDef,
        "UpdateActionStatus": Sequence[UpdateActionStatusType],
        "ShowNodeLevelUpdateStatus": bool,
        "MaxRecords": int,
        "Marker": str,
    },
    total=False,
)

DescribeUsersMessageDescribeUsersPaginateTypeDef = TypedDict(
    "DescribeUsersMessageDescribeUsersPaginateTypeDef",
    {
        "Engine": str,
        "UserId": str,
        "Filters": Sequence[FilterTypeDef],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeUsersMessageRequestTypeDef = TypedDict(
    "DescribeUsersMessageRequestTypeDef",
    {
        "Engine": str,
        "UserId": str,
        "Filters": Sequence[FilterTypeDef],
        "MaxRecords": int,
        "Marker": str,
    },
    total=False,
)

DestinationDetailsTypeDef = TypedDict(
    "DestinationDetailsTypeDef",
    {
        "CloudWatchLogsDetails": CloudWatchLogsDestinationDetailsTypeDef,
        "KinesisFirehoseDetails": KinesisFirehoseDestinationDetailsTypeDef,
    },
    total=False,
)

EventsMessageTypeDef = TypedDict(
    "EventsMessageTypeDef",
    {
        "Marker": str,
        "Events": List[EventTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GlobalReplicationGroupTypeDef = TypedDict(
    "GlobalReplicationGroupTypeDef",
    {
        "GlobalReplicationGroupId": str,
        "GlobalReplicationGroupDescription": str,
        "Status": str,
        "CacheNodeType": str,
        "Engine": str,
        "EngineVersion": str,
        "Members": List[GlobalReplicationGroupMemberTypeDef],
        "ClusterEnabled": bool,
        "GlobalNodeGroups": List[GlobalNodeGroupTypeDef],
        "AuthTokenEnabled": bool,
        "TransitEncryptionEnabled": bool,
        "AtRestEncryptionEnabled": bool,
        "ARN": str,
    },
    total=False,
)

ModifyCacheParameterGroupMessageRequestTypeDef = TypedDict(
    "ModifyCacheParameterGroupMessageRequestTypeDef",
    {
        "CacheParameterGroupName": str,
        "ParameterNameValues": Sequence[ParameterNameValueTypeDef],
    },
)

_RequiredResetCacheParameterGroupMessageRequestTypeDef = TypedDict(
    "_RequiredResetCacheParameterGroupMessageRequestTypeDef",
    {
        "CacheParameterGroupName": str,
    },
)
_OptionalResetCacheParameterGroupMessageRequestTypeDef = TypedDict(
    "_OptionalResetCacheParameterGroupMessageRequestTypeDef",
    {
        "ResetAllParameters": bool,
        "ParameterNameValues": Sequence[ParameterNameValueTypeDef],
    },
    total=False,
)


class ResetCacheParameterGroupMessageRequestTypeDef(
    _RequiredResetCacheParameterGroupMessageRequestTypeDef,
    _OptionalResetCacheParameterGroupMessageRequestTypeDef,
):
    pass


_RequiredModifyReplicationGroupShardConfigurationMessageRequestTypeDef = TypedDict(
    "_RequiredModifyReplicationGroupShardConfigurationMessageRequestTypeDef",
    {
        "ReplicationGroupId": str,
        "NodeGroupCount": int,
        "ApplyImmediately": bool,
    },
)
_OptionalModifyReplicationGroupShardConfigurationMessageRequestTypeDef = TypedDict(
    "_OptionalModifyReplicationGroupShardConfigurationMessageRequestTypeDef",
    {
        "ReshardingConfiguration": Sequence[ReshardingConfigurationTypeDef],
        "NodeGroupsToRemove": Sequence[str],
        "NodeGroupsToRetain": Sequence[str],
    },
    total=False,
)


class ModifyReplicationGroupShardConfigurationMessageRequestTypeDef(
    _RequiredModifyReplicationGroupShardConfigurationMessageRequestTypeDef,
    _OptionalModifyReplicationGroupShardConfigurationMessageRequestTypeDef,
):
    pass


RegionalConfigurationTypeDef = TypedDict(
    "RegionalConfigurationTypeDef",
    {
        "ReplicationGroupId": str,
        "ReplicationGroupRegion": str,
        "ReshardingConfiguration": Sequence[ReshardingConfigurationTypeDef],
    },
)

NodeGroupUpdateStatusTypeDef = TypedDict(
    "NodeGroupUpdateStatusTypeDef",
    {
        "NodeGroupId": str,
        "NodeGroupMemberUpdateStatus": List[NodeGroupMemberUpdateStatusTypeDef],
    },
    total=False,
)

ReservedCacheNodeTypeDef = TypedDict(
    "ReservedCacheNodeTypeDef",
    {
        "ReservedCacheNodeId": str,
        "ReservedCacheNodesOfferingId": str,
        "CacheNodeType": str,
        "StartTime": datetime,
        "Duration": int,
        "FixedPrice": float,
        "UsagePrice": float,
        "CacheNodeCount": int,
        "ProductDescription": str,
        "OfferingType": str,
        "State": str,
        "RecurringCharges": List[RecurringChargeTypeDef],
        "ReservationARN": str,
    },
    total=False,
)

ReservedCacheNodesOfferingTypeDef = TypedDict(
    "ReservedCacheNodesOfferingTypeDef",
    {
        "ReservedCacheNodesOfferingId": str,
        "CacheNodeType": str,
        "Duration": int,
        "FixedPrice": float,
        "UsagePrice": float,
        "ProductDescription": str,
        "OfferingType": str,
        "RecurringCharges": List[RecurringChargeTypeDef],
    },
    total=False,
)

ReshardingStatusTypeDef = TypedDict(
    "ReshardingStatusTypeDef",
    {
        "SlotMigration": SlotMigrationTypeDef,
    },
    total=False,
)

ServiceUpdatesMessageTypeDef = TypedDict(
    "ServiceUpdatesMessageTypeDef",
    {
        "Marker": str,
        "ServiceUpdates": List[ServiceUpdateTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SubnetTypeDef = TypedDict(
    "SubnetTypeDef",
    {
        "SubnetIdentifier": str,
        "SubnetAvailabilityZone": AvailabilityZoneTypeDef,
        "SubnetOutpost": SubnetOutpostTypeDef,
    },
    total=False,
)

UpdateActionResultsMessageTypeDef = TypedDict(
    "UpdateActionResultsMessageTypeDef",
    {
        "ProcessedUpdateActions": List[ProcessedUpdateActionTypeDef],
        "UnprocessedUpdateActions": List[UnprocessedUpdateActionTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UserGroupResponseMetadataTypeDef = TypedDict(
    "UserGroupResponseMetadataTypeDef",
    {
        "UserGroupId": str,
        "Status": str,
        "Engine": str,
        "UserIds": List[str],
        "MinimumEngineVersion": str,
        "PendingChanges": UserGroupPendingChangesTypeDef,
        "ReplicationGroups": List[str],
        "ARN": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UserGroupTypeDef = TypedDict(
    "UserGroupTypeDef",
    {
        "UserGroupId": str,
        "Status": str,
        "Engine": str,
        "UserIds": List[str],
        "MinimumEngineVersion": str,
        "PendingChanges": UserGroupPendingChangesTypeDef,
        "ReplicationGroups": List[str],
        "ARN": str,
    },
    total=False,
)

DescribeUsersResultTypeDef = TypedDict(
    "DescribeUsersResultTypeDef",
    {
        "Users": List[UserTypeDef],
        "Marker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

NodeGroupTypeDef = TypedDict(
    "NodeGroupTypeDef",
    {
        "NodeGroupId": str,
        "Status": str,
        "PrimaryEndpoint": EndpointTypeDef,
        "ReaderEndpoint": EndpointTypeDef,
        "Slots": str,
        "NodeGroupMembers": List[NodeGroupMemberTypeDef],
    },
    total=False,
)

CacheParameterGroupDetailsTypeDef = TypedDict(
    "CacheParameterGroupDetailsTypeDef",
    {
        "Marker": str,
        "Parameters": List[ParameterTypeDef],
        "CacheNodeTypeSpecificParameters": List[CacheNodeTypeSpecificParameterTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EngineDefaultsTypeDef = TypedDict(
    "EngineDefaultsTypeDef",
    {
        "CacheParameterGroupFamily": str,
        "Marker": str,
        "Parameters": List[ParameterTypeDef],
        "CacheNodeTypeSpecificParameters": List[CacheNodeTypeSpecificParameterTypeDef],
    },
    total=False,
)

AuthorizeCacheSecurityGroupIngressResultTypeDef = TypedDict(
    "AuthorizeCacheSecurityGroupIngressResultTypeDef",
    {
        "CacheSecurityGroup": CacheSecurityGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CacheSecurityGroupMessageTypeDef = TypedDict(
    "CacheSecurityGroupMessageTypeDef",
    {
        "Marker": str,
        "CacheSecurityGroups": List[CacheSecurityGroupTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateCacheSecurityGroupResultTypeDef = TypedDict(
    "CreateCacheSecurityGroupResultTypeDef",
    {
        "CacheSecurityGroup": CacheSecurityGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RevokeCacheSecurityGroupIngressResultTypeDef = TypedDict(
    "RevokeCacheSecurityGroupIngressResultTypeDef",
    {
        "CacheSecurityGroup": CacheSecurityGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SnapshotTypeDef = TypedDict(
    "SnapshotTypeDef",
    {
        "SnapshotName": str,
        "ReplicationGroupId": str,
        "ReplicationGroupDescription": str,
        "CacheClusterId": str,
        "SnapshotStatus": str,
        "SnapshotSource": str,
        "CacheNodeType": str,
        "Engine": str,
        "EngineVersion": str,
        "NumCacheNodes": int,
        "PreferredAvailabilityZone": str,
        "PreferredOutpostArn": str,
        "CacheClusterCreateTime": datetime,
        "PreferredMaintenanceWindow": str,
        "TopicArn": str,
        "Port": int,
        "CacheParameterGroupName": str,
        "CacheSubnetGroupName": str,
        "VpcId": str,
        "AutoMinorVersionUpgrade": bool,
        "SnapshotRetentionLimit": int,
        "SnapshotWindow": str,
        "NumNodeGroups": int,
        "AutomaticFailover": AutomaticFailoverStatusType,
        "NodeSnapshots": List[NodeSnapshotTypeDef],
        "KmsKeyId": str,
        "ARN": str,
        "DataTiering": DataTieringStatusType,
    },
    total=False,
)

LogDeliveryConfigurationRequestTypeDef = TypedDict(
    "LogDeliveryConfigurationRequestTypeDef",
    {
        "LogType": LogTypeType,
        "DestinationType": DestinationTypeType,
        "DestinationDetails": DestinationDetailsTypeDef,
        "LogFormat": LogFormatType,
        "Enabled": bool,
    },
    total=False,
)

LogDeliveryConfigurationTypeDef = TypedDict(
    "LogDeliveryConfigurationTypeDef",
    {
        "LogType": LogTypeType,
        "DestinationType": DestinationTypeType,
        "DestinationDetails": DestinationDetailsTypeDef,
        "LogFormat": LogFormatType,
        "Status": LogDeliveryConfigurationStatusType,
        "Message": str,
    },
    total=False,
)

PendingLogDeliveryConfigurationTypeDef = TypedDict(
    "PendingLogDeliveryConfigurationTypeDef",
    {
        "LogType": LogTypeType,
        "DestinationType": DestinationTypeType,
        "DestinationDetails": DestinationDetailsTypeDef,
        "LogFormat": LogFormatType,
    },
    total=False,
)

CreateGlobalReplicationGroupResultTypeDef = TypedDict(
    "CreateGlobalReplicationGroupResultTypeDef",
    {
        "GlobalReplicationGroup": GlobalReplicationGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DecreaseNodeGroupsInGlobalReplicationGroupResultTypeDef = TypedDict(
    "DecreaseNodeGroupsInGlobalReplicationGroupResultTypeDef",
    {
        "GlobalReplicationGroup": GlobalReplicationGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteGlobalReplicationGroupResultTypeDef = TypedDict(
    "DeleteGlobalReplicationGroupResultTypeDef",
    {
        "GlobalReplicationGroup": GlobalReplicationGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeGlobalReplicationGroupsResultTypeDef = TypedDict(
    "DescribeGlobalReplicationGroupsResultTypeDef",
    {
        "Marker": str,
        "GlobalReplicationGroups": List[GlobalReplicationGroupTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisassociateGlobalReplicationGroupResultTypeDef = TypedDict(
    "DisassociateGlobalReplicationGroupResultTypeDef",
    {
        "GlobalReplicationGroup": GlobalReplicationGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

FailoverGlobalReplicationGroupResultTypeDef = TypedDict(
    "FailoverGlobalReplicationGroupResultTypeDef",
    {
        "GlobalReplicationGroup": GlobalReplicationGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

IncreaseNodeGroupsInGlobalReplicationGroupResultTypeDef = TypedDict(
    "IncreaseNodeGroupsInGlobalReplicationGroupResultTypeDef",
    {
        "GlobalReplicationGroup": GlobalReplicationGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyGlobalReplicationGroupResultTypeDef = TypedDict(
    "ModifyGlobalReplicationGroupResultTypeDef",
    {
        "GlobalReplicationGroup": GlobalReplicationGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RebalanceSlotsInGlobalReplicationGroupResultTypeDef = TypedDict(
    "RebalanceSlotsInGlobalReplicationGroupResultTypeDef",
    {
        "GlobalReplicationGroup": GlobalReplicationGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredIncreaseNodeGroupsInGlobalReplicationGroupMessageRequestTypeDef = TypedDict(
    "_RequiredIncreaseNodeGroupsInGlobalReplicationGroupMessageRequestTypeDef",
    {
        "GlobalReplicationGroupId": str,
        "NodeGroupCount": int,
        "ApplyImmediately": bool,
    },
)
_OptionalIncreaseNodeGroupsInGlobalReplicationGroupMessageRequestTypeDef = TypedDict(
    "_OptionalIncreaseNodeGroupsInGlobalReplicationGroupMessageRequestTypeDef",
    {
        "RegionalConfigurations": Sequence[RegionalConfigurationTypeDef],
    },
    total=False,
)


class IncreaseNodeGroupsInGlobalReplicationGroupMessageRequestTypeDef(
    _RequiredIncreaseNodeGroupsInGlobalReplicationGroupMessageRequestTypeDef,
    _OptionalIncreaseNodeGroupsInGlobalReplicationGroupMessageRequestTypeDef,
):
    pass


UpdateActionTypeDef = TypedDict(
    "UpdateActionTypeDef",
    {
        "ReplicationGroupId": str,
        "CacheClusterId": str,
        "ServiceUpdateName": str,
        "ServiceUpdateReleaseDate": datetime,
        "ServiceUpdateSeverity": ServiceUpdateSeverityType,
        "ServiceUpdateStatus": ServiceUpdateStatusType,
        "ServiceUpdateRecommendedApplyByDate": datetime,
        "ServiceUpdateType": Literal["security-update"],
        "UpdateActionAvailableDate": datetime,
        "UpdateActionStatus": UpdateActionStatusType,
        "NodesUpdated": str,
        "UpdateActionStatusModifiedDate": datetime,
        "SlaMet": SlaMetType,
        "NodeGroupUpdateStatus": List[NodeGroupUpdateStatusTypeDef],
        "CacheNodeUpdateStatus": List[CacheNodeUpdateStatusTypeDef],
        "EstimatedUpdateTime": str,
        "Engine": str,
    },
    total=False,
)

PurchaseReservedCacheNodesOfferingResultTypeDef = TypedDict(
    "PurchaseReservedCacheNodesOfferingResultTypeDef",
    {
        "ReservedCacheNode": ReservedCacheNodeTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ReservedCacheNodeMessageTypeDef = TypedDict(
    "ReservedCacheNodeMessageTypeDef",
    {
        "Marker": str,
        "ReservedCacheNodes": List[ReservedCacheNodeTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ReservedCacheNodesOfferingMessageTypeDef = TypedDict(
    "ReservedCacheNodesOfferingMessageTypeDef",
    {
        "Marker": str,
        "ReservedCacheNodesOfferings": List[ReservedCacheNodesOfferingTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CacheSubnetGroupTypeDef = TypedDict(
    "CacheSubnetGroupTypeDef",
    {
        "CacheSubnetGroupName": str,
        "CacheSubnetGroupDescription": str,
        "VpcId": str,
        "Subnets": List[SubnetTypeDef],
        "ARN": str,
    },
    total=False,
)

DescribeUserGroupsResultTypeDef = TypedDict(
    "DescribeUserGroupsResultTypeDef",
    {
        "UserGroups": List[UserGroupTypeDef],
        "Marker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeEngineDefaultParametersResultTypeDef = TypedDict(
    "DescribeEngineDefaultParametersResultTypeDef",
    {
        "EngineDefaults": EngineDefaultsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CopySnapshotResultTypeDef = TypedDict(
    "CopySnapshotResultTypeDef",
    {
        "Snapshot": SnapshotTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateSnapshotResultTypeDef = TypedDict(
    "CreateSnapshotResultTypeDef",
    {
        "Snapshot": SnapshotTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteSnapshotResultTypeDef = TypedDict(
    "DeleteSnapshotResultTypeDef",
    {
        "Snapshot": SnapshotTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSnapshotsListMessageTypeDef = TypedDict(
    "DescribeSnapshotsListMessageTypeDef",
    {
        "Marker": str,
        "Snapshots": List[SnapshotTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredCreateCacheClusterMessageRequestTypeDef = TypedDict(
    "_RequiredCreateCacheClusterMessageRequestTypeDef",
    {
        "CacheClusterId": str,
    },
)
_OptionalCreateCacheClusterMessageRequestTypeDef = TypedDict(
    "_OptionalCreateCacheClusterMessageRequestTypeDef",
    {
        "ReplicationGroupId": str,
        "AZMode": AZModeType,
        "PreferredAvailabilityZone": str,
        "PreferredAvailabilityZones": Sequence[str],
        "NumCacheNodes": int,
        "CacheNodeType": str,
        "Engine": str,
        "EngineVersion": str,
        "CacheParameterGroupName": str,
        "CacheSubnetGroupName": str,
        "CacheSecurityGroupNames": Sequence[str],
        "SecurityGroupIds": Sequence[str],
        "Tags": Sequence[TagTypeDef],
        "SnapshotArns": Sequence[str],
        "SnapshotName": str,
        "PreferredMaintenanceWindow": str,
        "Port": int,
        "NotificationTopicArn": str,
        "AutoMinorVersionUpgrade": bool,
        "SnapshotRetentionLimit": int,
        "SnapshotWindow": str,
        "AuthToken": str,
        "OutpostMode": OutpostModeType,
        "PreferredOutpostArn": str,
        "PreferredOutpostArns": Sequence[str],
        "LogDeliveryConfigurations": Sequence[LogDeliveryConfigurationRequestTypeDef],
        "TransitEncryptionEnabled": bool,
    },
    total=False,
)


class CreateCacheClusterMessageRequestTypeDef(
    _RequiredCreateCacheClusterMessageRequestTypeDef,
    _OptionalCreateCacheClusterMessageRequestTypeDef,
):
    pass


_RequiredCreateReplicationGroupMessageRequestTypeDef = TypedDict(
    "_RequiredCreateReplicationGroupMessageRequestTypeDef",
    {
        "ReplicationGroupId": str,
        "ReplicationGroupDescription": str,
    },
)
_OptionalCreateReplicationGroupMessageRequestTypeDef = TypedDict(
    "_OptionalCreateReplicationGroupMessageRequestTypeDef",
    {
        "GlobalReplicationGroupId": str,
        "PrimaryClusterId": str,
        "AutomaticFailoverEnabled": bool,
        "MultiAZEnabled": bool,
        "NumCacheClusters": int,
        "PreferredCacheClusterAZs": Sequence[str],
        "NumNodeGroups": int,
        "ReplicasPerNodeGroup": int,
        "NodeGroupConfiguration": Sequence[NodeGroupConfigurationTypeDef],
        "CacheNodeType": str,
        "Engine": str,
        "EngineVersion": str,
        "CacheParameterGroupName": str,
        "CacheSubnetGroupName": str,
        "CacheSecurityGroupNames": Sequence[str],
        "SecurityGroupIds": Sequence[str],
        "Tags": Sequence[TagTypeDef],
        "SnapshotArns": Sequence[str],
        "SnapshotName": str,
        "PreferredMaintenanceWindow": str,
        "Port": int,
        "NotificationTopicArn": str,
        "AutoMinorVersionUpgrade": bool,
        "SnapshotRetentionLimit": int,
        "SnapshotWindow": str,
        "AuthToken": str,
        "TransitEncryptionEnabled": bool,
        "AtRestEncryptionEnabled": bool,
        "KmsKeyId": str,
        "UserGroupIds": Sequence[str],
        "LogDeliveryConfigurations": Sequence[LogDeliveryConfigurationRequestTypeDef],
        "DataTieringEnabled": bool,
    },
    total=False,
)


class CreateReplicationGroupMessageRequestTypeDef(
    _RequiredCreateReplicationGroupMessageRequestTypeDef,
    _OptionalCreateReplicationGroupMessageRequestTypeDef,
):
    pass


_RequiredModifyCacheClusterMessageRequestTypeDef = TypedDict(
    "_RequiredModifyCacheClusterMessageRequestTypeDef",
    {
        "CacheClusterId": str,
    },
)
_OptionalModifyCacheClusterMessageRequestTypeDef = TypedDict(
    "_OptionalModifyCacheClusterMessageRequestTypeDef",
    {
        "NumCacheNodes": int,
        "CacheNodeIdsToRemove": Sequence[str],
        "AZMode": AZModeType,
        "NewAvailabilityZones": Sequence[str],
        "CacheSecurityGroupNames": Sequence[str],
        "SecurityGroupIds": Sequence[str],
        "PreferredMaintenanceWindow": str,
        "NotificationTopicArn": str,
        "CacheParameterGroupName": str,
        "NotificationTopicStatus": str,
        "ApplyImmediately": bool,
        "EngineVersion": str,
        "AutoMinorVersionUpgrade": bool,
        "SnapshotRetentionLimit": int,
        "SnapshotWindow": str,
        "CacheNodeType": str,
        "AuthToken": str,
        "AuthTokenUpdateStrategy": AuthTokenUpdateStrategyTypeType,
        "LogDeliveryConfigurations": Sequence[LogDeliveryConfigurationRequestTypeDef],
    },
    total=False,
)


class ModifyCacheClusterMessageRequestTypeDef(
    _RequiredModifyCacheClusterMessageRequestTypeDef,
    _OptionalModifyCacheClusterMessageRequestTypeDef,
):
    pass


_RequiredModifyReplicationGroupMessageRequestTypeDef = TypedDict(
    "_RequiredModifyReplicationGroupMessageRequestTypeDef",
    {
        "ReplicationGroupId": str,
    },
)
_OptionalModifyReplicationGroupMessageRequestTypeDef = TypedDict(
    "_OptionalModifyReplicationGroupMessageRequestTypeDef",
    {
        "ReplicationGroupDescription": str,
        "PrimaryClusterId": str,
        "SnapshottingClusterId": str,
        "AutomaticFailoverEnabled": bool,
        "MultiAZEnabled": bool,
        "NodeGroupId": str,
        "CacheSecurityGroupNames": Sequence[str],
        "SecurityGroupIds": Sequence[str],
        "PreferredMaintenanceWindow": str,
        "NotificationTopicArn": str,
        "CacheParameterGroupName": str,
        "NotificationTopicStatus": str,
        "ApplyImmediately": bool,
        "EngineVersion": str,
        "AutoMinorVersionUpgrade": bool,
        "SnapshotRetentionLimit": int,
        "SnapshotWindow": str,
        "CacheNodeType": str,
        "AuthToken": str,
        "AuthTokenUpdateStrategy": AuthTokenUpdateStrategyTypeType,
        "UserGroupIdsToAdd": Sequence[str],
        "UserGroupIdsToRemove": Sequence[str],
        "RemoveUserGroups": bool,
        "LogDeliveryConfigurations": Sequence[LogDeliveryConfigurationRequestTypeDef],
    },
    total=False,
)


class ModifyReplicationGroupMessageRequestTypeDef(
    _RequiredModifyReplicationGroupMessageRequestTypeDef,
    _OptionalModifyReplicationGroupMessageRequestTypeDef,
):
    pass


PendingModifiedValuesTypeDef = TypedDict(
    "PendingModifiedValuesTypeDef",
    {
        "NumCacheNodes": int,
        "CacheNodeIdsToRemove": List[str],
        "EngineVersion": str,
        "CacheNodeType": str,
        "AuthTokenStatus": AuthTokenUpdateStatusType,
        "LogDeliveryConfigurations": List[PendingLogDeliveryConfigurationTypeDef],
    },
    total=False,
)

ReplicationGroupPendingModifiedValuesTypeDef = TypedDict(
    "ReplicationGroupPendingModifiedValuesTypeDef",
    {
        "PrimaryClusterId": str,
        "AutomaticFailoverStatus": PendingAutomaticFailoverStatusType,
        "Resharding": ReshardingStatusTypeDef,
        "AuthTokenStatus": AuthTokenUpdateStatusType,
        "UserGroups": UserGroupsUpdateStatusTypeDef,
        "LogDeliveryConfigurations": List[PendingLogDeliveryConfigurationTypeDef],
    },
    total=False,
)

UpdateActionsMessageTypeDef = TypedDict(
    "UpdateActionsMessageTypeDef",
    {
        "Marker": str,
        "UpdateActions": List[UpdateActionTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CacheSubnetGroupMessageTypeDef = TypedDict(
    "CacheSubnetGroupMessageTypeDef",
    {
        "Marker": str,
        "CacheSubnetGroups": List[CacheSubnetGroupTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateCacheSubnetGroupResultTypeDef = TypedDict(
    "CreateCacheSubnetGroupResultTypeDef",
    {
        "CacheSubnetGroup": CacheSubnetGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyCacheSubnetGroupResultTypeDef = TypedDict(
    "ModifyCacheSubnetGroupResultTypeDef",
    {
        "CacheSubnetGroup": CacheSubnetGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CacheClusterTypeDef = TypedDict(
    "CacheClusterTypeDef",
    {
        "CacheClusterId": str,
        "ConfigurationEndpoint": EndpointTypeDef,
        "ClientDownloadLandingPage": str,
        "CacheNodeType": str,
        "Engine": str,
        "EngineVersion": str,
        "CacheClusterStatus": str,
        "NumCacheNodes": int,
        "PreferredAvailabilityZone": str,
        "PreferredOutpostArn": str,
        "CacheClusterCreateTime": datetime,
        "PreferredMaintenanceWindow": str,
        "PendingModifiedValues": PendingModifiedValuesTypeDef,
        "NotificationConfiguration": NotificationConfigurationTypeDef,
        "CacheSecurityGroups": List[CacheSecurityGroupMembershipTypeDef],
        "CacheParameterGroup": CacheParameterGroupStatusTypeDef,
        "CacheSubnetGroupName": str,
        "CacheNodes": List[CacheNodeTypeDef],
        "AutoMinorVersionUpgrade": bool,
        "SecurityGroups": List[SecurityGroupMembershipTypeDef],
        "ReplicationGroupId": str,
        "SnapshotRetentionLimit": int,
        "SnapshotWindow": str,
        "AuthTokenEnabled": bool,
        "AuthTokenLastModifiedDate": datetime,
        "TransitEncryptionEnabled": bool,
        "AtRestEncryptionEnabled": bool,
        "ARN": str,
        "ReplicationGroupLogDeliveryEnabled": bool,
        "LogDeliveryConfigurations": List[LogDeliveryConfigurationTypeDef],
    },
    total=False,
)

ReplicationGroupTypeDef = TypedDict(
    "ReplicationGroupTypeDef",
    {
        "ReplicationGroupId": str,
        "Description": str,
        "GlobalReplicationGroupInfo": GlobalReplicationGroupInfoTypeDef,
        "Status": str,
        "PendingModifiedValues": ReplicationGroupPendingModifiedValuesTypeDef,
        "MemberClusters": List[str],
        "NodeGroups": List[NodeGroupTypeDef],
        "SnapshottingClusterId": str,
        "AutomaticFailover": AutomaticFailoverStatusType,
        "MultiAZ": MultiAZStatusType,
        "ConfigurationEndpoint": EndpointTypeDef,
        "SnapshotRetentionLimit": int,
        "SnapshotWindow": str,
        "ClusterEnabled": bool,
        "CacheNodeType": str,
        "AuthTokenEnabled": bool,
        "AuthTokenLastModifiedDate": datetime,
        "TransitEncryptionEnabled": bool,
        "AtRestEncryptionEnabled": bool,
        "MemberClustersOutpostArns": List[str],
        "KmsKeyId": str,
        "ARN": str,
        "UserGroupIds": List[str],
        "LogDeliveryConfigurations": List[LogDeliveryConfigurationTypeDef],
        "ReplicationGroupCreateTime": datetime,
        "DataTiering": DataTieringStatusType,
    },
    total=False,
)

CacheClusterMessageTypeDef = TypedDict(
    "CacheClusterMessageTypeDef",
    {
        "Marker": str,
        "CacheClusters": List[CacheClusterTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateCacheClusterResultTypeDef = TypedDict(
    "CreateCacheClusterResultTypeDef",
    {
        "CacheCluster": CacheClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteCacheClusterResultTypeDef = TypedDict(
    "DeleteCacheClusterResultTypeDef",
    {
        "CacheCluster": CacheClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyCacheClusterResultTypeDef = TypedDict(
    "ModifyCacheClusterResultTypeDef",
    {
        "CacheCluster": CacheClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RebootCacheClusterResultTypeDef = TypedDict(
    "RebootCacheClusterResultTypeDef",
    {
        "CacheCluster": CacheClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CompleteMigrationResponseTypeDef = TypedDict(
    "CompleteMigrationResponseTypeDef",
    {
        "ReplicationGroup": ReplicationGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateReplicationGroupResultTypeDef = TypedDict(
    "CreateReplicationGroupResultTypeDef",
    {
        "ReplicationGroup": ReplicationGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DecreaseReplicaCountResultTypeDef = TypedDict(
    "DecreaseReplicaCountResultTypeDef",
    {
        "ReplicationGroup": ReplicationGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteReplicationGroupResultTypeDef = TypedDict(
    "DeleteReplicationGroupResultTypeDef",
    {
        "ReplicationGroup": ReplicationGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

IncreaseReplicaCountResultTypeDef = TypedDict(
    "IncreaseReplicaCountResultTypeDef",
    {
        "ReplicationGroup": ReplicationGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyReplicationGroupResultTypeDef = TypedDict(
    "ModifyReplicationGroupResultTypeDef",
    {
        "ReplicationGroup": ReplicationGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModifyReplicationGroupShardConfigurationResultTypeDef = TypedDict(
    "ModifyReplicationGroupShardConfigurationResultTypeDef",
    {
        "ReplicationGroup": ReplicationGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ReplicationGroupMessageTypeDef = TypedDict(
    "ReplicationGroupMessageTypeDef",
    {
        "Marker": str,
        "ReplicationGroups": List[ReplicationGroupTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartMigrationResponseTypeDef = TypedDict(
    "StartMigrationResponseTypeDef",
    {
        "ReplicationGroup": ReplicationGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TestFailoverResultTypeDef = TypedDict(
    "TestFailoverResultTypeDef",
    {
        "ReplicationGroup": ReplicationGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
