import pathlib
import re
from typing import Any, Callable, Dict, List, Optional, Sequence, Union, cast

from tktl.core.exceptions import TaktileSdkError
from tktl.core.loggers import LOG
from tktl.core.schemas.repository import (
    Endpoint,
    Repository,
    RepositoryDeployment,
    Resources,
)


def default_comp(x: Any, y: Any):
    return x == y


def branch_comp(x: str, y: str):
    return x == y or y == f"refs/heads/{x}"


def is_in_sequence_comp(x: Sequence, y: str):
    return y in set(x)


def filter_prop(
    resources: Sequence[Resources],
    prop_name: str,
    value: Any,
    key: Callable = default_comp,
):
    if value is not None:
        return [d for d in resources if key(value, getattr(d, prop_name))]
    return resources


def filter_deployments(
    deployments: List[RepositoryDeployment],
    git_hash: Optional[str] = None,
    branch_name: Optional[str] = None,
    status_name: Union[str, List[str], None] = None,
) -> List[RepositoryDeployment]:
    for n, v in zip(
        ["commit_hash", "git_ref", "status"], [git_hash, branch_name, status_name]
    ):
        if n == "git_ref":
            comp = branch_comp
        elif n == "commit_hash" and git_hash:
            if len(git_hash) < 40:

                def comp(x: str, y: str):
                    return y.startswith(x)

            else:
                comp = default_comp
        elif n == "status":
            if isinstance(status_name, list):
                comp = is_in_sequence_comp
            else:
                comp = default_comp
        else:
            comp = default_comp
        deployments = filter_prop(deployments, prop_name=n, value=v, key=comp)

    return deployments


def filter_repositories(
    repositories: List[Repository],
    repository_name: Optional[str] = None,
    repository_owner: Optional[str] = None,
) -> List[Repository]:
    for n, v in zip(
        ["repository_name", "repository_owner"], [repository_name, repository_owner]
    ):
        repositories = filter_prop(repositories, prop_name=n, value=v)
    return repositories


def filter_endpoints(
    endpoints: List[Endpoint],
    endpoint_name: Optional[str] = None,
    endpoint_kind: Optional[str] = None,
) -> List[Endpoint]:

    for n, v in zip(["name", "kind"], [endpoint_name, endpoint_kind]):
        endpoints = filter_prop(endpoints, prop_name=n, value=v)
    return endpoints


def get_deployment_from_endpoint_and_branch(
    endpoint_mapping: List[Dict[str, Union[Endpoint, RepositoryDeployment]]],
    endpoint_name: str,
    branch_name: str = None,
) -> Optional[RepositoryDeployment]:
    filtered = [
        e
        for e in endpoint_mapping
        if e and cast(Endpoint, e["endpoint"]).name == endpoint_name
    ]
    if len(filtered) == 0:
        LOG.warning(
            f"No endpoints with name: {endpoint_name} found across all deployed branches"
        )
        return None
    if len(filtered) == 1:
        deployment = cast(RepositoryDeployment, filtered[0]["deployment"])
        if branch_name is not None and not branch_comp(deployment.git_ref, branch_name):
            base_name = pathlib.Path(deployment.git_ref).name
            LOG.warning(
                f"No endpoint {endpoint_name} for branch {branch_name}, but found one for branch: "
                f"{base_name}. Returning that instead"
            )
        return deployment
    else:
        available_branches = set(
            [
                pathlib.Path(cast(RepositoryDeployment, e["deployment"]).git_ref).name
                for e in endpoint_mapping
            ]
        )
        if branch_name is None:
            LOG.warning(
                f"Ambiguous: more than one branch for repository with endpoint: {endpoint_name}. Please "
                f"specify a branch. Available branches: with such endpoint: {', '.join(available_branches)}"
            )
            return None
        branch_filtered = [
            e
            for e in filtered
            if branch_comp(
                cast(RepositoryDeployment, e["deployment"]).git_ref, branch_name
            )
        ]
        if len(branch_filtered) == 0:
            LOG.warning(
                f"No endpoints with name: {endpoint_name} and branch {branch_name} found. Available "
                f"branches with such endpoint: {', '.join(available_branches)}"
            )
            return None
        elif len(branch_filtered) == 1:
            return cast(RepositoryDeployment, branch_filtered[0]["deployment"])
        else:
            # Impossible to have more than one endpoint in the same branch for the same repo with the same name
            raise TaktileSdkError("This should never, ever happen")


def parse_remote_url(remote_url: str):
    match = re.findall(r"(?<=github.com).*", remote_url)
    return pathlib.Path(match[0].strip("/").strip(":")).stem if match else ""
