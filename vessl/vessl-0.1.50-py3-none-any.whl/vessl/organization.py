from typing import List

from openapi_client.models import (
    OrganizationCreateAPIInput,
    ResponseOrganization,
    ResponseOrganizationInfo,
)
from vessl import vessl_api
from vessl.util.exception import InvalidOrganizationError


def read_organization(organization_name: str) -> ResponseOrganizationInfo:
    """Read organization

    Args:
        organization_name(str): Organization name.

    Example:
        ```python
        vessl.read_organization(
            organization_name="foo"
        )
        ```
    """
    return vessl_api.organization_read_api(organization_name=organization_name)


def list_organizations() -> List[ResponseOrganization]:
    """List organizations

    Example:
        ```python
        vessl.list_organizations()
        ```
    """
    return vessl_api.organization_list_api().organizations


def create_organization(
    organization_name: str,
) -> ResponseOrganizationInfo:
    """Create oragnization

    Args:
        organization_name(str): Organization name.
        region(str): Physical location where your cluster data centers.

    Example:
        ```python
        vessl.create_organization(
            organization_name="foo",
            region="ap-northeast-2",
        )
        ```
    """
    return vessl_api.organization_create_api(
        organization_create_api_input=OrganizationCreateAPIInput(
            name=organization_name,
        )
    )


def _get_organization_name(**kwargs) -> str:
    organization_name = kwargs.get("organization_name")
    if organization_name is not None:
        return organization_name
    if vessl_api.organization is not None:
        return vessl_api.organization.name
    raise InvalidOrganizationError("No organization selected.")
