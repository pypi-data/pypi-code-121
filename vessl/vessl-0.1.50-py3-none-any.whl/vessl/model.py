from typing import List

from openapi_client import (
    ModelRepositoryCreateAPIInput,
    ModelRepositoryUpdateAPIInput,
    StorageFile,
    ResponseModelRepositoryDetail,
)
from openapi_client.models import (
    ModelCreateAPIInput,
    ModelUpdateAPIInput,
    ResponseModelDetail,
)
from vessl import vessl_api
from vessl.organization import _get_organization_name
from vessl.volume import copy_volume_file, delete_volume_file, list_volume_files


def read_model_repository(
    repository_name: str, **kwargs
) -> ResponseModelRepositoryDetail:
    """Read model repository in the default organization. If you want to
    override the default organization, then pass `organization_name` as
    `**kwargs`.

    Args:
        repository_name(str): Model repository name.

    Example:
        ```python
        vessl.read_model_repository(
            repository_name="Transformer-ImageNet",
        )
        ```
    """
    return vessl_api.model_repository_read_api(
        organization_name=_get_organization_name(**kwargs),
        repository_name=repository_name,
    )


def list_model_repositories(**kwargs) -> List[ResponseModelRepositoryDetail]:
    """List model repositories in the default organization. If you want to
    override the default organization, then pass `organization_name` as
    `**kwargs`.

    Example:
        ```python
        vessl.list_model_repositories()
        ```
    """
    return vessl_api.model_repository_list_api(
        organization_name=_get_organization_name(**kwargs),
    ).results


def create_model_repository(
    name: str, description: str = None, **kwargs
) -> ResponseModelRepositoryDetail:
    """Create model repository in the default organization. If you want to
    override the default organization, then pass `organization_name` as
    `**kwargs`.

    Args:
        name(str): Model repository name.
        description(str): Model repository description. Defaults to None.

    Example:
        ```python
        vessl.create_model_repository(
            name="Transformer-ImageNet",
            description="Transformer model trained on ImageNet",
        )
        ```
    """
    return vessl_api.model_repository_create_api(
        organization_name=_get_organization_name(**kwargs),
        model_repository_create_api_input=ModelRepositoryCreateAPIInput(
            name=name,
            description=description,
        ),
    )


def update_model_repository(
    name: str, description: str, **kwargs
) -> ResponseModelRepositoryDetail:
    """Update model repository in the default organization. If you want to
    override the default organization, then pass `organization_name` as
    `**kwargs`.

    Args:
        name(str): Model repository name.
        description(str): Model repository description to update.

    Example:
        ```python
        vessl.update_model_repository(
            name="Transformer-ImageNet",
            description="Update description to this",
        )
        ```
    """
    return vessl_api.model_update_api(
        organization_name=_get_organization_name(**kwargs),
        name=name,
        model_repository_update_api_input=ModelRepositoryUpdateAPIInput(
            description=description
        ),
    )


def delete_model_repository(name: str, **kwargs) -> object:
    """Delete model repository in the default organization. If you want to
    override the default organization, then pass `organization_name` as
    `**kwargs`.

    Args:
        name(str): Model repository name.

    Example:
        ```python
        vessl.delete_model_repository(
            name="Transformer-ImageNet",
        )
        ```
    """
    return vessl_api.model_repository_delete_api(
        organization_name=_get_organization_name(**kwargs),
        name=name,
    )


def read_model(
    repository_name: str, model_number: int, **kwargs
) -> ResponseModelDetail:
    """Read model in the default organization. If you want to override the
    default organization, then pass `organization_name` as `**kwargs`.

    Args:
        repository_name(str): Model repository name.
        model_number(int): Model number.

    Example:
        ```python
        vessl.read_model(
            repository_name="Transformer-ImageNet",
            model_number=1,
        )
        ```
    """
    return vessl_api.model_read_api(
        organization_name=_get_organization_name(**kwargs),
        repository_name=repository_name,
        number=model_number,
    )


def list_models(repository_name: str, **kwargs) -> List[ResponseModelDetail]:
    """List models in the default organization. If you want to override the
    default organization, then pass `organization_name` as `**kwargs`.

    Args:
        repository_name(str): Model repository name.

    Example:
        ```python
        vessl.list_models(
            repository_name="Transformer-ImageNet",
        )
        ```
    """
    return vessl_api.model_list_api(
        organization_name=_get_organization_name(**kwargs),
        repository_name=repository_name,
    ).results


def create_model(
    repository_name: str,
    repository_description: str = None,
    experiment_id: int = None,
    model_name: str = None,
    paths: List[str] = None,
    **kwargs,
) -> ResponseModelDetail:
    """Create model in the default organization. If you want to override the
    default organization, then pass `organization_name` as `**kwargs`. If the
    given model repository name does not exist, then create one with the given
    repository_description. Otherwise, create a model in the existing model
    repository.

    Args:
        repository_name(str): Model repository name.
        repository_description(str): Model repository description. Defaults to
            None
        experiment_id(int): Pass experiment ID if the model is sourced from the
            experiment outputs. Defaults to None.
        model_name(str): Model name is unique and optional. Defaults to None.
        paths(List[str]): Paths for creating model. Paths could be sub paths of
            experiment output files or local file paths. Defaults to root.

    Example:
        ```python
        vessl.create_model(
            repository_name="Transformer-ImageNet",
            repository_description="Transformer model trained on ImageNet",
            experiment_id=123456,
            model_name="v0.0.1",
        )
        ```
    """
    if paths is None:
        paths = ["/"]

    return vessl_api.model_create_api(
        organization_name=_get_organization_name(**kwargs),
        repository_name=repository_name,
        model_create_api_input=ModelCreateAPIInput(
            repository_description=repository_description,
            experiment_id=experiment_id,
            model_name=model_name,
            paths=paths,
        ),
    )


