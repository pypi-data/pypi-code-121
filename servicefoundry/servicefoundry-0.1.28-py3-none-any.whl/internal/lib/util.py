from typing import List, Optional, Tuple, TypeVar, Union

import questionary

from servicefoundry.internal.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.internal.console import console
from servicefoundry.internal.lib.messages import (
    PROMPT_USING_CLUSTER_CONTEXT,
    PROMPT_USING_WORKSPACE_CONTEXT,
)
from servicefoundry.internal.model.entity import Cluster, Deployment, Service, Workspace

# TODO: Move type casting downwards into `ServiceFoundrySession` and `ServiceFoundryServiceClient`
# TODO: Abstract duplicated code across resolving different entities
T = TypeVar("T")


def _filter_by_attr_match(
    instances: List[T],
    value: Optional[str],
    attrs: Tuple[str, ...] = ("name", "fqn", "id"),
) -> List[T]:
    found = instances
    if value:
        for attr in attrs:
            found = [i for i in instances if getattr(i, attr, None) == value]
            if found:
                break
    return found


def all_clusters(client: ServiceFoundryServiceClient) -> List[Cluster]:
    clusters = [Cluster.from_dict(c) for c in client.list_cluster()]
    return clusters


def all_workspaces(client: ServiceFoundryServiceClient) -> List[Workspace]:
    workspaces = [Workspace.from_dict(w) for w in client.list_workspace()]
    return workspaces


def all_services(client: ServiceFoundryServiceClient) -> List[Service]:
    services = [Service.from_dict(s) for s in client.list_service()]
    return services


def all_deployments(client: ServiceFoundryServiceClient) -> List[Deployment]:
    # TODO (chiragjn): query in a loop! Make a single backend API
    services = all_services(client=client)
    deployments = []
    for service in services:
        deployments.extend(
            [
                Deployment.from_dict(d)
                for d in client.list_deployment(service_id=service.id)
            ]
        )
    return deployments


def get_cluster_from_context(client: ServiceFoundryServiceClient) -> Optional[Cluster]:
    cluster = client.session.get_cluster()
    if cluster:
        cluster = Cluster.from_dict(cluster)
    return cluster


def get_workspace_from_context(
    client: ServiceFoundryServiceClient,
) -> Optional[Workspace]:
    workspace = client.session.get_workspace()
    if workspace:
        workspace = Workspace.from_dict(workspace)
    return workspace


def resolve_clusters(
    client: ServiceFoundryServiceClient,
    name_or_id: Optional[str] = None,
    ignore_context: bool = False,
) -> List[Cluster]:
    if not ignore_context and not name_or_id:
        cluster = get_cluster_from_context(client=client)
        if cluster:
            return [cluster]

    clusters = all_clusters(client=client)
    return _filter_by_attr_match(
        instances=clusters, value=name_or_id, attrs=("name", "fqn", "id")
    )


def resolve_workspaces(
    client: ServiceFoundryServiceClient,
    name_or_id: Optional[str] = None,
    cluster_name_or_id: Optional[Union[Cluster, str]] = None,
    ignore_context: bool = False,
) -> List[Workspace]:
    if not ignore_context and not name_or_id:
        workspace = get_workspace_from_context(client=client)
        if workspace:
            return [workspace]

    if isinstance(cluster_name_or_id, Cluster):
        clusters = [cluster_name_or_id]
        cluster_name_or_id = clusters[0].id
    else:
        clusters = resolve_clusters(
            client=client, name_or_id=cluster_name_or_id, ignore_context=ignore_context
        )

    if not clusters:
        if cluster_name_or_id:
            raise ValueError(f"No cluster found with name or id {cluster_name_or_id!r}")
        else:
            raise ValueError("Unable to resolve clusters without a name or id")
    elif len(clusters) == 1:
        cluster = clusters[0]
        _workspaces = client.get_workspace_by_name(
            workspace_name="", cluster_id=cluster.id
        )
        workspaces = [Workspace.from_dict(w) for w in _workspaces]
    else:
        if cluster_name_or_id:
            raise ValueError(
                f"More than one cluster found with name or id {cluster_name_or_id!r}: {clusters!r}"
            )
        else:
            # TODO (chiragjn): optimize this, we have wasted a call to v1/cluster
            workspaces = all_workspaces(client=client)

    return _filter_by_attr_match(
        instances=workspaces, value=name_or_id, attrs=("name", "fqn", "id")
    )


