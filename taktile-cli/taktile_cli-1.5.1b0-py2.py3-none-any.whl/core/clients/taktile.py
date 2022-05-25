from json import JSONDecodeError
from typing import List, Optional, Tuple

from pydantic import UUID4, ValidationError
from taktile_client.config import collect_api_key
from taktile_client.http_client import API

from tktl.constants import URL_UNAVAILABLE
from tktl.core.clients.utils import (
    filter_deployments,
    filter_endpoints,
    filter_prop,
    filter_repositories,
)
from tktl.core.config import settings
from tktl.core.exceptions import APIClientException, TaktileSdkError
from tktl.core.loggers import LOG, Logger
from tktl.core.schemas.deployment import DeploymentBase
from tktl.core.schemas.future.service import InfoEndpointResponseModel
from tktl.core.schemas.repository import (
    Endpoint,
    Repository,
    RepositoryDeployment,
    RepositorySecret,
    UserRepository,
    _format_http_url,
)
from tktl.core.t import DeploymentStatesT
from tktl.core.utils import flatten, lru_cache


class TaktileApiClient(API):
    SCHEME: str

    def __init__(self, logger: Logger = LOG):
        """
        Base class. All client classes inherit from it.
        """
        super().__init__(api_base=settings.TAKTILE_API_URL, api_key=collect_api_key())
        self.api_key = collect_api_key()
        self.logger = logger

    def get_repository_secret_names(self, repository_id: UUID4):
        return self.call(
            verb="get",
            path=f"{settings.API_V1_STR}/secrets/names/{repository_id}",
            model=RepositorySecret,
        )

    def get_user_repositories(self) -> List[UserRepository]:
        return self.call(
            verb="get", path=f"{settings.API_V1_STR}/repositories", model=UserRepository
        )

    def get_secrets_for_local_repository(
        self, secrets_repository: str
    ) -> List[RepositorySecret]:
        user_repositories = self.get_user_repositories()
        repo = filter_prop(
            resources=user_repositories,
            prop_name="full_name",
            value=secrets_repository,
        )
        if not repo:
            raise TaktileSdkError(
                f"No remote repositories with Taktile installed named: `{secrets_repository}`"
            )
        elif len(repo) > 1:
            raise TaktileSdkError(
                f"More than one remote repository found named `{secrets_repository}`"
            )
        else:
            repo = repo[0]
        secrets = self.get_repository_secret_names(repository_id=repo.id)
        return secrets


