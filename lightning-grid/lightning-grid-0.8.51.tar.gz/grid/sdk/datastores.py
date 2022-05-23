import textwrap
import warnings
from collections import defaultdict
from datetime import datetime, time
from pathlib import Path
from typing import List, Optional, Union, Dict
from urllib.parse import urlparse

import click
import rich

from grid.openapi import V1GetDatastoreResponse, V1DatastoreOptimizationStatus, V1DatastoreSourceType
from grid.openapi.rest import ApiException
from grid.sdk import env
from grid.sdk._gql.queries import get_user_teams
from grid.sdk.affirmations import affirm, is_not_deleted, is_not_created, is_not_shallow, is_created
from grid.sdk.client import create_swagger_client
from grid.sdk.rest import GridRestClient
from grid.sdk.rest.datastores import (
    get_datastore_from_id,
    get_datastore_from_name,
    delete_datastore,
    create_datastore,
    get_datastore_list,
    mark_datastore_upload_complete,
)
from grid.sdk.user import User, user_from_logged_in_account
from grid.sdk.user_messaging import errors
from grid.sdk.utilities import SPECIAL_NAME_TO_SKIP_OBJECT_INIT
from grid.sdk.utils.datastore_uploads import (
    resume_datastore_upload,
    begin_new_datastore_upload,
    find_incomplete_datastore_upload,
    load_datastore_work_state,
    initialize_upload_work,
)

DATASTORE_TERMINAL_STATES = [
    V1DatastoreOptimizationStatus.DELETED,
    V1DatastoreOptimizationStatus.SUCCEEDED,
    V1DatastoreOptimizationStatus.FAILED,
]


def _datastore_optimization_status_name_to_human(phase: str) -> str:
    """Converts datastore status enum name to cannoniacl format

    Example
    -------
    "DATASTORE_OPTIMIZATION_STATUS_FAILED" -> "failed"

    Notes
    -----
    See PRD for terms used: https://www.notion.so/gridai/Workload-status-observability-0b635c62db9644499d5b5fbd992385d3
    """
    conversion_map = {
        V1DatastoreOptimizationStatus.DELETED:
        "deleted",
        V1DatastoreOptimizationStatus.FAILED:
        "failed",
        V1DatastoreOptimizationStatus.SUCCEEDED:
        "available",
        V1DatastoreOptimizationStatus.OPTIMIZING:
        "optimizing",
        V1DatastoreOptimizationStatus.POD_PENDING:
        "optimizing",
        # yes, this doesn't make sense... but we need to make the datastore proto
        # spec compliant with every other resource before we can change this
        V1DatastoreOptimizationStatus.UNSPECIFIED:
        "uploading",
    }

    if phase not in conversion_map:
        warnings.warn((
            f"The operation completed, but you've found a bug! We cannot convert optimization "
            f"status name: {phase} to a human readable format. Please report this to the grid "
            f"support team on the community slack or at support@grid.ai."
        ), RuntimeWarning)
    else:
        phase = conversion_map[phase]
    return phase


def fetch_datastore(datastore_name: str, datastore_version: int, cluster: str) -> 'Datastore':
    """
    Validate the existence of provided datastore and user's access. Inject datastore id to the
    config, based on the name and version provided. If version is not provided, this function also
    injects the maximum version to the config
    """
    split = datastore_name.split(":")
    owner = None
    if len(split) == 1:
        datastore_name = split[0]
    elif len(split) == 2:
        datastore_name = split[1]
        owner = split[0]
    elif len(split) > 2:
        raise ValueError(f"Error while parsing {datastore_name}. Use the format <username>:<datastore-name>")

    # Fetching all datastores and filter them based on the arguments
    all_datastores = list_datastores(is_global=True, cluster_id=cluster)
    possible_datastores = [d for d in all_datastores if d.name == datastore_name]
    if datastore_version:
        possible_datastores = [d for d in possible_datastores if d.version == datastore_version]
    if not owner:
        # TODO - this is a hack that must be fixed after proper RBAC can fetch the datastore in a team
        user = user_from_logged_in_account()
        owner = user.username
    possible_datastores = [d for d in possible_datastores if d.user.username == owner]
    if cluster:
        possible_datastores = [d for d in possible_datastores if d.cluster_id == cluster]

    # Throwing if no datastores found
    if len(possible_datastores) == 0:
        raise ValueError(
            f'No ready-to-use datastore found with name {datastore_name} '
            f'and version {datastore_version} in the cluster {cluster}'
        )

    # choosing the latest datastore if no version is provided
    if datastore_version is None:
        selected_dstore = possible_datastores[0]
        for dstore in possible_datastores:
            if dstore.version > selected_dstore.version:
                selected_dstore = dstore
        warnings.warn(
            f'No ``--datastore_version`` passed. Using datastore: {datastore_name} version: {selected_dstore.version}'
        )
    else:
        selected_dstore = possible_datastores[0]

    return selected_dstore


