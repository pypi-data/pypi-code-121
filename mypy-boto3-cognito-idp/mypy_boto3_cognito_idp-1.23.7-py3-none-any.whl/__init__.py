"""
Main interface for cognito-idp service.

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_cognito_idp import (
        AdminListGroupsForUserPaginator,
        AdminListUserAuthEventsPaginator,
        Client,
        CognitoIdentityProviderClient,
        ListGroupsPaginator,
        ListIdentityProvidersPaginator,
        ListResourceServersPaginator,
        ListUserPoolClientsPaginator,
        ListUserPoolsPaginator,
        ListUsersInGroupPaginator,
        ListUsersPaginator,
    )

    session = Session()
    client: CognitoIdentityProviderClient = session.client("cognito-idp")

    admin_list_groups_for_user_paginator: AdminListGroupsForUserPaginator = client.get_paginator("admin_list_groups_for_user")
    admin_list_user_auth_events_paginator: AdminListUserAuthEventsPaginator = client.get_paginator("admin_list_user_auth_events")
    list_groups_paginator: ListGroupsPaginator = client.get_paginator("list_groups")
    list_identity_providers_paginator: ListIdentityProvidersPaginator = client.get_paginator("list_identity_providers")
    list_resource_servers_paginator: ListResourceServersPaginator = client.get_paginator("list_resource_servers")
    list_user_pool_clients_paginator: ListUserPoolClientsPaginator = client.get_paginator("list_user_pool_clients")
    list_user_pools_paginator: ListUserPoolsPaginator = client.get_paginator("list_user_pools")
    list_users_paginator: ListUsersPaginator = client.get_paginator("list_users")
    list_users_in_group_paginator: ListUsersInGroupPaginator = client.get_paginator("list_users_in_group")
    ```
"""
from .client import CognitoIdentityProviderClient
from .paginator import (
    AdminListGroupsForUserPaginator,
    AdminListUserAuthEventsPaginator,
    ListGroupsPaginator,
    ListIdentityProvidersPaginator,
    ListResourceServersPaginator,
    ListUserPoolClientsPaginator,
    ListUserPoolsPaginator,
    ListUsersInGroupPaginator,
    ListUsersPaginator,
)

Client = CognitoIdentityProviderClient


__all__ = (
    "AdminListGroupsForUserPaginator",
    "AdminListUserAuthEventsPaginator",
    "Client",
    "CognitoIdentityProviderClient",
    "ListGroupsPaginator",
    "ListIdentityProvidersPaginator",
    "ListResourceServersPaginator",
    "ListUserPoolClientsPaginator",
    "ListUserPoolsPaginator",
    "ListUsersInGroupPaginator",
    "ListUsersPaginator",
)
