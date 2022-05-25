from typing import List

from openapi_client.models.response_kernel_resource_spec import (
    ResponseKernelResourceSpec,
)
from vessl import vessl_api
from vessl.organization import _get_organization_name
from vessl.util.exception import InvalidKernelResourceSpecError


def read_kernel_resource_spec(
    cluster_id: int, kernel_resource_spec_name: str, **kwargs
) -> ResponseKernelResourceSpec:
    """Read kernel resource spec in the default organization. If you
    want to override the default organization, then pass `organization_name` as
    `**kwargs`.

    Args:
        cluster_id(int): Cluster ID.
        kernel_resource_spec_name(str): Kernel resource spec name.

    Example:
        ```python
        vessl.read_kernel_resource_spec(
            cluster_id=123,
            kernel_resource_spec_name="v1.cpu-4.mem-13",
        )
        ```
    """
    kernel_resource_specs = list_kernel_resource_specs(cluster_id, **kwargs)
    kernel_resource_specs = {x.name: x for x in kernel_resource_specs}

    if kernel_resource_spec_name not in kernel_resource_specs:
        import pdb

        pdb.set_trace()
        raise InvalidKernelResourceSpecError(
            f"Kernel resource spec not found: {kernel_resource_spec_name}"
        )
    return kernel_resource_specs[kernel_resource_spec_name]


def list_kernel_resource_specs(
    cluster_id: int,
    **kwargs,
) -> List[ResponseKernelResourceSpec]:
    """List kernel resource specs in the default organization. If you
    want to override the default organization, then pass `organization_name` as
    `**kwargs`.

    Args:
        cluster_id(int): Cluster ID.

    Example:
        ```python
        vessl.list_kernel_resource_specs(
            cluster_id=123,
        )
        ```
    """
    return vessl_api.kernel_resource_spec_list_api(
        cluster_id=cluster_id,
        organization_name=_get_organization_name(**kwargs),
    ).results


def _configure_custom_kernel_resource_spec(
    processor_type: str = None,
    cpu_limit: float = None,
    memory_limit: str = None,
    gpu_type: str = None,
    gpu_limit: int = None,
) -> ResponseKernelResourceSpec:
    return ResponseKernelResourceSpec(
        processor_type=processor_type,
        cpu_type="Any",
        cpu_limit=cpu_limit,
        memory_limit=memory_limit,
        gpu_type=gpu_type,
        gpu_limit=gpu_limit,
    )
