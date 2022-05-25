from typing import List

from openapi_client.models import OrmKernelImage, ResponseKernelImage
from vessl import vessl_api
from vessl.organization import _get_organization_name


def read_kernel_image(image_id: int) -> ResponseKernelImage:
    """Read the kernel image.

    Args:
        image_id(int): Image ID.

    Example:
        ```python
        vessl.read_kernel_image(
            image_id=1,
        )
        ```
    """
    return vessl_api.kernel_image_read_api(image_id=image_id)


def list_kernel_images(**kwargs) -> List[OrmKernelImage]:
    """List kernel images in the default organization. If you
    want to override the default organization, then pass `organization_name` as
    `**kwargs`.

    Example:
        ```python
        vessl.list_kernel_images()
        ```
    """
    return vessl_api.kernel_image_list_api(
        organization_name=_get_organization_name(**kwargs),
    ).results
