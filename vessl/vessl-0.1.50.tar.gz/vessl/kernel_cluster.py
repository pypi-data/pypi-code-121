from typing import List

from openapi_client.models import (
    ClusterUpdateAPIInput,
    ResponseKernelClusterInfo,
    ResponseKernelClusterNodeInfo,
)
from vessl import vessl_api
from vessl.organization import _get_organization_name
from vessl.util.exception import InvalidKernelClusterError


def read_cluster(cluster_name: str, **kwargs) -> ResponseKernelClusterInfo:
    """Read cluster in the default organization. If you want to override the
    default organization, then pass `organization_name` as `**kwargs`.

    Args:
        cluster_name(str): Cluster name.

    Example:
        ```python
        vessl.read_cluster(
            cluster_name="seoul-cluster",
        )
        ```
    """
    kernel_clusters = list_clusters(**kwargs)
    kernel_clusters = {x.name: x for x in kernel_clusters}

    if cluster_name not in kernel_clusters:
        raise InvalidKernelClusterError(f"Kernel cluster not found: {cluster_name}")
    return kernel_clusters[cluster_name]


def list_clusters(**kwargs) -> List[ResponseKernelClusterInfo]:
    """List clusters in the default organization. If you want to override the
    default organization, then pass `organization_name` as `**kwargs`.

    Example:
        ```python
        vessl.list_clusters()
        ```
    """
    return vessl_api.cluster_list_api(
        organization_name=_get_organization_name(**kwargs),
    ).clusters


def delete_cluster(cluster_id: int, **kwargs) -> object:
    """Delete custom cluster in the default organization. If you want to
    override the default organization, then pass `organization_name` as
    `**kwargs`.

    Args:
        cluster_id(int): Cluster ID.

    Example:
        ```python
        vessl.delete_cluster(
            cluster_id=1,
        )
        ```
    """
    return vessl_api.custom_cluster_delete_api(
        cluster_id=cluster_id,
        organization_name=_get_organization_name(**kwargs),
    )


def rename_cluster(
    cluster_id: int, new_cluster_name: str, **kwargs
) -> ResponseKernelClusterInfo:
    """Rename custom cluster in the default organization. If you want to
    override the default organization, then pass `organization_name` as
    `**kwargs`.

    Args:
        cluster_id(int): Cluster ID.
        new_cluster_name(str): Cluster name to change.

    Example:
        ```python
        vessl.rename_cluster(
            cluster_id=1,
            new_cluster_name="seoul-cluster-2",
        )
        ```
    """
    return vessl_api.custom_cluster_update_api(
        cluster_id=cluster_id,
        organization_name=_get_organization_name(**kwargs),
        custom_cluster_update_api_input=ClusterUpdateAPIInput(
            name=new_cluster_name,
        ),
    )


def list_cluster_nodes(
    cluster_id: int, **kwargs
) -> List[ResponseKernelClusterNodeInfo]:
    """List custom cluster nodes in the default organization. If you want to
    override the default organization, then pass `organization_name` as
    `**kwargs`.

    Args:
        cluster_id(int): Cluster ID.

    Example:
        ```python
        vessl.list_cluster_nodes(
            cluster_id=1,
        )
        ```
    """
    return vessl_api.custom_cluster_node_list_api(
        cluster_id=cluster_id,
        organization_name=_get_organization_name(**kwargs),
    ).nodes
