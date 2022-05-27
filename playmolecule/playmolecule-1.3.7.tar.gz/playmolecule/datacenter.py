# (c) 2015-2022 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
from playmolecule.utils import (
    tempname,
    format_filesize,
    parse_timestamp_utc,
    utc_timestamp_to_local,
    ensurelist,
    _requestURL,
)
import tarfile
import logging
import time
import json
import os
import re


logger = logging.getLogger(__name__)


def download_dataset(
    session, datasetid, path, files=None, tmpdir=None, attempts=1, _logger=True
):
    """Download a dataset from the backend

    Parameters
    ----------
    session : Session
        A Session object
    datasetid : int
        The ID of the dataset we want to download
    path : str
        The location to which to download the dataset
    files : list
        A subset list of files inside of the dataset to retrieve
    tmpdir : str
        A location to store temporary data. If set to None, the default is /tmp/
    attempts : int
        Number of times to attempt uploading the file. Can help with unstable connections
    _logger : bool
        Set to False to reduce the verbosity

    Examples
    --------
    >>> download_dataset(session, 182, "./dataset_182/")
    """
    session._require_log_in()

    if not isinstance(datasetid, int):
        raise RuntimeError("datasetid must be an integer")

    downloaded = False
    while not downloaded and attempts > 0:
        headers = {"token": session._token}
        if files is not None:
            files = ensurelist(files)
            if len(files):
                headers["files"] = ",".join(files)

        try:
            result = _request_url(
                "get",
                f"{session._server_endpoint}/datacenter/{datasetid}",
                headers,
                _logger=_logger,
            )
        except Exception as e:
            attempts -= 1
            _throw_error(
                f"Error downloading dataset {datasetid} with error {e}. Retrying in 5s. Attempts remaining {attempts}.",
                _logger,
            )
            time.sleep(5)
        else:
            downloaded = True

    if not downloaded or result is None:
        _throw_error(
            f"Failed to download dataset {datasetid} to {path}",
            _logger,
        )
        return

    tmpfile = tempname(suffix=".tar.gz", tmpdir=tmpdir)

    with open(tmpfile, "wb") as f:
        f.write(result.content)

    os.makedirs(path, exist_ok=True)

    try:
        with tarfile.open(tmpfile) as tar:
            outname = os.path.abspath(path)
            members = tar.getmembers()
            if len(members) == 1:
                outname = os.path.abspath(os.path.join(path, members[0].name))

            tar.extractall(path=path)
        os.remove(tmpfile)
    except Exception as e:
        if os.path.exists(tmpfile):
            os.remove(tmpfile)
        _throw_error(
            f"Error untaring results for dataset {datasetid} with error {e}",
            _logger,
        )
        return

    if _logger:
        logger.info(f"Dataset {datasetid} was downloaded successfully to {outname}.")

    return outname


