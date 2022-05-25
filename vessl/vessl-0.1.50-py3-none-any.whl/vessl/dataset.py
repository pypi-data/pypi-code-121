from typing import List

from openapi_client import VESSLDatasetCreateAPIInput
from openapi_client.models import (
    GSDatasetCreateAPIInput,
    ResponseDatasetInfo,
    ResponseDatasetInfoDetail,
    ResponseDatasetVersionInfo,
    StorageFile,
    S3DatasetCreateAPIInput,
)
from vessl import vessl_api
from vessl.organization import _get_organization_name
from vessl.util.constant import DATASET_PATH_SCHEME_GS, DATASET_PATH_SCHEME_S3
from vessl.util.exception import InvalidDatasetError
from vessl.volume import copy_volume_file, delete_volume_file, list_volume_files


def read_dataset(dataset_name: str, **kwargs) -> ResponseDatasetInfoDetail:
    """Read a dataset in the default organization. If you want to override the
    default organization, then pass `organization_name` as `**kwargs`.

    Args:
        dataset_name(str): Dataset name.

    Example:
        ```python
        vessl.read_dataset(
           dataset_name="mnist",
        )
        ```
    """
    return vessl_api.dataset_read_api(
        dataset_name=dataset_name, organization_name=_get_organization_name(**kwargs)
    )


def read_dataset_version(
    dataset_id: int,
    dataset_version_hash: str,
    **kwargs,
) -> ResponseDatasetVersionInfo:
    """Read the specific version of dataset in the default organization. If you
    want to override the default organization, then pass `organization_name` as
    `**kwargs`.

    Args:
        dataset_id(int): Dataset id.
        dataset_version_hash(str): Dataset version hash.

    Example:
        ```python
        vessl.read_dataset_version(
            dataset_id=1,
            dataset_version_hash="hash123"
        )
        ```
    """
    return vessl_api.dataset_version_read_api(
        dataset_id=dataset_id,
        dataset_version_hash=dataset_version_hash,
        organization_name=_get_organization_name(**kwargs),
    )


def list_datasets(**kwargs) -> List[ResponseDatasetInfo]:
    """List datasets in the default organization. If you want to override the
    default organization, then pass `organization_name` as `**kwargs`.

    Example:
        ```
        vessl.list_datasets()
        ```
    """
    return vessl_api.dataset_list_api(
        organization_name=_get_organization_name(**kwargs),
    ).results


def _create_dataset_local(
    dataset_name: str,
    is_version_enabled: bool = False,
    description: str = None,
    **kwargs,
) -> ResponseDatasetInfoDetail:
    return vessl_api.v_essl_dataset_create_api(
        organization_name=_get_organization_name(**kwargs),
        vessl_dataset_create_api_input=VESSLDatasetCreateAPIInput(
            name=dataset_name,
            description=description,
            is_version_enabled=is_version_enabled,
        ),
    )


def _create_dataset_s3(
    dataset_name: str,
    is_version_enabled: bool = False,
    is_public: bool = True,
    description: str = None,
    external_path: str = None,
    aws_role_arn: str = None,
    version_path: str = None,
    **kwargs,
) -> ResponseDatasetInfoDetail:
    if is_version_enabled and (
        version_path is None or not version_path.startswith(DATASET_PATH_SCHEME_S3)
    ):
        raise InvalidDatasetError(f"Invalid version path: {version_path}")

    return vessl_api.s3_dataset_create_api(
        organization_name=_get_organization_name(**kwargs),
        s3_dataset_create_api_input=S3DatasetCreateAPIInput(
            name=dataset_name,
            description=description,
            is_version_enabled=is_version_enabled,
            s3_path=external_path,
            version_s3_path=version_path,
            is_public=is_public,
            aws_role_arn=aws_role_arn,
        ),
    )


def _create_dataset_gs(
    dataset_name: str,
    is_version_enabled: bool = False,
    is_public: bool = False,
    description: str = None,
    external_path: str = None,
    version_path: str = None,
    **kwargs,
) -> ResponseDatasetInfoDetail:
    if is_version_enabled:
        raise InvalidDatasetError("Versioning is not supported for GoogleStorage")

    return vessl_api.g_s_dataset_create_api(
        organization_name=_get_organization_name(**kwargs),
        gs_dataset_create_api_input=GSDatasetCreateAPIInput(
            name=dataset_name,
            description=description,
            is_version_enabled=is_version_enabled,
            gs_path=external_path,
            version_gs_path=version_path,
            is_public=is_public,
        ),
    )