class Datastore:
    _name: str
    _id: str
    _version: int
    _source: Optional[Union[str, Path]]
    _s3_no_copy: bool
    _status: Optional[str]
    _created_at: datetime
    _user: User
    _cluster_id: str
    _size: str

    _is_deleted: bool
    _is_created: bool
    _is_shallow: bool

    def __init__(
        self,
        name: Optional[str] = None,
        source: Optional[Union[str, Path]] = None,
        s3_no_copy: bool = False,
        user: Optional[User] = None,
        version: int = 0,
        cluster_id: Optional[str] = None,
    ):
        """Initialize a new DataStore Object.

        If a DataStore with the given name, version, team and cluster already exists,
        then the object returned will be able to interact with the existing DataStore.

        Alternatively, if the DataStore is going to be created for the first time, then
        the ``source` parameters can be used to specify the location of the DataStore on
        disk (or at a remote location).

        After initializing the datastore object, the data itself can be uploaded by calling
        the ``upload()`` method.

        TODO
        ----
        - user and team shouldn't be arguments

        Parameters
        ----------
        name
            The name of the DataStore.
        version
            The version of the DataStore.
        source
            The location of the DataStore on disk or at a remote location.
        s3_no_copy
            If using an s3:// bucket as source use a remote reference type
        user
            The user that owns the DataStore.
        cluster_id
            The name of the cluster that the DataStore should be uploaded to.
        """
        # --------------------------------------------------------------------------- #
        #    This should be the first block that goes into the constructor of the     #
        #    resource object. This block sets the correct values for the private      #
        #    attributes which is then later picked up by the decorator(s) to take     #
        #    right actions. It also initialize the _client object and cluster_id      #
        #    which is required by the downstream methods regardless of the object     #
        #    is completely initialized or not. Most importantly, this blocks checks   #
        #    for the name argument to decide if it's a call from other internal       #
        #    methods to create a shallow object. This is done by checking the         #
        #    special name variable. Other methods that already has the backend        #
        #    response fetched, can use this to create the object without the backend  #
        #    call and then fill-in the response they already have.                    #
        #                                                                             #
        self._client = GridRestClient(api_client=create_swagger_client())
        cluster_id = cluster_id or env.CONTEXT
        self._is_shallow = False
        self._cluster_id = cluster_id
        if name == SPECIAL_NAME_TO_SKIP_OBJECT_INIT:
            self._is_shallow = True
            self._is_created = False
            self._is_deleted = False
            return
        #                                                                             #
        # --------------------------------------------------------------------------- #

        if name is None:
            if source:
                name = parse_name_from_source(source)
            else:
                raise ValueError("Name is required if source is not provided.")
        else:
            try:

                datastore = get_datastore_from_name(
                    client=self._client, cluster_id=cluster_id, datastore_name=name, version=version
                )
                self.__dict__ = self._setup_from_response(datastore).__dict__
                return
            except KeyError:
                self._is_deleted = False  # the datastore has not been deleted
                self._is_created = False  # it doesn't exists in the grid backend.
                pass
        if version:
            raise ValueError(
                f"Existing datastore with name {name} and version {version} is not found. "
                f"If you are creating a new datastore, avoid passing a version argument "
                f"as this is auto-generated."
            )

        self._name = name
        self._version = 0
        self._source = source
        self._user = user
        self._cluster_id = cluster_id
        self._s3_no_copy = s3_no_copy
        self._id = None
        self._status = None
        self._created_at = None
        self._size = None

        try:
            resp = get_datastore_from_name(
                client=self._client, cluster_id=self._cluster_id, datastore_name=self._name, version=self._version
            )
            self.__dict__ = self._setup_from_response(resp).__dict__
        except KeyError:
            self._is_deleted = False
            self._is_created = False
            self._is_shallow = False

    @classmethod
    def _setup_from_response(cls, datastore: V1GetDatastoreResponse) -> 'Datastore':
        instance = cls(name=SPECIAL_NAME_TO_SKIP_OBJECT_INIT)
        instance._is_deleted = datastore.status.phase == V1DatastoreOptimizationStatus.DELETED
        instance._is_created = True
        instance._is_shallow = False

        instance._id = datastore.id
        instance._name = datastore.name
        instance._cluster_id = datastore.spec.cluster_id
        instance._version = datastore.spec.version
        instance._source = datastore.spec.source
        instance._s3_no_copy = instance._source == V1DatastoreSourceType.OBJECT_STORE_REFERENCE_ONLY
        instance._status = datastore.status.phase
        instance._created_at = datastore.created_at
        instance._size = f"{datastore.spec.size_mib} MiB"
        instance._user = User(user_id=datastore.spec.user_id, username="", first_name="", last_name="")
        return instance

    @classmethod
    def _from_id(cls, datastore_id: str, cluster_id: Optional[str] = env.CONTEXT) -> "Datastore":
        instance = cls(name=SPECIAL_NAME_TO_SKIP_OBJECT_INIT, cluster_id=cluster_id)
        instance._id = datastore_id
        instance._is_shallow = True
        return instance

    @property
    def id(self) -> str:
        return self._id

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def s3_no_copy(self):
        """When using an s3:// bucket source, this flag determines if we the data should
        be copied into the grid managed bucket, or if we should only keep a reference to it.
        """
        return self._s3_no_copy

    # ------------------ Attributes Only Valid Before Upload ---------------

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def source(self) -> Union[str, Path]:
        """The directory path at which the datastore is initialized from.

        !!! Note

            This property is only available to the instance of this class which uploads
            the datastore. Previously existing datastores will not possess any value
            for this property.
        """
        return self._source

    # ------------------ Attributes Fully Active After Upload ---------------

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def name(self) -> str:
        """The name of the datastore.
        """
        return self._name

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def version(self) -> int:
        """The version of the datastore.
        """
        return self._version

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def user(self) -> User:
        """Information about the owner of the datastore (name, username, etc).
        """
        return self._user

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def created_at(self) -> datetime:
        """Date-Time timestamp when this datastore was created (first uploaded).
        """
        return self._created_at

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def size(self) -> str:
        """Size (in Bytes) of the datastore.
        """
        return self._size

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def status(self) -> str:
        """The status of the datastore.
        """
        if (self._status and (self._status not in DATASTORE_TERMINAL_STATES)) or ((self._status is None) and
                                                                                  (self._is_created is True)):
            self._update_status()

        return _datastore_optimization_status_name_to_human(self._status)

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def cluster_id(self) -> str:
        """ID of the cluster which this datastore is uploaded to.

        !!! info

            This feature is only available to bring-your-own-cloud-credentials
            customers. Please see https://www.grid.ai/pricing/ for more info.
        """
        return self._cluster_id

    def _unshallow(self):
        """ If the object is a shallow (i.e. only has an id and `_is_shallow` attribute is True)
        object, this method can be triggered to get the full object from the BE. It is designed
        to be called only from the `is_not_shallow` decorator and should not be called directly.
        """
        if not self._is_shallow:
            raise RuntimeError('Datastore is already unshallow')
        if not hasattr(self, '_id') or self._id is None:
            raise RuntimeError("Cannot unshallow resource without a valid Datastore id")
        self._is_shallow = False
        try:
            datastore = get_datastore_from_id(self._client, datastore_id=self._id, cluster_id=self.cluster_id)
        except ApiException as e:  # TODO change to GridException
            if hasattr(e, 'reason') and e.reason == "Not Found":
                self._is_deleted = True
                self._status = V1DatastoreOptimizationStatus.DELETED
        else:
            self.__dict__ = self._setup_from_response(datastore).__dict__

    # -------------- Dunder Methods ----------------------

    @affirm(is_not_shallow, is_not_deleted)
    def __repr__(self):
        if self._is_created:
            res = textwrap.dedent(
                f"""\
                {self.__class__.__name__}(
                    {"name": <10} = \"{self.name}\",
                    {"version": <10} = {self.version},
                    {"size": <10} = \"{self.size}\",
                    {"created_at": <10} = {self.created_at},
                    {"owner": <10} = {self.user},
                    {"cluster_id": <10} = {self.cluster_id},
                )"""
            )
        else:
            res = textwrap.dedent(
                f"""\
                {self.__class__.__name__}(
                    {"name": <12} = \"{self.name}\",
                    {"version": <12} = {self.version},
                    {"source": <12} = \"{self.source}\",
                    {"s3_no_copy": <12} = {self.s3_no_copy},
                    {"owner": <12} = {self.user},
                    {"cluster_id": <12} = {self.cluster_id},
                )"""
            )
        return res

    @affirm(is_not_shallow, is_not_deleted)
    def __str__(self):
        return repr(self)

    @affirm(is_not_shallow, is_not_deleted)
    def __eq__(self, other: 'Datastore'):
        # TODO - handling team's datastore equality here is probably not the best. We should
        #  delegate that to the backend when Project lands
        # need to handle case where attributes of a DataStore are not `User` or `Team`
        # classes. This is the case before the datastore is uploaded.
        self_owner = self._user.user_id if hasattr(self._user, 'user_id') else self._user
        other_owner = other._user.user_id if hasattr(other._user, 'user_id') else other.user

        return (
            self.__class__.__qualname__ == other.__class__.__qualname__ and self._name == other._name
            and self._version == other._version and self_owner == other_owner
        )

    @affirm(is_not_shallow, is_not_deleted)
    def __hash__(self):
        return hash((
            self._name, self._id, self._version, self._size, self._created_at, self._status, self._user, self._source,
            self._cluster_id, self._is_deleted, self._is_created
        ))

    # ---------------------  Internal Methods ----------------------

    @affirm(is_not_shallow, is_not_deleted)
    def _update_status(self):
        """Refreshes the``snapshot_status`` attribute by querying the Grid API.
        """
        updated = get_datastore_from_id(c=self._client, cluster_id=self._cluster_id, datastore_id=self._id)
        self._status = str(updated.status.phase)

    # ---------------------  Public Facing Methods ---------------------

    @affirm(is_not_shallow, is_not_deleted, is_created)
    def delete(self):
        """Deletes the datastore from the grid system.
        """
        delete_datastore(c=self._client, cluster_id=self._cluster_id, datastore_id=self._id)
        self._is_deleted = True

    @affirm(is_not_shallow, is_not_created)
    def upload(self):
        """Uploads the contents of the directories referenced by this datastore instance to Grid.

        Depending on your internet connection this may be a potentially long running process.
        If uploading is inturupsed, the upload session can be resumed by initializing this
        ``Datastore`` object again with the same parameters repeating the call to ``upload()``.
        """
        self._client = GridRestClient(create_swagger_client())
        dstore = create_datastore(
            c=self._client,
            cluster_id=self._cluster_id,
            name=self._name,
            source=self._source,
            no_copy_data_source=self._s3_no_copy
        )
        self._id = dstore.id
        self._version = dstore.spec.version
        self._created_at = dstore.created_at

        if dstore.spec.source_type != V1DatastoreSourceType.EXPANDED_FILES:
            mark_datastore_upload_complete(c=self._client, cluster_id=self._cluster_id, datastore_id=self._id)
            dstore_resp = get_datastore_from_id(c=self._client, datastore_id=self._id, cluster_id=self._cluster_id)
            self.__dict__ = self._setup_from_response(dstore_resp).__dict__
            return

        incomplete_id = find_incomplete_datastore_upload(grid_dir=Path(env.GRID_DIR))
        if (incomplete_id is not None) and (incomplete_id == self._id):
            initial_work = load_datastore_work_state(grid_dir=Path(env.GRID_DIR), datastore_id=incomplete_id)
            resume_datastore_upload(client=self._client, grid_dir=Path(env.GRID_DIR), work=initial_work)
            dstore_resp = get_datastore_from_id(c=self._client, datastore_id=self._id, cluster_id=self._cluster_id)
            self.__dict__ = self._setup_from_response(dstore_resp).__dict__
            return

        begin_new_datastore_upload(
            client=self._client,
            grid_dir=Path(env.GRID_DIR),
            source_path=Path(self._source),
            cluster_id=self._cluster_id,
            datastore_id=self._id,
            datastore_name=self._name,
            creation_timestamp=self._created_at,
            datastore_version=str(self._version),
        )
        dstore_resp = get_datastore_from_id(c=self._client, datastore_id=self._id, cluster_id=self._cluster_id)
        self.__dict__ = self._setup_from_response(dstore_resp).__dict__
        return


