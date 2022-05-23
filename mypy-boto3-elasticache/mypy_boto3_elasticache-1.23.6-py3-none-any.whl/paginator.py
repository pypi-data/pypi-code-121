"""
Type annotations for elasticache service client paginators.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/)

Usage::

    ```python
    from boto3.session import Session

    from mypy_boto3_elasticache.client import ElastiCacheClient
    from mypy_boto3_elasticache.paginator import (
        DescribeCacheClustersPaginator,
        DescribeCacheEngineVersionsPaginator,
        DescribeCacheParameterGroupsPaginator,
        DescribeCacheParametersPaginator,
        DescribeCacheSecurityGroupsPaginator,
        DescribeCacheSubnetGroupsPaginator,
        DescribeEngineDefaultParametersPaginator,
        DescribeEventsPaginator,
        DescribeGlobalReplicationGroupsPaginator,
        DescribeReplicationGroupsPaginator,
        DescribeReservedCacheNodesPaginator,
        DescribeReservedCacheNodesOfferingsPaginator,
        DescribeServiceUpdatesPaginator,
        DescribeSnapshotsPaginator,
        DescribeUpdateActionsPaginator,
        DescribeUserGroupsPaginator,
        DescribeUsersPaginator,
    )

    session = Session()
    client: ElastiCacheClient = session.client("elasticache")

    describe_cache_clusters_paginator: DescribeCacheClustersPaginator = client.get_paginator("describe_cache_clusters")
    describe_cache_engine_versions_paginator: DescribeCacheEngineVersionsPaginator = client.get_paginator("describe_cache_engine_versions")
    describe_cache_parameter_groups_paginator: DescribeCacheParameterGroupsPaginator = client.get_paginator("describe_cache_parameter_groups")
    describe_cache_parameters_paginator: DescribeCacheParametersPaginator = client.get_paginator("describe_cache_parameters")
    describe_cache_security_groups_paginator: DescribeCacheSecurityGroupsPaginator = client.get_paginator("describe_cache_security_groups")
    describe_cache_subnet_groups_paginator: DescribeCacheSubnetGroupsPaginator = client.get_paginator("describe_cache_subnet_groups")
    describe_engine_default_parameters_paginator: DescribeEngineDefaultParametersPaginator = client.get_paginator("describe_engine_default_parameters")
    describe_events_paginator: DescribeEventsPaginator = client.get_paginator("describe_events")
    describe_global_replication_groups_paginator: DescribeGlobalReplicationGroupsPaginator = client.get_paginator("describe_global_replication_groups")
    describe_replication_groups_paginator: DescribeReplicationGroupsPaginator = client.get_paginator("describe_replication_groups")
    describe_reserved_cache_nodes_paginator: DescribeReservedCacheNodesPaginator = client.get_paginator("describe_reserved_cache_nodes")
    describe_reserved_cache_nodes_offerings_paginator: DescribeReservedCacheNodesOfferingsPaginator = client.get_paginator("describe_reserved_cache_nodes_offerings")
    describe_service_updates_paginator: DescribeServiceUpdatesPaginator = client.get_paginator("describe_service_updates")
    describe_snapshots_paginator: DescribeSnapshotsPaginator = client.get_paginator("describe_snapshots")
    describe_update_actions_paginator: DescribeUpdateActionsPaginator = client.get_paginator("describe_update_actions")
    describe_user_groups_paginator: DescribeUserGroupsPaginator = client.get_paginator("describe_user_groups")
    describe_users_paginator: DescribeUsersPaginator = client.get_paginator("describe_users")
    ```
"""
from datetime import datetime
from typing import Generic, Iterator, Sequence, TypeVar, Union

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .literals import ServiceUpdateStatusType, SourceTypeType, UpdateActionStatusType
from .type_defs import (
    CacheClusterMessageTypeDef,
    CacheEngineVersionMessageTypeDef,
    CacheParameterGroupDetailsTypeDef,
    CacheParameterGroupsMessageTypeDef,
    CacheSecurityGroupMessageTypeDef,
    CacheSubnetGroupMessageTypeDef,
    DescribeEngineDefaultParametersResultTypeDef,
    DescribeGlobalReplicationGroupsResultTypeDef,
    DescribeSnapshotsListMessageTypeDef,
    DescribeUserGroupsResultTypeDef,
    DescribeUsersResultTypeDef,
    EventsMessageTypeDef,
    FilterTypeDef,
    PaginatorConfigTypeDef,
    ReplicationGroupMessageTypeDef,
    ReservedCacheNodeMessageTypeDef,
    ReservedCacheNodesOfferingMessageTypeDef,
    ServiceUpdatesMessageTypeDef,
    TimeRangeFilterTypeDef,
    UpdateActionsMessageTypeDef,
)

