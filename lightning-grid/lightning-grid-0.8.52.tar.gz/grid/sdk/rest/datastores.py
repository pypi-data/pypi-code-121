from typing import Dict, Optional, List, TYPE_CHECKING

from pathlib import Path
import validators

from grid.openapi import (
    Externalv1Datastore,
    Externalv1DatastoreSpec,
    V1GetDatastoreResponse,
    V1DatastoreSourceType,
    V1CreateDatastoreRequest,
    V1CreateDatastoreResponse,
    V1DatastoreUploadObject,
    Body2,
    V1PresignedUploadUrl,
    Body3,
    V1CompletePresignedUrlsUploadObject,
    V1CompletePresignedUrlUpload,
)
from grid.sdk.rest.client import GridRestClient
from grid.sdk.rest.exceptions import throw_with_message
from grid.sdk.user_messaging import errors

if TYPE_CHECKING:
    from grid.sdk.utils.datastore_uploads import DataFile


@throw_with_message
def create_datastore(
    c: GridRestClient,
    cluster_id: str,
    name: str,
    source: str,
    no_copy_data_source: bool,
    version: int = 0,
) -> V1CreateDatastoreResponse:
    """Create a new datastore.

    Parameters
    ----------
    c
        Client
    cluster_id
        Cluster ID to use for uploading files.
    name
        Human readable name assigned to the datastore.
    source
        the source string as passed in by the user on the CLI or SDK.
    no_copy_data_source
        do not copy bucket data, create a shallow clone.
    version
        The version of the datastore to create with some same `name`.
    """
    if Path(source).exists():
        source_type = V1DatastoreSourceType.EXPANDED_FILES
        if no_copy_data_source is True:
            raise ValueError(errors.datastore_invalid_no_copy_option(source))

    elif validators.url(source) is True:
        source_type = V1DatastoreSourceType.HTTP_URL
        if no_copy_data_source is True:
            raise ValueError(errors.datastore_invalid_no_copy_option(source))

    elif source.startswith("s3://"):
        if not source.endswith("/"):
            raise (ValueError(errors.datastore_s3_source_does_not_end_in_slash(source)))
        if no_copy_data_source is True:
            source_type = V1DatastoreSourceType.OBJECT_STORE_REFERENCE_ONLY
        else:
            source_type = V1DatastoreSourceType.OBJECT_STORE

    else:
        raise ValueError(errors.datastore_invalid_source(source))

    if source_type == V1DatastoreSourceType.EXPANDED_FILES:
        source = ""  # expanded file source should not be set to a value in backend.

    resp = c.datastore_service_create_datastore(
        spec_cluster_id=cluster_id,
        body=V1CreateDatastoreRequest(
            name=name,
            spec=Externalv1DatastoreSpec(
                cluster_id=cluster_id,
                source=source,
                source_type=source_type,
                version=version,
            ),
        ),
    )
    return resp


def delete_datastore(c: 'GridRestClient', cluster_id: str, datastore_id: str) -> None:
    """Delete a datastore on a provided cluster with the given datastore id.
    """
    c.datastore_service_delete_datastore(cluster_id=cluster_id, id=datastore_id)


def datastore_upload_object_from_data_file(df: 'DataFile') -> V1DatastoreUploadObject:
    if not df.relative_file_name:
        raise ValueError(f"relative_file_name is a required field. Not found in df: {df}")
    if not df.part_count:
        raise ValueError(f"part_count is a required field. Not found in df: {df}")

    urls = None
    if len(df.tasks) > 0:
        urls = []
        for task in df.tasks:
            if not task.part_number:
                raise ValueError(f"part_number is required if datafile tasks are defined. df: {df} task: {task}")
            if not task.url:
                raise ValueError(f"url is required if datafile tasks are defined. df: {df} task: {task}")
            urls.append(V1PresignedUploadUrl(
                part_number=task.part_number,
                url=task.url,
            ))

    return V1DatastoreUploadObject(
        key=df.relative_file_name,
        part_count=str(df.part_count),
        upload_id=df.upload_id,
        expiry_time=df.expiry_time,
        urls=urls
    )


@throw_with_message
def create_presigned_urls(
    c: GridRestClient, cluster_id: str, datastore_id: str, upload_objects: List[V1DatastoreUploadObject]
) -> List[V1DatastoreUploadObject]:
    """Create presigned URLs for uploading files to a datastore.

    Parameters
    ----------
    c
        Client
    cluster_id
        Cluster ID to use for uploading files.
    datastore_id
        Datastore ID to use for uploading files.
    upload_objects
        List of objects to upload.
    """
    resp = c.datastore_service_create_datastore_presigned_urls(
        cluster_id=cluster_id,
        datastore_id=datastore_id,
        body=Body2(objects=upload_objects),
    )
    return resp.objects


