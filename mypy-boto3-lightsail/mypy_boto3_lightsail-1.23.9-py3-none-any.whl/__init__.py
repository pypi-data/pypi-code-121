"""
Main interface for lightsail service.

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_lightsail import (
        Client,
        GetActiveNamesPaginator,
        GetBlueprintsPaginator,
        GetBundlesPaginator,
        GetCloudFormationStackRecordsPaginator,
        GetDiskSnapshotsPaginator,
        GetDisksPaginator,
        GetDomainsPaginator,
        GetExportSnapshotRecordsPaginator,
        GetInstanceSnapshotsPaginator,
        GetInstancesPaginator,
        GetKeyPairsPaginator,
        GetLoadBalancersPaginator,
        GetOperationsPaginator,
        GetRelationalDatabaseBlueprintsPaginator,
        GetRelationalDatabaseBundlesPaginator,
        GetRelationalDatabaseEventsPaginator,
        GetRelationalDatabaseParametersPaginator,
        GetRelationalDatabaseSnapshotsPaginator,
        GetRelationalDatabasesPaginator,
        GetStaticIpsPaginator,
        LightsailClient,
    )

    session = Session()
    client: LightsailClient = session.client("lightsail")

    get_active_names_paginator: GetActiveNamesPaginator = client.get_paginator("get_active_names")
    get_blueprints_paginator: GetBlueprintsPaginator = client.get_paginator("get_blueprints")
    get_bundles_paginator: GetBundlesPaginator = client.get_paginator("get_bundles")
    get_cloud_formation_stack_records_paginator: GetCloudFormationStackRecordsPaginator = client.get_paginator("get_cloud_formation_stack_records")
    get_disk_snapshots_paginator: GetDiskSnapshotsPaginator = client.get_paginator("get_disk_snapshots")
    get_disks_paginator: GetDisksPaginator = client.get_paginator("get_disks")
    get_domains_paginator: GetDomainsPaginator = client.get_paginator("get_domains")
    get_export_snapshot_records_paginator: GetExportSnapshotRecordsPaginator = client.get_paginator("get_export_snapshot_records")
    get_instance_snapshots_paginator: GetInstanceSnapshotsPaginator = client.get_paginator("get_instance_snapshots")
    get_instances_paginator: GetInstancesPaginator = client.get_paginator("get_instances")
    get_key_pairs_paginator: GetKeyPairsPaginator = client.get_paginator("get_key_pairs")
    get_load_balancers_paginator: GetLoadBalancersPaginator = client.get_paginator("get_load_balancers")
    get_operations_paginator: GetOperationsPaginator = client.get_paginator("get_operations")
    get_relational_database_blueprints_paginator: GetRelationalDatabaseBlueprintsPaginator = client.get_paginator("get_relational_database_blueprints")
    get_relational_database_bundles_paginator: GetRelationalDatabaseBundlesPaginator = client.get_paginator("get_relational_database_bundles")
    get_relational_database_events_paginator: GetRelationalDatabaseEventsPaginator = client.get_paginator("get_relational_database_events")
    get_relational_database_parameters_paginator: GetRelationalDatabaseParametersPaginator = client.get_paginator("get_relational_database_parameters")
    get_relational_database_snapshots_paginator: GetRelationalDatabaseSnapshotsPaginator = client.get_paginator("get_relational_database_snapshots")
    get_relational_databases_paginator: GetRelationalDatabasesPaginator = client.get_paginator("get_relational_databases")
    get_static_ips_paginator: GetStaticIpsPaginator = client.get_paginator("get_static_ips")
    ```
"""
from .client import LightsailClient
from .paginator import (
    GetActiveNamesPaginator,
    GetBlueprintsPaginator,
    GetBundlesPaginator,
    GetCloudFormationStackRecordsPaginator,
    GetDiskSnapshotsPaginator,
    GetDisksPaginator,
    GetDomainsPaginator,
    GetExportSnapshotRecordsPaginator,
    GetInstanceSnapshotsPaginator,
    GetInstancesPaginator,
    GetKeyPairsPaginator,
    GetLoadBalancersPaginator,
    GetOperationsPaginator,
    GetRelationalDatabaseBlueprintsPaginator,
    GetRelationalDatabaseBundlesPaginator,
    GetRelationalDatabaseEventsPaginator,
    GetRelationalDatabaseParametersPaginator,
    GetRelationalDatabaseSnapshotsPaginator,
    GetRelationalDatabasesPaginator,
    GetStaticIpsPaginator,
)

Client = LightsailClient


__all__ = (
    "Client",
    "GetActiveNamesPaginator",
    "GetBlueprintsPaginator",
    "GetBundlesPaginator",
    "GetCloudFormationStackRecordsPaginator",
    "GetDiskSnapshotsPaginator",
    "GetDisksPaginator",
    "GetDomainsPaginator",
    "GetExportSnapshotRecordsPaginator",
    "GetInstanceSnapshotsPaginator",
    "GetInstancesPaginator",
    "GetKeyPairsPaginator",
    "GetLoadBalancersPaginator",
    "GetOperationsPaginator",
    "GetRelationalDatabaseBlueprintsPaginator",
    "GetRelationalDatabaseBundlesPaginator",
    "GetRelationalDatabaseEventsPaginator",
    "GetRelationalDatabaseParametersPaginator",
    "GetRelationalDatabaseSnapshotsPaginator",
    "GetRelationalDatabasesPaginator",
    "GetStaticIpsPaginator",
    "LightsailClient",
)