__all__ = (
    "DescribeCacheClustersPaginator",
    "DescribeCacheEngineVersionsPaginator",
    "DescribeCacheParameterGroupsPaginator",
    "DescribeCacheParametersPaginator",
    "DescribeCacheSecurityGroupsPaginator",
    "DescribeCacheSubnetGroupsPaginator",
    "DescribeEngineDefaultParametersPaginator",
    "DescribeEventsPaginator",
    "DescribeGlobalReplicationGroupsPaginator",
    "DescribeReplicationGroupsPaginator",
    "DescribeReservedCacheNodesPaginator",
    "DescribeReservedCacheNodesOfferingsPaginator",
    "DescribeServiceUpdatesPaginator",
    "DescribeSnapshotsPaginator",
    "DescribeUpdateActionsPaginator",
    "DescribeUserGroupsPaginator",
    "DescribeUsersPaginator",
)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class DescribeCacheClustersPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeCacheClusters)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describecacheclusterspaginator)
    """

    def paginate(
        self,
        *,
        CacheClusterId: str = ...,
        ShowCacheNodeInfo: bool = ...,
        ShowCacheClustersNotInReplicationGroups: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[CacheClusterMessageTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeCacheClusters.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describecacheclusterspaginator)
        """


class DescribeCacheEngineVersionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeCacheEngineVersions)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describecacheengineversionspaginator)
    """

    def paginate(
        self,
        *,
        Engine: str = ...,
        EngineVersion: str = ...,
        CacheParameterGroupFamily: str = ...,
        DefaultOnly: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[CacheEngineVersionMessageTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeCacheEngineVersions.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describecacheengineversionspaginator)
        """


class DescribeCacheParameterGroupsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeCacheParameterGroups)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describecacheparametergroupspaginator)
    """

    def paginate(
        self, *, CacheParameterGroupName: str = ..., PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[CacheParameterGroupsMessageTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeCacheParameterGroups.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describecacheparametergroupspaginator)
        """


class DescribeCacheParametersPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeCacheParameters)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describecacheparameterspaginator)
    """

    def paginate(
        self,
        *,
        CacheParameterGroupName: str,
        Source: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[CacheParameterGroupDetailsTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeCacheParameters.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describecacheparameterspaginator)
        """


class DescribeCacheSecurityGroupsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeCacheSecurityGroups)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describecachesecuritygroupspaginator)
    """

    def paginate(
        self, *, CacheSecurityGroupName: str = ..., PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[CacheSecurityGroupMessageTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeCacheSecurityGroups.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describecachesecuritygroupspaginator)
        """


class DescribeCacheSubnetGroupsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeCacheSubnetGroups)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describecachesubnetgroupspaginator)
    """

    def paginate(
        self, *, CacheSubnetGroupName: str = ..., PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[CacheSubnetGroupMessageTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeCacheSubnetGroups.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describecachesubnetgroupspaginator)
        """


class DescribeEngineDefaultParametersPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeEngineDefaultParameters)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describeenginedefaultparameterspaginator)
    """

    def paginate(
        self, *, CacheParameterGroupFamily: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeEngineDefaultParametersResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeEngineDefaultParameters.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describeenginedefaultparameterspaginator)
        """


class DescribeEventsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeEvents)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describeeventspaginator)
    """

    def paginate(
        self,
        *,
        SourceIdentifier: str = ...,
        SourceType: SourceTypeType = ...,
        StartTime: Union[datetime, str] = ...,
        EndTime: Union[datetime, str] = ...,
        Duration: int = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[EventsMessageTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeEvents.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describeeventspaginator)
        """


class DescribeGlobalReplicationGroupsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeGlobalReplicationGroups)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describeglobalreplicationgroupspaginator)
    """

    def paginate(
        self,
        *,
        GlobalReplicationGroupId: str = ...,
        ShowMemberInfo: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeGlobalReplicationGroupsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeGlobalReplicationGroups.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describeglobalreplicationgroupspaginator)
        """


class DescribeReplicationGroupsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeReplicationGroups)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describereplicationgroupspaginator)
    """

    def paginate(
        self, *, ReplicationGroupId: str = ..., PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ReplicationGroupMessageTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeReplicationGroups.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describereplicationgroupspaginator)
        """


class DescribeReservedCacheNodesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeReservedCacheNodes)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describereservedcachenodespaginator)
    """

    def paginate(
        self,
        *,
        ReservedCacheNodeId: str = ...,
        ReservedCacheNodesOfferingId: str = ...,
        CacheNodeType: str = ...,
        Duration: str = ...,
        ProductDescription: str = ...,
        OfferingType: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ReservedCacheNodeMessageTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeReservedCacheNodes.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describereservedcachenodespaginator)
        """


class DescribeReservedCacheNodesOfferingsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeReservedCacheNodesOfferings)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describereservedcachenodesofferingspaginator)
    """

    def paginate(
        self,
        *,
        ReservedCacheNodesOfferingId: str = ...,
        CacheNodeType: str = ...,
        Duration: str = ...,
        ProductDescription: str = ...,
        OfferingType: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ReservedCacheNodesOfferingMessageTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeReservedCacheNodesOfferings.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describereservedcachenodesofferingspaginator)
        """


class DescribeServiceUpdatesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeServiceUpdates)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describeserviceupdatespaginator)
    """

    def paginate(
        self,
        *,
        ServiceUpdateName: str = ...,
        ServiceUpdateStatus: Sequence[ServiceUpdateStatusType] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ServiceUpdatesMessageTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeServiceUpdates.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describeserviceupdatespaginator)
        """


class DescribeSnapshotsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeSnapshots)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describesnapshotspaginator)
    """

    def paginate(
        self,
        *,
        ReplicationGroupId: str = ...,
        CacheClusterId: str = ...,
        SnapshotName: str = ...,
        SnapshotSource: str = ...,
        ShowNodeGroupConfig: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeSnapshotsListMessageTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeSnapshots.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describesnapshotspaginator)
        """


class DescribeUpdateActionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeUpdateActions)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describeupdateactionspaginator)
    """

    def paginate(
        self,
        *,
        ServiceUpdateName: str = ...,
        ReplicationGroupIds: Sequence[str] = ...,
        CacheClusterIds: Sequence[str] = ...,
        Engine: str = ...,
        ServiceUpdateStatus: Sequence[ServiceUpdateStatusType] = ...,
        ServiceUpdateTimeRange: TimeRangeFilterTypeDef = ...,
        UpdateActionStatus: Sequence[UpdateActionStatusType] = ...,
        ShowNodeLevelUpdateStatus: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[UpdateActionsMessageTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeUpdateActions.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describeupdateactionspaginator)
        """


class DescribeUserGroupsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeUserGroups)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describeusergroupspaginator)
    """

    def paginate(
        self, *, UserGroupId: str = ..., PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeUserGroupsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeUserGroups.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describeusergroupspaginator)
        """


class DescribeUsersPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeUsers)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describeuserspaginator)
    """

    def paginate(
        self,
        *,
        Engine: str = ...,
        UserId: str = ...,
        Filters: Sequence[FilterTypeDef] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeUsersResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Paginator.DescribeUsers.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_elasticache/paginators/#describeuserspaginator)
        """