class DeploymentApiClient(API):
    SCHEME: str

    def __init__(self, logger: Logger = LOG):
        _api_key = collect_api_key()
        super().__init__(api_base=settings.DEPLOYMENT_API_URL, api_key=_api_key)
        self.api_key = _api_key
        self.logger = logger

    @lru_cache(timeout=50, typed=False)
    def __get_repositories(self) -> List[Repository]:
        return self.call(
            verb="get", path=f"{settings.API_V1_STR}/models", model=Repository
        )

    def _get_repositories(self) -> List[Repository]:
        repositories = self.__get_repositories()
        if not repositories:
            raise TaktileSdkError(
                "No repositories found on your account, so no resources can be fetched"
            )
        return repositories

    def get_deployments(
        self,
        repository_id: Optional[UUID4],
        git_hash: Optional[str],
        branch_name: Optional[str],
        status_name: Optional[str],
        repository_name: Optional[str],
        repository_owner: Optional[str],
        return_all: bool,
    ) -> Optional[List[RepositoryDeployment]]:

        repositories = filter_repositories(
            self._get_repositories(),
            repository_name=repository_name,
            repository_owner=repository_owner,
        )

        if repository_id:
            repo = [r for r in repositories if r.id == repository_id]
            if not repo:
                LOG.warning("No repositories with matching id found")
                return None
            else:
                deployments = repo[0].deployments
        else:
            deployments = flatten([r.deployments for r in repositories])

        if return_all:
            filtered_deployments = deployments
        else:
            filtered_deployments = filter_deployments(
                deployments,
                git_hash=git_hash,
                branch_name=branch_name,
                status_name=status_name,
            )

        def get_number_of_endpoints(deployment: RepositoryDeployment):
            try:
                return len(get_endpoints_for_deployment(deployment))
            except (JSONDecodeError, APIClientException):
                return 0

        endpoints_for_deployment = [
            get_number_of_endpoints(deployment) for deployment in filtered_deployments
        ]
        for e, d in zip(endpoints_for_deployment, filtered_deployments):
            d.n_endpoints = e
        return filtered_deployments

    def get_repositories(
        self,
        repository_name: Optional[str] = None,
        repository_owner: Optional[str] = None,
        return_all: bool = False,
    ) -> List[Repository]:
        repositories = self._get_repositories()
        if return_all:
            return repositories
        return filter_repositories(
            repositories,
            repository_name=repository_name,
            repository_owner=repository_owner,
        )

    def get_endpoints(
        self,
        deployment_id: Optional[UUID4] = None,
        endpoint_kind: Optional[str] = None,
        endpoint_name: Optional[str] = None,
        repository_name: Optional[str] = None,
        repository_owner: Optional[str] = None,
        git_hash: Optional[str] = None,
        branch_name: Optional[str] = None,
        status_name: Optional[str] = None,
        return_all: bool = False,
    ) -> List[Endpoint]:
        repositories = filter_repositories(
            self._get_repositories(),
            repository_name=repository_name,
            repository_owner=repository_owner,
        )
        deployments = filter_deployments(
            deployments=flatten([r.deployments for r in repositories]),
            git_hash=git_hash,
            branch_name=branch_name,
            status_name=status_name,
        )

        if deployment_id:
            deployments = [d for d in deployments if d.id == deployment_id]
            if not deployments:
                LOG.warning(
                    f"No endpoints for deployment with id {deployment_id} found"
                )
        endpoints = flatten(
            [get_endpoints_for_deployment(deployment) for deployment in deployments]
        )
        if return_all:
            return endpoints
        return filter_endpoints(
            endpoints, endpoint_kind=endpoint_kind, endpoint_name=endpoint_name
        )

    def get_deployment_by_branch_name(self, repository_name: str, branch_name: str):
        # owner is guaranteed not to have a slash in it so can split on first occurrence
        owner, name = repository_name.split("/", 1)
        repositories = filter_repositories(
            self._get_repositories(),
            repository_name=name,
            repository_owner=owner,
        )
        if not repositories:
            raise TaktileSdkError(f"No repos named {repository_name} found")

        deployments = filter_deployments(
            deployments=flatten([r.deployments for r in repositories]),
            branch_name=branch_name,
            status_name=DeploymentStatesT.list(),
        )
        if not deployments:
            raise TaktileSdkError("No running deployments found")

        if len(deployments) > 1:
            raise TaktileSdkError(
                "More than one deployment for single branch and repo found. "
                "Exiting, as this should not happen"
            )
        return deployments[0]

    def get_endpoint_by_name(
        self, repository_name: str, branch_name: str, endpoint_name: str
    ) -> Tuple[RepositoryDeployment, Endpoint]:
        deployment = self.get_deployment_by_branch_name(
            repository_name=repository_name, branch_name=branch_name
        )
        endpoints = get_endpoints_for_deployment(deployment)
        for endpoint in endpoints:
            if endpoint.name == endpoint_name:
                return deployment, endpoint
        raise TaktileSdkError(f"No endpoint named {endpoint_name} found")

    def delete_deployment(self, deployment_id: UUID4) -> DeploymentBase:
        return self.call(
            verb="delete",
            path=f"{settings.API_V1_STR}/deployments/{deployment_id}",
            model=DeploymentBase,
        )


def get_endpoints_for_deployment(deployment: RepositoryDeployment) -> List[Endpoint]:
    url = _format_http_url(deployment.public_docs_url, docs=False)
    if url == URL_UNAVAILABLE:
        return []
    client = API(api_base=url, api_key=collect_api_key())

    try:
        endpoint_models = client.call(verb="get", path="info", model=Endpoint)
    except ValidationError:
        endpoint_models = [
            Endpoint(
                name=e.name,
                kind=e.kind,
                deployment_id=None,
                profiling_supported=e.profile_kind is not None,
            )
            for e in client.call(
                verb="get", path="info", model=InfoEndpointResponseModel
            ).endpoints
        ]

    for endpoint in endpoint_models:
        endpoint.deployment_id = deployment.id
    return endpoint_models
