"""
Main interface for elasticache service.

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_elasticache import (
        CacheClusterAvailableWaiter,
        CacheClusterDeletedWaiter,
        Client,
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
        DescribeReservedCacheNodesOfferingsPaginator,
        DescribeReservedCacheNodesPaginator,
        DescribeServiceUpdatesPaginator,
        DescribeSnapshotsPaginator,
        DescribeUpdateActionsPaginator,
        DescribeUserGroupsPaginator,
        DescribeUsersPaginator,
        ElastiCacheClient,
        ReplicationGroupAvailableWaiter,
        ReplicationGroupDeletedWaiter,
    )

    session = Session()
    client: ElastiCacheClient = session.client("elasticache")

    cache_cluster_available_waiter: CacheClusterAvailableWaiter = client.get_waiter("cache_cluster_available")
    cache_cluster_deleted_waiter: CacheClusterDeletedWaiter = client.get_waiter("cache_cluster_deleted")
    replication_group_available_waiter: ReplicationGroupAvailableWaiter = client.get_waiter("replication_group_available")
    replication_group_deleted_waiter: ReplicationGroupDeletedWaiter = client.get_waiter("replication_group_deleted")

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
from .client import ElastiCacheClient
from .paginator import (
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
    DescribeReservedCacheNodesOfferingsPaginator,
    DescribeReservedCacheNodesPaginator,
    DescribeServiceUpdatesPaginator,
    DescribeSnapshotsPaginator,
    DescribeUpdateActionsPaginator,
    DescribeUserGroupsPaginator,
    DescribeUsersPaginator,
)
from .waiter import (
    CacheClusterAvailableWaiter,
    CacheClusterDeletedWaiter,
    ReplicationGroupAvailableWaiter,
    ReplicationGroupDeletedWaiter,
)

Client = ElastiCacheClient


__all__ = (
    "CacheClusterAvailableWaiter",
    "CacheClusterDeletedWaiter",
    "Client",
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
    "DescribeReservedCacheNodesOfferingsPaginator",
    "DescribeReservedCacheNodesPaginator",
    "DescribeServiceUpdatesPaginator",
    "DescribeSnapshotsPaginator",
    "DescribeUpdateActionsPaginator",
    "DescribeUserGroupsPaginator",
    "DescribeUsersPaginator",
    "ElastiCacheClient",
    "ReplicationGroupAvailableWaiter",
    "ReplicationGroupDeletedWaiter",
)