def get_datasets(
    session,
    public=None,
    datasetid=None,
    remotepath=None,
    useronly=False,
    startswith=None,
    tags=None,
    taggedonly=False,
    completedonly=False,
    group=None,
    filelist=False,
    execid=None,
    returnobj=False,
):
    """Get a list of datasets filtered by various arguments

    Parameters
    ----------
    session : Session
        A Session object
    public : bool
        If set to True it will only return public datasets. If set to False it will only return private datasets.
        If set to None this parameter will be ignored.
    datasetid : int
        The ID of a specific dataset for which we want to retrieve information
    remotepath : str
        The remote (virtual) path at which the dataset is located
    useronly : bool
        Returns only datasets of the currently logged in user of the Session
    startswith : str
        Returns any datasets whose remote (virtual) path starts with the specific string
    tags : list
        Returns only datasets which have the specified tags
    taggedonly : bool
        If set to True it will only return datasets which have tags
    completedonly : bool
        If set to True it will only return datasets whose jobs have completed successfully
    group : str
        Only get datasets related to a job group
    filelist : bool
        Set to True to return the files of each dataset as well
    execid : str
        Search for datasets produced by this execution ID
    returnobj : bool
        Set to True to return Dataset objects instead of dictionaries

    Returns
    -------
    datasetlist : list
        A list of datasets retrieved with the above filters

    Examples
    --------
    >>> datasets = get_datasets(session, remotepath="KdeepTrainer/models/PDBBind2019")
    >>> datasets = get_datasets(session, tags=["app:kdeep"])
    """
    session._require_log_in()

    if tags is not None:
        tags = ensurelist(tags)

    # Enforce file list when returning objects
    filelist = True if returnobj else filelist

    headers = {
        "token": session._token,
        "userOnly": str(useronly),
        "datasetId": str(datasetid) if datasetid is not None else "",
        "filePath": remotepath if remotepath is not None else "",
        "public": str(public) if public is not None else "",
        "startsWith": startswith if startswith is not None else "",
        "tags": ",".join(tags) if tags is not None else "",
        "taggedOnly": str(taggedonly),
        "completedOnly": str(completedonly),
        "group": str(group) if group is not None else "",
        "filelist": str(filelist) if filelist is not None else "",
        "execID": execid if execid is not None else "",
    }

    r = _request_url(
        "get",
        f"{session._server_endpoint}/datacenter",
        headers=headers,
        _logger=False,
    )
    if r is None:
        return

    datasets = json.loads(r.text)
    for ds in datasets:
        ds["created_at"] = parse_timestamp_utc(ds["created_at"])
        ds["updated_at"] = parse_timestamp_utc(ds["updated_at"])

    if datasets is None:
        return []

    if returnobj:
        for i, ds in enumerate(datasets):
            datasets[i] = Dataset(ds["id"], _session=session, _props=ds)

    return datasets


def remove_dataset(session, datasetid, _logger=True):
    """Removes (deletes) a dataset from the backend

    Parameters
    ----------
    session : Session
        A Session object
    datasetid : int
        The ID of the dataset we want to delete
    _logger : bool
        Set to False to reduce verbosity
    """
    session._require_log_in()

    headers = {"token": session._token}

    r = _request_url(
        "delete",
        f"{session._server_endpoint}/datacenter/{datasetid}",
        headers=headers,
        _logger=_logger,
    )

    if r is None:
        return

    if _logger:
        logger.info(f"Dataset {datasetid} was deleted successfully.")


def move_dataset(session, datasetid, remotepath, _logger=True):
    """Changes the remote location of a dataset

        Parameters
    ----------
    session : Session
        A Session object
    datasetid : int
        The ID of the dataset we want to delete
    remotepath : str
        The new remote location of the dataset
    _logger : bool
        Set to False to reduce verbosity
    """
    session._require_log_in()

    headers = {"token": session._token, "remotepath": remotepath}

    r = _request_url(
        "put",
        f"{session._server_endpoint}/datacenter/{datasetid}",
        headers=headers,
        _logger=_logger,
    )

    if r is None:
        return

    if _logger:
        logger.info(f"Dataset {datasetid} was moved successfully to {remotepath}.")


def update_dataset_comments(session, datasetid, comments, _logger=True):
    """Changes the remote location of a dataset

        Parameters
    ----------
    session : Session
        A Session object
    datasetid : int
        The ID of the dataset we want to delete
    comments : str
        The new comments of the dataset
    _logger : bool
        Set to False to reduce verbosity
    """
    session._require_log_in()

    headers = {"token": session._token, "comments": comments}

    r = _request_url(
        "put",
        f"{session._server_endpoint}/datacenter/{datasetid}",
        headers=headers,
        _logger=_logger,
    )

    if r is None:
        return

    if _logger:
        logger.info(f"Dataset {datasetid} comments were updated.")


class DataCenterError(Exception):
    pass


def _throw_error(message, _logger=False):
    if _logger:
        logger.error(message)
    else:
        raise DataCenterError(message)


def _request_url(*args, **kwargs):
    return _requestURL(*args, **kwargs, _throwError=_throw_error)