def resolve_services(
    client: ServiceFoundryServiceClient,
    name_or_id: Optional[str] = None,
    workspace_name_or_id: Optional[Union[Workspace, str]] = None,
    cluster_name_or_id: Optional[Union[Cluster, str]] = None,
    ignore_context: bool = False,
) -> List[Service]:
    if isinstance(workspace_name_or_id, Workspace):
        workspaces = [workspace_name_or_id]
        workspace_name_or_id = workspaces[0].id
    else:
        workspaces = resolve_workspaces(
            client=client,
            name_or_id=workspace_name_or_id,
            cluster_name_or_id=cluster_name_or_id,
            ignore_context=ignore_context,
        )
    if not workspaces:
        if workspace_name_or_id:
            raise ValueError(
                f"No workspaces found with name or id {workspace_name_or_id!r}"
            )
        else:
            raise ValueError("Unable to resolve workspaces without a name or id")
    elif len(workspaces) == 1:
        workspace = workspaces[0]
        _services = client.list_service_by_workspace(workspace_id=workspace.id)
        services = [Service.from_dict(s) for s in _services]
    else:
        if workspace_name_or_id:
            raise ValueError(
                f"More than one workspace found with name or id {workspace_name_or_id!r}: {workspaces!r}"
            )
        else:
            services = all_services(client=client)

    return _filter_by_attr_match(
        instances=services, value=name_or_id, attrs=("name", "fqn", "id")
    )


def resolve_deployments(
    client: ServiceFoundryServiceClient,
    name_or_id: Optional[str] = None,
    service_name_or_id: Optional[Union[Service, str]] = None,
    workspace_name_or_id: Optional[Union[Workspace, str]] = None,
    cluster_name_or_id: Optional[Union[Cluster, str]] = None,
    ignore_context: bool = False,
) -> List[Deployment]:
    if isinstance(service_name_or_id, Service):
        services = [service_name_or_id]
        service_name_or_id = services[0].id
    else:
        services = resolve_services(
            client=client,
            name_or_id=service_name_or_id,
            workspace_name_or_id=workspace_name_or_id,
            cluster_name_or_id=cluster_name_or_id,
            ignore_context=ignore_context,
        )
    if not services:
        if service_name_or_id:
            raise ValueError(
                f"No services found with name or id {service_name_or_id!r}"
            )
        else:
            raise ValueError("Unable to resolve services without a name or id")
    elif len(services) == 1:
        service = services[0]
        _deployments = client.list_deployment(service_id=service.id)
        deployments = [Deployment.from_dict(d) for d in _deployments]
    else:
        if service_name_or_id:
            raise ValueError(
                f"More than one service found with name or id {service_name_or_id!r}: {services!r}"
            )
        else:
            raise NotImplementedError(
                "Cannot fetch deployments without a service name or id"
            )
            # TODO (chiragjn): Needs an API from server side to fetch all deployments.
            #                  Otherwise we can do it slowly by doing
            #                  flatten([c.list_deployment(service_id=s.id) for s in all_services])

    return _filter_by_attr_match(
        instances=deployments, value=name_or_id, attrs=("name", "fqn", "id")
    )


def ask_pick_cluster(clusters: List[Cluster]) -> Cluster:
    choices = [
        questionary.Choice(title=f"{c.name} ({c.fqn})", value=c) for c in clusters
    ]
    return questionary.select("Pick a cluster", choices=choices).ask()


