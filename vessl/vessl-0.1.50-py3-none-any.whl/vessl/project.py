from typing import List

from openapi_client.models import ProjectCreateAPIInput, ResponseProjectInfo
from vessl import vessl_api
from vessl.organization import _get_organization_name
from vessl.util.exception import InvalidProjectError


def read_project(project_name: str, **kwargs) -> ResponseProjectInfo:
    """Read project in the default organization. If you want to
    override the default organization, then pass `organization_name` as
    `**kwargs`.

    Args:
        project_name(str): Project name.

    Example:
        ```python
        vessl.read_project(
            project_name="tutorials",
        )
        ```
    """
    return vessl_api.project_read_api(
        organization_name=_get_organization_name(**kwargs),
        project_name=project_name,
    )


def list_projects(**kwargs) -> List[ResponseProjectInfo]:
    """List projects in the default organization. If you want to
    override the default organization, then pass `organization_name` as
    `**kwargs`.

    Example:
        ```python
        vessl.list_projects()
        ```
    """
    return vessl_api.project_list_api(
        organization_name=_get_organization_name(**kwargs),
    ).results


def create_project(
    project_name: str,
    description: str = None,
    **kwargs,
) -> ResponseProjectInfo:
    """Create project in the default organization. If you want to
    override the default organization, then pass `organization_name` as
    `**kwargs`.

    Args:
        project_name(str): Project name.
        description(str): Project description. Defaults to None.

    Example:
        ```python
        vessl.create_project(
            project_name="tutorials",
            description="VESSL tutorial project",
        )
        ```
    """
    return vessl_api.project_create_api(
        organization_name=_get_organization_name(**kwargs),
        project_create_api_input=ProjectCreateAPIInput(
            name=project_name,
            description=description,
            project_repositories=[],  # TODO: support project repositories
        ),
    )


### Deprecate for now
# def clone_project(project_name: str, **kwargs) -> None:
#     """Clone project

#     Keyword args:
#         organization_name (str): override default organization
#     """
#     project = read_project(project_name, **kwargs)

#     if project.type != PROJECT_TYPE_VERSION_CONTROL:
#         raise InvalidProjectError("Project type must be version-control.")

#     github_token = vessl_api.cli_git_hub_token_api().token

#     dirname = project.cached_git_repo_slug
#     git_url = f"https://{github_token}@github.com/{project.cached_git_owner_slug}/{project.cached_git_repo_slug}.git"
#     try:
#         subprocess.check_output(["git", "clone", git_url])
#     except subprocess.CalledProcessError:
#         dirname = f"savvihub-{project.cached_git_repo_slug}"
#         logger.info(f"Falling back to '{dirname}'...")
#         subprocess.check_output(["git", "clone", git_url, dirname])

#     subprocess.check_output(["rm", "-rf", f"{dirname}/.git"])


def _get_project_name(**kwargs) -> str:
    project_name = kwargs.get("project_name")
    if project_name is not None:
        return project_name
    if vessl_api.project is not None:
        return vessl_api.project.name
    raise InvalidProjectError("No project selected.")


def _get_project(**kwargs) -> ResponseProjectInfo:
    project_name = kwargs.get("project_name")
    if project_name is not None:
        return read_project(project_name)
    if vessl_api.project is not None:
        return vessl_api.project
    raise InvalidProjectError("No project selected.")