class Dataset:
    def __init__(self, datasetid, files=(), _session=None, _props=None) -> None:
        if _session is None:
            raise RuntimeError("Please specify session object in _session argument")
        self._session = _session
        self.datasetid = datasetid
        self.files = ensurelist(files)
        self._session._require_log_in()

        # Handle input case where user gives datasetid="dc://952874?files=/index.csv,/bar/foo.txt"
        if isinstance(datasetid, str) and datasetid.startswith("dc://"):
            pieces = datasetid.split("?files=")
            self.datasetid = int(pieces[0].split("/")[2])
            if len(pieces) == 2:
                self.files = pieces[1].split(",")

        if _props is None:
            self.update()
        else:
            self.props = _props

    def subset(self, key):
        """Gets a subset of the dataset

        Parameters
        ----------
        key : str or list or regex
            Select files of the dataset either as a single string, a list of strings or a regular expression

        Examples
        --------
        >>> ds2 = ds.subset(["mol6.xtc", "mol6.pdb"])
        >>> ds2 = ds.subset(re.compile(".*.png"))

        Or alternatively
        >>> ds2 = ds[["mol6.xtc", "mol6.pdb"]]
        >>> ds2 = ds[re.compile(".*.png")]
        """
        if isinstance(key, re.Pattern):
            files = []
            for ff in self.props["files"]:
                if key.match(ff):
                    files.append(ff)
            logger.info(f"Regular expression matched files: {files}")
        else:
            files = ensurelist(key)
            for ff in files:
                if ff not in self.props["files"]:
                    raise FileNotFoundError(
                        f"File {ff} not in file list of dataset {self.props['files']}. You might have to use the `update` method if files have changed."
                    )

        return Dataset(
            self.datasetid, files=files, _session=self._session, _props=self.props
        )

    def __getitem__(self, key):
        return self.subset(key)

    def update(self):
        ds = get_datasets(self._session, datasetid=self.datasetid, filelist=True)
        if ds is None:
            raise RuntimeError(f"Could not find dataset {self.datasetid} in backend")
        self.props = ds[0]

    def __str__(self) -> str:
        return self.identifier

    def __repr__(self) -> str:
        repr = f"<{self.__class__.__module__}.{self.__class__.__name__} object at {hex(id(self))}>\n"
        repr += f"Dataset: {self.__str__()}"
        for pp in sorted(self.props):
            repr += f"\n  {pp}: {self.props[pp]}"
        return repr

    def download(self, path, tmpdir=None, attempts=1, _logger=True):
        """Download the dataset from the backend

        Parameters
        ----------
        path : str
            The location to which to download the dataset
        tmpdir : str
            A location to store temporary data. If set to None, the default is /tmp/
        attempts : int
            Number of times to attempt uploading the file. Can help with unstable connections
        _logger : bool
            Set to False to reduce the verbosity

        Examples
        --------
        >>> ds.download("./dataset_data/")
        """
        return download_dataset(
            self._session,
            datasetid=self.datasetid,
            path=path,
            tmpdir=tmpdir,
            attempts=attempts,
            files=self.files,
            _logger=_logger,
        )

    def list_files(self):
        if len(self.files):
            return None
        return self.props["files"]

    def remove(self, _logger=True):
        if len(self.files):
            raise RuntimeError(
                "Cannot remove individual files from dataset. Please run the remove command from the complete dataset object."
            )

        return remove_dataset(self._session, datasetid=self.datasetid, _logger=_logger)

    def remove_tags(self):
        raise NotImplementedError("remove_tags is not implemented yet")

    def move(self, remotepath):
        move_dataset(self._session, self.datasetid, remotepath, _logger=False)
        self.update()

    def update_comments(self, comments):
        update_dataset_comments(self._session, self.datasetid, comments, _logger=False)
        self.update()

    @property
    def identifier(self):
        id_str = f"dc://{self.datasetid}"
        if len(self.files):
            id_str += f"?files={','.join(self.files)}"
        return id_str