def update_model(
    repository_name: str, model_number: int, name: str, **kwargs
) -> ResponseModelDetail:
    """Update model in the default organization. If you want to override the
    default organization, then pass `organization_name` as `**kwargs`.

    Args:
        repository_name(str): Model repository name.
        model_number(int): Model number.
        name(str): Model name to update.

    Example:
        ```python
        vessl.update_model(
            repository_name="Transformer-ImageNet",
            model_number=1,
            name="v0.0.2",
        )
        ```
    """
    return vessl_api.model_update_api(
        organization_name=_get_organization_name(**kwargs),
        repository_name=repository_name,
        number=model_number,
        model_update_api_input=ModelUpdateAPIInput(name=name),
    )


def delete_model(repository_name: str, model_number: int, **kwargs) -> object:
    """Delete model in the default organization. If you want to override the
    default organization, then pass `organization_name` as `**kwargs`.

    Args:
        repository_name(str): Model repository name.
        model_number(int): Model number.

    Example:
        ```python
        vessl.delete_model(
            repository_name="Transformer-ImageNet",
            model_number=1,
        )
        ```
    """
    return vessl_api.model_delete_api(
        organization_name=_get_organization_name(**kwargs),
        repository_name=repository_name,
        version=model_number,
    )


def list_model_volume_files(
    repository_name: str,
    model_number: int,
    need_download_url: bool = False,
    path: str = "",
    recursive: bool = False,
    **kwargs,
) -> List[StorageFile]:
    """List model files in the default organization. If you want to override the
    default organization, then pass `organization_name` as `**kwargs`.

    Args:
        repository_name(str): Model repository name.
        model_number(int): Model number.
        need_download_url(bool): True if you need a download URL, False
            otherwise. Defaults to False.
        path(str): Directory path to list. Defaults to root.
        recursive(bool): True if file is a directory, False otherwise. Defaults
            to False.

    Example:
        ```python
        vessl.list_model_volume_files(
            repository_name="Transformer-ImageNet",
            model_number=1,
            recursive=True,
        )
        ```
    """
    model = read_model(
        repository_name=repository_name, model_number=model_number, **kwargs
    )
    return list_volume_files(
        model.artifact_volume_id, need_download_url, path, recursive
    )


def upload_model_volume_file(
    repository_name: str,
    model_number: int,
    source_path: str,
    dest_path: str,
    **kwargs,
) -> None:
    """Upload file to the model in the default organization. If you want to
    override the default organization, then pass `organization_name` as
    `**kwargs`.

    Args:
        repository_name(str): Model repository name.
        model_number(int): Model number.
        source_path(str): Local source path.
        dest_path(str): Destination path within the model.

    Example:
        ```python
        vessl.upload_model_volume_file(
            repository_name="Transformer-ImageNet",
            model_number=1,
            source_path="model_best.pth",
            dest_path="model_best.pth",
        )
        ```
    """
    model = read_model(
        repository_name=repository_name, model_number=model_number, **kwargs
    )
    return copy_volume_file(
        source_volume_id=None,
        source_path=source_path,
        dest_volume_id=model.artifact_volume_id,
        dest_path=dest_path,
    )


def download_model_volume_file(
    repository_name: str,
    model_number: int,
    source_path: str,
    dest_path: str,
    **kwargs,
) -> None:
    """Download a model in the default organization. If you want to override the
    default organization, then pass `organization_name` as `**kwargs`.

    Args:
        repository_name(str): Model repository name.
        model_number(int): Model number.
        source_path(str): Source path within the model
        dest_path(str): Local destination path

    Example:
        ```python
        vessl.download_model_volume_file(
            repository_name="Transformer-ImageNet",
            model_number=1,
            source_path="model_best.pth",
            dest_path="models",
        )
        ```
    """
    model = read_model(
        repository_name=repository_name, model_number=model_number, **kwargs
    )
    return copy_volume_file(
        source_volume_id=model.artifact_volume_id,
        source_path=source_path,
        dest_volume_id=None,
        dest_path=dest_path,
    )


def delete_model_volume_file(
    repository_name: str,
    model_number: int,
    path: str,
    **kwargs,
):
    """Delete the model volume file in the default organization. If you want to
    override the default organization, then pass `organization_name` as
    `**kwargs`.

    Args:
        repository_name(str): Model repository name.
        model_number(int): Model number.
        path(str): File path within the model

    Example:
        ```python
        vessl.delete_model_volume_file(
            repository_name="Transformer-ImageNet",
            model_number=1,
            source_path="models",
            recursive=True,
        )
        ```
    """
    model = read_model(
        repository_name=repository_name, model_number=model_number, **kwargs
    )
    delete_volume_file(model.artifact_volume_id, path)