@throw_with_message
def complete_presigned_url_upload(
    c: GridRestClient, cluster_id: str, datastore_id: str, data_files: List['DataFile']
) -> None:
    """Complete uploading files to a datastore.

    Parameters
    ----------
    c
        Client
    cluster_id
        Cluster ID to use for uploading files.
    datastore_id
        Datastore ID to use for uploading files.
    data_files
        List of data files to upload.
    """
    completed_objects = []
    for df in data_files:
        parts = []
        # Upload parts must always be sorted by part_number or an error will occur.
        # They should never be "unsorted" in this list, but this is a bit of defensive
        # programming to ensure that this is the case
        tasks = sorted(df.tasks, key=lambda x: int(x.part_number))
        for task in tasks:
            parts.append(V1CompletePresignedUrlUpload(
                part_number=task.part_number,
                etag=task.etag,
            ))

        completed_objects.append(
            V1CompletePresignedUrlsUploadObject(key=df.relative_file_name, upload_id=df.upload_id, urls=parts)
        )

    c.datastore_service_complete_datastore_presigned_urls_upload(
        cluster_id=cluster_id,
        datastore_id=datastore_id,
        body=Body3(objects=completed_objects),
    )


@throw_with_message
def mark_datastore_upload_complete(c: GridRestClient, cluster_id: str, datastore_id: str):
    """Tell the grid backend that all datastore files have been uploaded.

    Failing to call this method will indefintely hold the datastore desired
    state as "uploading"; meaning that it will never be optimized or made
    available to compute services.

    Parameters
    ----------
    c
        Client
    cluster_id
        The cluster ID the datastore is uploaded to
    datastore_id
        The datastore ID
    """
    c.datastore_service_mark_datastore_upload_complete(cluster_id=cluster_id, datastore_id=datastore_id)


@throw_with_message
def datastore_id_from_name(c: GridRestClient, cluster_id: str, name: str, version: Optional[str] = None) -> str:
    """Find the id of a datastore with some name (and optionally version) on a cluster.

    Parameters
    ----------
    c
        Client
    cluster_id
        which cluster should be used to find the datastore in.
    name
        the name of the datastore to find the ID of
    version
        The version of the datastore with ``name`` to find the ID of.
        NOTE: If no ``version`` argument is present, then the maximum
        version of the datastore will be used.

    Returns
    -------
    str
       The ID of the datastore.
    """
    dstores = c.datastore_service_list_datastores(cluster_id=cluster_id, available=True)

    datastore_versions: Dict[int, Externalv1Datastore] = {}

    for dstore in dstores.datastores:
        if dstore.name == name:
            spec = dstore.spec
            datastore_versions[spec.version] = dstore

    if version is None:
        # use the max version available
        version = max(datastore_versions.keys())

    try:
        return datastore_versions[version].id
    except KeyError:
        raise KeyError(f"no datastore exists with name: {name}")


@throw_with_message
def get_datastore_from_id(c: GridRestClient, datastore_id: str, cluster_id: str) -> V1GetDatastoreResponse:
    dstore = c.datastore_service_get_datastore(cluster_id=cluster_id, id=datastore_id)
    return dstore


@throw_with_message
def get_datastore_from_name(client: GridRestClient, cluster_id: str, datastore_name: str, version: int):
    ds_version_to_id_map = {}
    datastores = get_datastore_list(client=client, cluster_id=cluster_id)

    for datastore in datastores:
        if datastore.name == datastore_name:
            ds_version_to_id_map[datastore.spec.version] = datastore.id
            # return if the version is the same
            if version and datastore.spec.version == version:
                return datastore

    # if version is not specified, return the latest version
    if version and len(ds_version_to_id_map) > 0:
        max_version = max(ds_version_to_id_map.keys())
        return ds_version_to_id_map[max_version]

    raise KeyError(f'Datastore with name {datastore_name} and version {version} not found')


@throw_with_message
def get_datastore_list(client: GridRestClient,
                       cluster_id: str,
                       user_ids: Optional[List[str]] = None) -> List[Externalv1Datastore]:
    """get a list of the datastores the user has access to on the cluster

    Parameters
    ----------
    client
        the rest client to interact with the grid-backend from.
    cluster_id
        the cluster id to get a list of datastores for
    user_ids
        the user_ids to get a list of datastores for (authenticated client user
        must have authorization to list datastores of teammates). default=None
    """
    user_ids = user_ids or []
    resp = client.datastore_service_list_datastores(cluster_id=cluster_id, user_ids=user_ids, available=True)
    return resp.datastores


def datastore_dsn_from_id(id: str) -> str:
    """Return the DSN of the datastore

    Parameters
    ----------
    id
        datastore ID to convert into DSN.

    Returns
    -------
    str
        DSN form of the datastore ID.
    """
    return f"datastore://grid/{id}"


def datastore_id_from_dsn(dsn: str) -> str:
    """Return the id of a datastore from a DSN.

    Parameters
    ----------
    dsn
        DSN string to convert into an ID

    Returns
    -------
    str
        ID of the datastore DSN string.
    """
    # convert ``datastore://grid/{id}`` -> ``['datastore:', '', 'grid', '{id}']``
    # convert ``datastore://grid/{id}/`` -> ``['datastore:', '', 'grid', '{id}', '']``
    # ... (we want the last element)
    parts = dsn.split('/')
    if dsn.endswith('/'):
        if len(parts) < 2:
            raise RuntimeError(f"Internal Error. invalid datastore dsn format while parsing ID. dsn={dsn}")
        return parts[-2]
    return parts[-1]