class DataCenter:
    """Class which manages all the datasets in the PlayMolecule backend

    Parameters
    ----------
    session : Session object
        A Session object
    """

    def __init__(self, session):
        self._session = session

    def get_datasets(
        self,
        public=None,
        datasetid=None,
        remotepath=None,
        useronly=False,
        startswith=None,
        tags=None,
        taggedonly=False,
        completedonly=False,
        group=None,
        filelist=False,
        execid=None,
        returnobj=False,
        _logger=True,
    ):
        """Get a list of datasets filtered by various arguments

        Parameters
        ----------
        public : bool
            If set to True it will only return public datasets. If set to False it will only return private datasets.
            If set to None this parameter will be ignored.
        datasetid : int
            The ID of a specific dataset for which we want to retrieve information
        remotepath : str
            The remote (virtual) path at which the dataset is located
        useronly : bool
            Returns only datasets of the currently logged in user of the Session
        startswith : str
            Returns any datasets whose remote (virtual) path starts with the specific string
        tags : list
            Returns only datasets which have the specified tags
        taggedonly : bool
            If set to True it will only return datasets which have tags
        completedonly : bool
            If set to True it will only return datasets whose jobs have completed successfully
        group : str
            Only get datasets related to a job group
        filelist : bool
            Set to True to return the files of each dataset as well
        execid : str
            Search for datasets produced by this execution ID
        returnobj : bool
            Set to True to return Dataset objects instead of dictionaries
        _logger : bool
            Set to False to reduce verbosity

        Returns
        -------
        datasetlist : list
            A list of datasets retrieved with the above filters

        Examples
        --------
        >>> datasets = dc.get_datasets(remotepath="KdeepTrainer/models/PDBBind2019")
        >>> datasets = dc.get_datasets(tags=["app:kdeep"])
        """
        datasets = get_datasets(
            self._session,
            public=public,
            datasetid=datasetid,
            remotepath=remotepath,
            useronly=useronly,
            startswith=startswith,
            tags=tags,
            taggedonly=taggedonly,
            completedonly=completedonly,
            group=group,
            filelist=filelist,
            execid=execid,
            returnobj=returnobj,
        )

        if not returnobj and _logger:
            columns = "{:<10} {:<49} {:<20} {:<6} {:<8} {:<36} {:<20} {:<20}"
            print(
                columns.format(
                    "ID",
                    "RemotePath",
                    "Comments",
                    "Public",
                    "FileSize",
                    "ExecID",
                    "DateCreated",
                    "DateUpdated",
                )
            )

            for ds in datasets:
                print(
                    columns.format(
                        ds["id"],
                        ds["filepath"],
                        ds["comments"][:20],
                        "True" if ds["public"] else "False",
                        format_filesize(ds["filesize"]),
                        ds["execid"],
                        utc_timestamp_to_local(ds["created_at"]).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        utc_timestamp_to_local(ds["updated_at"]).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    )
                )
        else:
            return datasets

    def upload_dataset(
        self,
        localpath,
        remotepath,
        comments="",
        public=False,
        execid="",
        overwrite=False,
        tags=None,
        tmpdir=None,
        attempts=1,
        _logger=True,
    ):
        """Uploads a dataset to the backend data center

        Parameters
        ----------
        localpath : str
            The location of the file we want to upload
        remotepath : str
            The remote (virtual) location to which the file should be uploaded
        comments : str
            Comments to attach to the specific dataset
        public : bool
            Set to True to make the dataset public (available to all users)
        execid : str
            Optionally you can relate this dataset to a specific job execution by passing it's job ID
        overwrite : bool
            Set to True to overwrite existing datasets at the specified remote (virtual) location
        tags : list of str
            A list of tags to attach to the specific dataset
        tmpdir : str
            Location to use for creating the upload archive file. The file will be deleted after uploading.
            If set to None it will use /tmp/
        attempts : int
            Number of times to attempt uploading the file. Can help with unstable connections
        _logger : bool
            Set to False to reduce the verbosity
        """
        self._session._require_log_in()

        if not os.path.isfile(localpath) and not os.path.isdir(localpath):
            raise RuntimeError("upload_dataset only accepts files or folders")

        if tags is not None:
            tags = ensurelist(tags)

        fname = os.path.basename(os.path.abspath(localpath))

        tmpfile = tempname(suffix=".tar.gz", tmpdir=tmpdir)
        with tarfile.open(tmpfile, "w:gz") as tar:
            if os.path.isdir(localpath):
                tar.add(localpath, arcname="")
            else:
                tar.add(localpath, arcname=fname)

        # If you specify a remote folder, append the file name for the remote path
        if remotepath.endswith("/"):
            remotepath = remotepath + fname

        # Tags need to be all lower case and strip whitespace
        if tags is not None:
            tags = [tag.lower().strip().replace(" ", "_") for tag in tags]
            for tag in tags:
                if not re.match("^[a-zA-Z0-9_:]+$", tag):
                    raise RuntimeError(
                        "Tags need to be alphanumeric only and can contain _ or :"
                    )

        files = {"uploadfile": (fname, open(tmpfile, "rb"))}
        headers = {"token": self._session._token}
        data = {
            "remotepath": remotepath,
            "comments": comments,
            "public": public,
            "execid": execid,
            "overwrite": overwrite,
            "tags": ",".join(tags) if tags is not None else "",
        }

        uploaded = False
        while not uploaded and attempts > 0:
            try:
                result = _request_url(
                    "post",
                    f"{self._session._server_endpoint}/datacenter",
                    headers=headers,
                    files=files,
                    data=data,
                    _logger=_logger,
                )
            except Exception as e:
                attempts -= 1
                _throw_error(
                    f"Error uploading dataset {localpath} with error {e}. Retrying in 5s. Attempts remaining {attempts}.",
                    _logger,
                )
                time.sleep(5)
            else:
                uploaded = True

        os.remove(tmpfile)

        if not uploaded or result is None:
            _throw_error(
                f"Failed to upload dataset {localpath} to {remotepath}",
                _logger,
            )
            return

        if _logger:
            logger.info(f"File {localpath} was uploaded successfully.")

        return int(result.json()["id"])

    def remove_dataset(self, datasetid, _logger=True):
        """Removes (deletes) a dataset from the backend

        Parameters
        ----------
        datasetid : int
            The ID of the dataset we want to delete
        _logger : bool
            Set to False to reduce verbosity
        """
        return remove_dataset(self._session, datasetid=datasetid, _logger=_logger)

    def download_dataset(self, datasetid, path, tmpdir=None, attempts=1, _logger=True):
        """Download a dataset from the backend

        Parameters
        ----------
        datasetid : int
            The ID of the dataset we want to download
        path : str
            The location to which to download the dataset
        tmpdir : str
            A location to store temporary data. If set to None, the default is /tmp/
        attempts : int
            Number of times to attempt uploading the file. Can help with unstable connections
        _logger : bool
            Set to False to reduce the verbosity

        Examples
        --------
        >>> dc.download_dataset(182, "./dataset_182/")
        """
        return download_dataset(
            self._session,
            datasetid=datasetid,
            path=path,
            tmpdir=tmpdir,
            attempts=attempts,
            _logger=_logger,
        )

    def get_dataset_tags(self, datasetid, _logger=True):
        """Returns tags associated with a dataset

        Parameters
        ----------
        datasetid : int
            The ID of the dataset for which to return tags
        _logger : bool
            Set to False to reduce verbosity
        """
        self._session._require_log_in()

        headers = {"token": self._session._token}

        r = _request_url(
            "get",
            f"{self._session._server_endpoint}/datacenter/{datasetid}/tags",
            headers=headers,
            _logger=_logger,
        )

        if r is None:
            return

        response = json.loads(r.text)
        return [] if response is None else response

    def remove_dataset_tag(self, datasetid, tag, _logger=True):
        """Removes a tag attached to a dataset

        Parameters
        ----------
        datasetid : int
            The ID of the dataset
        tag : str
            The tag we want to remove from the dataset
        _logger : bool
            Set to False to reduce verbosity
        """
        self._session._require_log_in()

        headers = {"token": self._session._token}

        r = _request_url(
            "delete",
            f"{self._session._server_endpoint}/datacenter/{datasetid}/tags/{tag.lower()}",
            headers=headers,
            _logger=_logger,
        )

        if r is None:
            return

        if _logger:
            logger.info(f"Tag {tag} was deleted from dataset {datasetid} successfully.")