def maybe_ask_pick_cluster(clusters: List[Cluster]) -> Cluster:
    if len(clusters) == 1:
        return clusters[0]
    return ask_pick_cluster(clusters=clusters)


def ask_pick_workspace(workspaces: List[Workspace]) -> Workspace:
    choices = [
        questionary.Choice(title=f"{w.name} ({w.fqn})", value=w) for w in workspaces
    ]
    return questionary.select("Pick a workspace", choices=choices).ask()


def maybe_ask_pick_workspace(workspaces: List[Workspace]) -> Workspace:
    if len(workspaces) == 1:
        return workspaces[0]
    return ask_pick_workspace(workspaces=workspaces)


def ask_pick_service(services: List[Service]) -> Service:
    choices = [
        questionary.Choice(title=f"{s.name} ({s.fqn})", value=s) for s in services
    ]
    return questionary.select("Pick a service", choices=choices).ask()


def maybe_ask_pick_service(services: List[Service]) -> Service:
    if len(services) == 1:
        return services[0]
    return ask_pick_service(services=services)


def ask_pick_deployment(deployments: List[Deployment]) -> Deployment:
    choices = [
        questionary.Choice(title=f"{d.name} ({d.fqn})", value=d) for d in deployments
    ]
    return questionary.select("Pick a deployment", choices=choices).ask()


def maybe_ask_pick_deployment(deployments: List[Deployment]) -> Deployment:
    if len(deployments) == 1:
        return deployments[0]
    return ask_pick_deployment(deployments=deployments)


def resolve_cluster_or_error(
    name_or_id: Optional[str] = None,
    ignore_context: bool = False,
    non_interactive: bool = True,
    client: Optional[ServiceFoundryServiceClient] = None,
) -> Cluster:
    if non_interactive:
        if ignore_context and not name_or_id:
            raise ValueError("cluster name or id cannot be null")

    clusters = resolve_clusters(
        client=client, name_or_id=name_or_id, ignore_context=ignore_context
    )

    if not clusters:
        if name_or_id:
            raise ValueError(f"No cluster found with name or id {name_or_id!r}")
        else:
            raise ValueError(f"No clusters found!")
    else:
        if non_interactive:
            if len(clusters) > 1:
                raise ValueError(
                    f"More than one cluster found with name or id {name_or_id!r}: {clusters!r}"
                )
            else:
                cluster = clusters[0]
        else:
            cluster = maybe_ask_pick_cluster(clusters=clusters)
    return cluster


def resolve_workspace_or_error(
    name_or_id: Optional[str] = None,
    cluster_name_or_id: Optional[Union[Cluster, str]] = None,
    ignore_context: bool = False,
    non_interactive: bool = True,
    client: Optional[ServiceFoundryServiceClient] = None,
) -> Tuple[Workspace, Cluster]:
    if non_interactive:
        if ignore_context and not name_or_id:
            raise ValueError("workspace name or id cannot be null")

    if isinstance(cluster_name_or_id, Cluster):
        cluster = cluster_name_or_id
    else:
        cluster = resolve_cluster_or_error(
            name_or_id=cluster_name_or_id,
            non_interactive=non_interactive,
            ignore_context=ignore_context,
            client=client,
        )

    console.print(PROMPT_USING_CLUSTER_CONTEXT.format(cluster.name))

    workspaces = resolve_workspaces(
        client=client,
        name_or_id=name_or_id,
        cluster_name_or_id=cluster,
        ignore_context=ignore_context,
    )
    if not workspaces:
        if name_or_id:
            raise ValueError(
                f"No workspace found with name or id {name_or_id!r} in cluster {cluster.name!r}"
            )
        else:
            raise ValueError(f"No workspaces found!")
    else:
        if non_interactive:
            if len(workspaces) > 1:
                raise ValueError(
                    f"More than one workspace found with name or id {name_or_id!r}: {workspaces!r}"
                )
            else:
                workspace = workspaces[0]
        else:
            workspace = maybe_ask_pick_workspace(workspaces=workspaces)
    return workspace, cluster