def list_datastores(cluster_id: Optional[str] = None, is_global: bool = False) -> List[Datastore]:
    """List datastores for user / teams

    Parameters
    ----------
    is_global:
        if True, returns a list of datastores of the everyone in the team
    cluster_id:
        if specified, returns a list of datastores for the specified cluster
    """
    user = user_from_logged_in_account()
    client = GridRestClient(create_swagger_client())

    cluster_id = cluster_id or env.CONTEXT
    datastores = []

    if not is_global:
        # single user only
        user_datastore_resps = get_datastore_list(client=client, cluster_id=cluster_id)
        for user_datastore in user_datastore_resps:
            dstore_resp = get_datastore_from_id(
                c=client, datastore_id=user_datastore.id, cluster_id=user_datastore.spec.cluster_id
            )
            dstore = Datastore._setup_from_response(datastore=dstore_resp)
            dstore.user.username = user.username
            datastores.append(dstore)
    else:
        # If ``include_teams`` is set, add datastores registered to the team.
        team_user_id_name_map: Dict[str, Dict[str, str]] = {}
        team_user_id_name_map[user.user_id] = {"username": user.username, "team_name": ""}
        for team_data in get_user_teams():
            for member_data in team_data['members']:
                team_user_id_name_map[member_data['id']] = {
                    "username": member_data['username'],
                    "team_name": team_data['name'],
                }

        team_dstore_list = get_datastore_list(
            client=client, cluster_id=cluster_id, user_ids=list(team_user_id_name_map.keys())
        )
        for team_dstore in team_dstore_list:
            resp = get_datastore_from_id(c=client, cluster_id=team_dstore.spec.cluster_id, datastore_id=team_dstore.id)
            dstore = Datastore._setup_from_response(datastore=resp)
            dstore.user.username = team_user_id_name_map[dstore.user.user_id]['username']
            dstore.user.team_name = team_user_id_name_map[dstore.user.user_id]['team_name']
            datastores.append(dstore)

    return datastores


def parse_name_from_source(source) -> str:
    """Parses datastore name from source if name isn't provided"""
    try:
        parse_result = urlparse(source)
    except ValueError:
        raise click.ClickException(errors.datastore_invalid_source(source))

    if parse_result.path != '/' and parse_result.path != '':
        path = Path(parse_result.path)
        base = path.name.split(".")[0]
        ret = base.lower().strip()
    else:
        ret = parse_result.netloc

    return ret
