from typing import List, Optional

from servicefoundry.internal.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.internal.lib.util import (
    all_deployments,
    resolve_deployment_or_error,
    resolve_deployments,
    resolve_service_or_error,
)
from servicefoundry.internal.model.entity import Deployment


def get_deployment(
    name_or_id: str,
    service_name_or_id: Optional[str] = None,
    workspace_name_or_id: Optional[str] = None,
    cluster_name_or_id: Optional[str] = None,
    non_interactive: bool = True,
    client: Optional[ServiceFoundryServiceClient] = None,
) -> Deployment:
    client = client or ServiceFoundryServiceClient.get_client()
    deployment, _, _, _ = resolve_deployment_or_error(
        name_or_id=name_or_id,
        service_name_or_id=service_name_or_id,
        cluster_name_or_id=cluster_name_or_id,
        workspace_name_or_id=workspace_name_or_id,
        non_interactive=non_interactive,
        client=client,
    )
    return deployment


def list_deployments(
    service_name_or_id: Optional[str] = None,
    workspace_name_or_id: Optional[str] = None,
    cluster_name_or_id: Optional[str] = None,
    all_: bool = False,
    non_interactive: bool = True,
    client: Optional[ServiceFoundryServiceClient] = None,
) -> List[Deployment]:
    client = client or ServiceFoundryServiceClient.get_client()
    if all_:
        deployments = all_deployments(client=client)
    else:
        service, workspace, cluster = resolve_service_or_error(
            name_or_id=service_name_or_id,
            workspace_name_or_id=workspace_name_or_id,
            cluster_name_or_id=cluster_name_or_id,
            non_interactive=non_interactive,
            client=client,
        )
        deployments = resolve_deployments(
            client=client,
            name_or_id=None,
            service_name_or_id=service,
            workspace_name_or_id=workspace,
            cluster_name_or_id=cluster,
            ignore_context=True,
        )
    return deployments