def resolve_service_or_error(
    name_or_id: str,
    workspace_name_or_id: Optional[Union[Workspace, str]] = None,
    cluster_name_or_id: Optional[Union[Cluster, str]] = None,
    ignore_context: bool = False,
    non_interactive: bool = True,
    client: Optional[ServiceFoundryServiceClient] = None,
) -> Tuple[Service, Workspace, Cluster]:
    if non_interactive:
        if ignore_context and not name_or_id:
            raise ValueError("service name or id cannot be null")

    if isinstance(cluster_name_or_id, Cluster):
        cluster = cluster_name_or_id
    else:
        cluster = resolve_cluster_or_error(
            name_or_id=cluster_name_or_id,
            non_interactive=non_interactive,
            ignore_context=ignore_context,
            client=client,
        )

    if isinstance(workspace_name_or_id, Workspace):
        workspace = workspace_name_or_id
    else:
        workspace, cluster = resolve_workspace_or_error(
            name_or_id=workspace_name_or_id,
            cluster_name_or_id=cluster,
            non_interactive=non_interactive,
            ignore_context=ignore_context,
            client=client,
        )

    console.print(PROMPT_USING_WORKSPACE_CONTEXT.format(workspace.name))

    services = resolve_services(
        client=client,
        name_or_id=name_or_id,
        workspace_name_or_id=workspace,
        cluster_name_or_id=cluster,
        ignore_context=ignore_context,
    )

    if not services:
        if name_or_id:
            raise ValueError(
                f"No service found with name or id {name_or_id!r} in workspace {workspace.name!r}"
            )
        else:
            raise ValueError(f"No services found!")
    else:
        if non_interactive:
            if len(services) > 1:
                raise ValueError(
                    f"More than one service found with name or id {name_or_id!r}: {services!r}"
                )
            else:
                service = services[0]
        else:
            service = maybe_ask_pick_service(services=services)

    return service, workspace, cluster


def resolve_deployment_or_error(
    name_or_id: str,
    service_name_or_id: Optional[Union[Service, str]] = None,
    workspace_name_or_id: Optional[Union[Workspace, str]] = None,
    cluster_name_or_id: Optional[Union[Cluster, str]] = None,
    ignore_context: bool = False,
    non_interactive: bool = True,
    client: Optional[ServiceFoundryServiceClient] = None,
) -> Tuple[Deployment, Service, Workspace, Cluster]:
    if non_interactive:
        if ignore_context and not name_or_id:
            raise ValueError("deployment name or id cannot be null")

    # TODO: resolve separately if we start to have a get all deployments API that can give deployments across services
    service, workspace, cluster = resolve_service_or_error(
        name_or_id=service_name_or_id,
        workspace_name_or_id=workspace_name_or_id,
        cluster_name_or_id=cluster_name_or_id,
        ignore_context=ignore_context,
        non_interactive=non_interactive,
        client=client,
    )

    deployments = resolve_deployments(
        client=client,
        service_name_or_id=service,
        name_or_id=name_or_id,
        workspace_name_or_id=workspace,
        cluster_name_or_id=cluster,
        ignore_context=ignore_context,
    )

    if not deployments:
        if name_or_id:
            raise ValueError(
                f"No deployment found with name or id {name_or_id!r} for service {service.name!r}"
            )
        else:
            raise ValueError(f"No deployments found!")
    else:
        if non_interactive:
            if len(deployments) > 1:
                raise ValueError(
                    f"More than one deployment found with name or id {name_or_id!r}: {deployments!r}"
                )
            else:
                deployment = deployments[0]
        else:
            deployment = maybe_ask_pick_deployment(deployments=deployments)

    return deployment, service, workspace, cluster