def create_dataset(
    dataset_name: str,
    description: str = None,
    is_version_enabled: bool = False,
    is_public: bool = False,
    external_path: str = None,
    aws_role_arn: str = None,
    version_path: str = None,
    **kwargs,
) -> ResponseDatasetInfoDetail:
    """Create a dataset in the default organization. If you want to override
    the default organization, then pass `organization_name` as `**kwargs`.

    Args:
        dataset_name(str): Dataset name.
        description(str): dataset description. Defaults to None.
        is_version_enabled(bool): True if a dataset versioning is set,
            False otherwise. Defaults to False.
        is_public(bool): True if a dataset is source from a public bucket, False
            otherwise. Defaults to False.
        external_path(str): AWS S3 or Google Cloud Storage bucket URL. Defaults
            to None.
        aws_role_arn(str): AWS Role ARN to access S3. Defaults to None.
        version_path(str): Versioning bucket path. Defaults to None.

    Example:
        ```python
        vessl.create_dataset(
            dataset_name="mnist",
            is_public=True,
            external_path="s3://savvihub-public-apne2/mnist"
        )
        ```
    """
    if external_path is None:
        return _create_dataset_local(
            dataset_name, is_version_enabled, description, **kwargs
        )

    if external_path.startswith(DATASET_PATH_SCHEME_S3):
        return _create_dataset_s3(
            dataset_name,
            is_version_enabled,
            is_public,
            description,
            external_path,
            aws_role_arn,
            version_path,
            **kwargs,
        )

    if external_path.startswith(DATASET_PATH_SCHEME_GS):
        return _create_dataset_gs(
            dataset_name,
            is_version_enabled,
            is_public,
            description,
            external_path,
            version_path,
            **kwargs,
        )

    raise InvalidDatasetError("Invalid path scheme. Must be either s3:// or gs://.")


def list_dataset_volume_files(
    dataset_name: str,
    need_download_url: bool = False,
    path: str = "",
    recursive: bool = False,
    **kwargs,
) -> List[StorageFile]:
    """List dataset volume files in the default organization. If you want to
    override the default organization, then pass `organization_name` as
    `**kwargs`.

    Args:
        dataset_name(str): Dataset name.
        need_download_url(bool): True if you need a download URL, False
            otherwise. Defaults to False.
        path(str): Directory path to list. Defaults to root(""),
        recursive(bool): True if list files recursively, False otherwise.
            Defaults to False.

    Example:
        ```python
        vessl.list_dataset_volume_files(
            dataset_name="mnist",
            recursive=True,
        )
        ```
    """
    dataset = read_dataset(dataset_name, **kwargs)
    return list_volume_files(dataset.volume_id, need_download_url, path, recursive)


def upload_dataset_volume_file(
    dataset_name: str,
    source_path: str,
    dest_path: str,
    **kwargs,
) -> None:
    """Upload file to the dataset. If you want to override the default
    organization, then pass `organization_name` as `**kwargs`.

    Args:
        dataset_name(str): Dataset name.
        source_path(str): Local source path.
        dest_path(str): Destination path within the dataset.

    Example:
        ```python
        vessl.upload_dataset_volume_file(
            dataset_name="mnist",
            source_path="test.csv",
            dest_path="train",
        )
        ```
    """
    dataset = read_dataset(dataset_name, **kwargs)
    return copy_volume_file(
        source_volume_id=None,
        source_path=source_path,
        dest_volume_id=dataset.volume_id,
        dest_path=dest_path,
    )


def download_dataset_volume_file(
    dataset_name: str,
    source_path: str,
    dest_path: str,
    **kwargs,
) -> None:
    """Download file from the dataset. If you want to override the default
    organization, then pass `organization_name` as `**kwargs`.

    Args:
        dataset_name(str): Dataset name.
        source_path(str): Source path within the dataset.
        dest_path(str): Local destination path.

    Example:
        ```python
        vessl.download_dataset_volume_file(
            dataset_name="mnist",
            source_path="train/test.csv",
            dest_path=".",
        )
        ```
    """
    dataset = read_dataset(dataset_name, **kwargs)
    return copy_volume_file(
        source_volume_id=dataset.volume_id,
        source_path=source_path,
        dest_volume_id=None,
        dest_path=dest_path,
    )


def copy_dataset_volume_file(
    dataset_name: str,
    source_path: str,
    dest_path: str,
    **kwargs,
) -> None:
    """Copy files within the same dataset. Noted that this is not supported for
    externally sourced datasets like S3 or GCS. If you want to override the
    default organization, then pass `organization_name` as `**kwargs`.

    Args:
        dataset_name(str): Dataset name.
        source_path(str): Source path within the dataset.
        dest_path(str): Local destination path.

    Example:
        ```python
        vessl.download_dataset_volume_file(
            dataset_name="mnist",
            source_path="train/test.csv",
            dest_path="test/test.csv",
        )
        ```
    """
    dataset = read_dataset(dataset_name, **kwargs)
    return copy_volume_file(
        source_volume_id=dataset.volume_id,
        source_path=source_path,
        dest_volume_id=dataset.volume_id,
        dest_path=dest_path,
    )


def delete_dataset_volume_file(
    dataset_name: str,
    path: str,
    **kwargs,
) -> List[StorageFile]:
    """Delete the dataset volume file. Noted that this is not supported for
    externally sourced datasets like S3 or GCS. If you want to override the
    default organization, then pass `organization_name` as `**kwargs`.

    Args:
        dataset_name(str): Dataset name.
        path(str): File path.

    Example:
        ```python
        vessl.delete_dataset_volume_file(
            dataset_name="mnist",
            path="train/test.csv",
        )
        ```
    """
    dataset = read_dataset(dataset_name, **kwargs)
    return delete_volume_file(dataset.volume_id, path)
