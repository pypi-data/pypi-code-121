# (c) 2015-2022 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
from protocolinterface import ProtocolInterface, val
from protocolinterface.validators import _Validator
from playmolecule.utils import get_destination_folder, ensurelist, _requestURL
import json
import os
import shutil
import tempfile
import time
import logging
import enum


logger = logging.getLogger(__name__)


class JobBucketNotFoundError(Exception):
    pass


class JobConfigNotLoadedError(Exception):
    pass


@enum.unique
class JobStatus(enum.IntEnum):
    """Job status codes describing the current status of a job

    WAITING_DATA : Waiting for communication fromm the job. Job has not reached the queue yet for computation.
    VALIDATING : Job is pending validation by admins
    WAITING_APPROVAL : Job is pending approval by admins
    RUNNING : Job is currently running
    COMPLETED : Job has successfully completed
    ERROR : Job has exited with an error
    QUEUED : Job is queued for execution
    SLEEPING : Job is sleeping and will be respawned soon. Used by periodically executing apps.
    """

    WAITING_DATA = 0
    VALIDATING = 1
    WAITING_APPROVAL = 2
    RUNNING = 3
    COMPLETED = 4
    ERROR = 5
    QUEUED = 6
    SLEEPING = 7

    def describe(self):
        codes = {
            0: "Waiting data",
            1: "Validating",
            2: "Waiting approval",
            3: "Running",
            4: "Completed",
            5: "Error",
            6: "Queued",
            7: "Sleeping",
        }
        return codes[self.value]

    def __str__(self):
        return self.describe()


class JobError(Exception):
    pass


def _throwError(message, _logger=False):
    if _logger:
        logger.error(message)
    else:
        raise JobError(message)


def _request_url(*args, **kwargs):
    return _requestURL(*args, **kwargs, _throwError=_throwError)


def short_execid(execid):
    """Returns the short execution ID of a job from the full execution ID"""
    return execid[:8].upper()


class StringOrDataset(_Validator):
    def validate(self, value):
        from playmolecule.datacenter import Dataset

        if not isinstance(value, str) and not isinstance(value, Dataset):
            raise ValueError(f'the value "{value}" must be a string or dataset object')


class Job(ProtocolInterface):
    """Create a Job object given the user session and an app id.

    Parameters
    ----------
    session: Session
        The user session
    appid: str
        The app ID
    execid: str
        The ID of the job if it has already been submited
    job_json : dict
        A dictionary from which to instantiate the job. Useful when creating a job from data from the API
    strict : bool
        If strict is True, Job creation will fail if not able to load correctly existing app configuration into the Job.
    """

    def __init__(
        self,
        session,
        appid,
        execid=None,
        job_json=None,
        strict=True,
    ):
        from playmolecule.datacenter import DataCenter

        super().__init__()
        self._session = session
        self._appid = appid
        self._execid = execid
        self._parentid = None

        self._datacenter = DataCenter(self._session)

        self._periodicity = 0
        self._arg("inputpath", "string", "input path", "/tmp", val.String())
        self._arg("output", "string", "Output path", ".", val.String())
        self._arg("description", "string", "job description", "", val.String())
        self._arg("group", "string", "job group", "", val.String())
        self._arg("name", "string", "job name", "", val.String())

        # Load basic job info for the above properties
        if job_json is not None:
            self._job_properties_from_json(job_json)

        # Create properties for the App-specific arguments
        if self._appid is not None:
            self._create_app_properties()
            if job_json is not None:
                # Load existing job configuration
                job_config_json = self._job_config_exists(job_json, strict)
                if job_config_json is not None:
                    self._job_config_from_json(job_config_json, strict)

    def _job_config_exists(self, job_json, strict):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = self._download(
                "config", tmpdir, execid=job_json["id"], _logger=False
            )
            if config_file is None:
                msg = f"Job {job_json['id']} doesn't have a config object."
                if strict:
                    raise JobBucketNotFoundError(msg)
                else:
                    logger.warning(msg)
                    return None

            config_json = json.load(open(config_file, "rb"))
        return config_json

    def _create_app_properties(self):
        response = _request_url(
            "get",
            f"{self._server_endpoint}/apps/{self._appid}",
            headers={"token": self._token},
        )
        if response is None:
            raise RuntimeError("Could not get App information from server")

        app_arguments = json.loads(response.text)
        for param in app_arguments["params"]:
            validator = self._get_validator(param["type"])
            value = self._get_value(param["type"], param["value"], param["name"])
            self._arg(
                param["name"],
                param["type"],
                param["description"],
                value,
                validator,
                required=param["mandatory"],
            )

    def _job_properties_from_json(self, job_json):
        self._appid = job_json["appid"]
        self._execid = job_json["id"]
        self._parentid = job_json["parentid"]
        self.name = job_json["name"]
        self.group = job_json["group"]
        self.description = job_json["description"]

    def _job_config_from_json(self, job_config_json, strict):
        params = job_config_json["params"]
        for i in range(0, len(params)):
            key = params[i]["name"]
            value = params[i]["value"]
            try:
                value = self._get_value(params[i]["type"], value, key)
                setattr(self, key, value)
            except Exception as e:
                msg = f"Could not set Job attribute {key} with error {e}. The Job was possibly spawned with an older app version."
                if strict:
                    raise JobConfigNotLoadedError(msg)
                else:
                    logger.warning(msg)

    # TODO: accept more synonyms
    def _get_validator(self, type):
        if type == "bool":
            return val.Boolean()
        elif type == "int":
            return val.Number(int, "ANY")
        elif type == "string":
            return val.String()
        elif type == "file":
            return StringOrDataset()
        elif type == "float":
            return val.Number(float, "ANY")
        elif type == "fileORstring":
            return val.String()

    def _get_value(self, type, value, name):
        if value is None:
            return None

        if type == "bool":
            if value.lower() == "true":
                return True
            elif value.lower() == "false":
                return False
            raise ValueError(f'Invalid bool value "{value}" for argument {name}')
        elif type == "int":
            if value == "":
                return None
            try:
                converted_value = int(value)
                return converted_value
            except ValueError:
                raise ValueError(f'Invalid int value "{value}" for argument {name}')
        elif type == "float":
            if value == "":
                return None
            try:
                converted_value = float(value)
                return converted_value
            except ValueError:
                raise ValueError(f'Invalid float value "{value}" for argument {name}')
        elif type == "string" or type == "fileORstring" or type == "file":
            return value

    @property
    def _token(self):
        return self._session._token

    @property
    def _server_endpoint(self):
        return self._session._server_endpoint

    @property
    def _short_execid(self):
        return short_execid(self._execid)

    def submit(self, child_of=None, queue_config=None, _logger=True):
        """Submits the job to the PlayMolecule backend server.

        Parameters
        ----------
        child_of: str
            The id of another job. If provided, the new job will be submited as a child of that job.
        queue_config : dict
            A dictionary containing key-value pairs for defailed configuration for this job on the queueing system.
            You can specify "cpus", "memory" and "priority" for the job.
        _logger: bool
            Set to False to reduce verbosity

        Examples
        --------
        >>> job = sess.start_app("proteinprepare")
        >>> job.pdbid = "3ptb"
        >>> job.submit(queue_config={"ncpu": 2, "memory": 4000, "priority": 500})
        """
        from playmolecule.datacenter import Dataset

        appid = self._appid
        token = self._token
        headers = {
            "Content-type": "application/json",
            "Accept": "text/plain",
            "token": token,
        }
        # send execution with Description
        description = self.description

        request_dict = {
            "description": description,
            "group": self.group,
            "name": self.name,
            "specs": json.dumps(queue_config) if queue_config is not None else r"{}",
        }

        if child_of is not None:
            request_dict["parentid"] = child_of

        r = _request_url(
            "post",
            f"{self._server_endpoint}/apps/{appid}",
            headers=headers,
            json=request_dict,
            _logger=_logger,
        )
        if r is None:
            return

        if _logger:
            logger.debug(f"{self._server_endpoint}/apps/{appid}")
            logger.debug(r.text)

        python_obj = json.loads(r.text)
        config = python_obj["config"]
        token = python_obj["token"]
        self._execid = str(python_obj["id"])

        inputpath = os.path.join(self.inputpath, self._execid)
        os.makedirs(inputpath, exist_ok=True)

        # Check if files exist and copy them to the temp folder
        out_config = {
            "appid": config["appid"],
            "execid": self._execid,
            "params": [],
        }
        for param in config["params"]:
            name = param["name"]
            value = getattr(self, name)
            datatype = self._commands[name]["datatype"]
            if value is None and self._commands[name]["required"]:
                _throwError(f"Mandatory field '{name}' is empty.", _logger)
                return

            if isinstance(value, Dataset):
                # Convert Dataset object to a unique identifier
                value = value.identifier

            if (
                (datatype == "file" or datatype == "fileORstring")
                and value != ""
                and not value.startswith("dc://")
            ):
                value = getattr(self, name)
                if not os.path.isfile(value) and not os.path.isdir(value):
                    if (datatype == "file" or "." in value) and value is not None:
                        _throwError(f"File or folder does not exist: {value}", _logger)
                        return
                else:
                    filename = os.path.basename(os.path.normpath(value))
                    if os.path.isfile(value):
                        shutil.copy(
                            getattr(self, name),
                            os.path.join(inputpath, filename),
                        )
                    else:
                        shutil.copytree(
                            getattr(self, name),
                            os.path.join(inputpath, filename),
                        )
            else:
                if type(value) == bool:
                    value = str(value)

            out_config["params"].append(
                {
                    "name": name,
                    "value": value,
                    "type": param["type"],
                    "tag": param["tag"],
                }
            )

        # Write the current config out
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, f"{self._execid}.json")
            with open(config_file, "w") as f:
                json.dump(out_config, f, sort_keys=True, indent=4)
            self._upload("config", config_file, _logger=_logger)

        # Upload the inputs
        self._upload("input", inputpath)

        if os.path.isdir(inputpath):
            shutil.rmtree(inputpath, ignore_errors=True)

        # Send the start message for the execution
        request_dict = {"periodicity": self._periodicity}
        r = _request_url(
            "post",
            f"{self._server_endpoint}/jobs/{self._execid}",
            headers=headers,
            json=request_dict,
            _logger=_logger,
        )
        if r is None:
            return

        if _logger:
            logger.info(f"Execution submitted. Execution ID: {self._execid}")

    def _set_progress(self, info, completion, _logger=True):
        """Set the progress of a job execution.

        Parameters
        ----------
        info: str
            A string to be set as info progress
        completion: str
            The completion ratio of the job as a string in X/Y format where X current step, Y total steps.
        _logger: bool
            Set to False to reduce verbosity

        Examples
        --------
        >>> job.set_progress(info="Calculating features", completion="2/5")
        """
        if type(info) is not str or type(completion) is not str:
            _throwError("Error: 'info' and 'completion' must be strings", _logger)
            return

        token = self._token
        headers = {
            "Content-type": "application/json",
            "Accept": "text/plain",
            "admin": token,
        }
        request_dict = {"progressper": completion, "progressinfo": info}

        r = _request_url(
            "post",
            f"{self._server_endpoint}/jobs/{self._execid}/report",
            headers=headers,
            json=request_dict,
            _logger=_logger,
        )
        if r is None:
            return

    def retrieve(
        self,
        path=None,
        force=False,
        skip=False,
        on_status=(
            JobStatus.RUNNING,
            JobStatus.COMPLETED,
            JobStatus.ERROR,
            JobStatus.SLEEPING,
        ),
        attempts=5,
        execid_subdir=True,
        tmpdir=None,
        _logger=True,
    ):
        """Retrieve the results of a job execution.

        The output will be retrieved in the working directory if the argument path is not passed,
        inside a folder with the id job as a name.
        If this folder already exists, another one with a timestamp will be created.
        If the job has not completed, the function will try to download intermediate results.

        Parameters
        ----------
        path: str
            Destination folder
        force: bool
            If the destination folder exists and force == True, the destination folder will be removed.
        skip: bool
            If the destination folder exists and skip == True, nothing will be performed.
        on_status: list or JobStatus
            Restrict at which job status the results will be retrieved
        attempts: int
            How many times to attempt downloading the data from minio
        execid_subdir: bool
            If True it will create a subdirectory inside `path` with the execution ID as name and retrieve the results there
        tmpdir : str
            Set a different directory for storing temporary files. If set to None it defaults to /tmp/
        _logger: bool
            Set as True for printing the info and errors in sys.stdout. If False, it returns the same information as an object (default=True).

        Returns
        -------
        path: str
            The destination path of the retrieved data

        Examples
        --------
        >>> job.retrieve("./results/", on_status=(JobStatus.COMPLETED, JobStatus.ERROR))
        """
        on_status = ensurelist(on_status)

        path = os.path.abspath(self.output) if path is None else os.path.abspath(path)
        if execid_subdir:
            path = os.path.join(path, self._execid)
        path = get_destination_folder(path, force=force, skip=skip)
        if skip and os.path.exists(path):
            if _logger:
                logger.warning(f"Path already exists, skipping: {path}")
            return path

        if not hasattr(self, "_execid"):
            _throwError("Can't retrieve. Job does not exist.", _logger)
            return

        if _logger:
            logger.info("Retrieving data of execution: " + self._execid)

        job_info = self._getJobInfo(_logger=_logger)
        if job_info is None:
            return

        status = JobStatus(int(job_info["status"]))

        if status in on_status:
            self._download(
                "output",
                path,
                tmpdir=tmpdir,
                attempts=attempts,
                _logger=_logger,
            )
            return path
        else:
            if _logger:
                logger.info(
                    f"Current job status is '{status.describe()}' but only retrieving '{', '.join(map(str, on_status))}'"
                )

    def describe(self, _logger=True):
        """Describes the input parameters of an application

        Parameters
        ----------
        _logger: bool
            Set as True for printing the info and errors in sys.stdout.
            If False, it returns the same information as a list (default=True).

        Returns
        -------
        app_descr : list
            The description of the inputs of an app
        """
        from playmolecule.session import _describe_app

        r = _request_url(
            "get",
            f"{self._server_endpoint}/apps/{self._appid}",
            headers={"token": self._token},
            _logger=_logger,
        )
        if r is None:
            return

        python_obj = json.loads(r.text)
        if _logger:
            _describe_app(python_obj, self)
        else:
            return python_obj

    def get_status(self, _logger=True):
        """Prints or returns the job status

        Parameters
        ----------
        _logger: bool
            Set as True for printing the info and errors in sys.stdout.
            If False, it returns the same information (default=True).

        Returns
        -------
        status : JobStatus
            The current status of the job
        """
        job_info = self._getJobInfo(_logger=_logger)
        if job_info is None:
            return

        status = JobStatus(job_info["status"])

        if _logger:
            logger.info(f"Job Status: {status.describe()}")

        return status

    def get_progress(self, _logger=True):
        """Prints the job progress.

        Parameters
        ----------
        _logger: bool
            Set as True for printing the info and errors in sys.stdout. If False, it returns the same information as an object (default=True).

        Returns
        -------
        info : str
            The information on the current progress
        completion : str
            The completion percentage
        """
        info = ""
        completion = ""
        if hasattr(self, "_execid"):
            job_info = self._getJobInfo(_logger=_logger)
            if job_info is None:
                return

            info = job_info["progressinfo"]
            completion = job_info["progressper"]
            if _logger:
                print("%-20s %-20s" % ("Progress info:", info))
                print("%-20s %-20s" % ("Progress percentage:", completion))
            else:
                return info, completion
        else:
            _throwError("Job not submited", _logger)
            return

    def _set_start(self, _logger=True):
        """Sets the status of a job as running

        Parameters
        ----------
        _logger: bool
            Set to False to reduce verbosity
        """
        self._session.set_job_status(self._execid, JobStatus.RUNNING, _logger=_logger)

    def _set_complete(self, _logger=True):
        """Sets the status of a job as completed

        Parameters
        ----------
        _logger: bool
            Set to False to reduce verbosity
        """
        self._session.set_job_status(self._execid, JobStatus.COMPLETED, _logger=_logger)

    def _set_sleep(self, _logger=True):
        """Sets the status of a job as sleeping

        Parameters
        ----------
        _logger: bool
            Set to False to reduce verbosity.
        """
        self._session.set_job_status(self._execid, JobStatus.SLEEPING, _logger=_logger)

    def _set_error(self, error_info=None, _logger=True):
        """Sets the status of a job as error

        Parameters
        ----------
        error_info : str
            Pass verbose information on the cause of the error
        _logger: bool
            Set to False to reduce verbosity
        """
        self._session.set_job_status(
            self._execid, JobStatus.ERROR, error_info=error_info, _logger=_logger
        )

    def get_children(self, status=None, return_dict=False, _logger=True):
        """Returns the children of the job.

        Parameters
        ----------
        status: list of JobStatus
            Only get children with specific job statuses given in a list
        return_dict : bool
            Set to True to return a dictionary with the children information instead of Job objects
        _logger : bool
            Set to False to reduce verbosity

        Returns
        -------
        children : list
            The children of the job
        """
        if not hasattr(self, "_execid"):
            return None

        token = self._token
        headers = {
            "Content-type": "application/json",
            "Accept": "text/plain",
            "token": token,
        }
        if status is None:
            r = _request_url(
                "get",
                f"{self._server_endpoint}/jobs/{self._execid}/children",
                headers=headers,
                _logger=_logger,
            )
        else:
            request_dict = {"statuscodes": [int(s) for s in ensurelist(status)]}
            r = _request_url(
                "post",
                f"{self._server_endpoint}/jobs/{self._execid}/children",
                headers=headers,
                json=request_dict,
                _logger=_logger,
            )

        if r is None:
            return None

        python_obj = json.loads(r.text)
        if return_dict:
            return python_obj
        else:  # This will become the default
            childrenJobs = []
            statuses = []
            for child_json in python_obj:
                childrenJobs.append(
                    Job(session=self._session, appid=None, job_json=child_json)
                )
                statuses.append(child_json["status"])
            return childrenJobs, statuses

    def wait_children(
        self,
        on_status=(JobStatus.COMPLETED, JobStatus.ERROR),
        seconds=10,
        _logger=True,
    ):
        """Blocks execution until all the children of the job have reached the given status

        Parameters
        ----------
        on_status : JobStatus or list of JobStatus
            The status(es) at which a child job will stop being waited upon
        seconds : float
            The sleep time between status checking of the children jobs
        _logger: bool
            Set to False to reduce verbosity
        """
        from collections import Counter

        unfinishedStatus = set(JobStatus) - set(ensurelist(on_status))

        while True:
            running_child_jobs = self.get_children(
                status=unfinishedStatus, return_dict=True
            )
            nrunning = len(running_child_jobs)

            if nrunning == 0:
                break

            statuses = Counter(
                [str(JobStatus(cj["status"])) for cj in running_child_jobs]
            )

            if _logger:
                logger.info(
                    f"There are still {nrunning} children running with status {dict(statuses)}. Sleeping for {seconds} seconds."
                )
            time.sleep(seconds)

        if _logger:
            logger.info("No children currently running")

    def wait(
        self,
        on_status=(JobStatus.COMPLETED, JobStatus.ERROR),
        seconds=10,
        _logger=True,
        _return_dataset=True,
    ):
        """Blocks execution until the job has reached the specific status or any of a list of statuses.

        Parameters
        ----------
        on_status : JobStatus or list of JobStatus
            The status(es) at which the job will not be waited upon and the code execution will continue.
        seconds : float
            The sleep time between status cheching
        _logger: bool
            Set to False to reduce verbosity
        """
        from playmolecule.datacenter import Dataset

        on_status = ensurelist(on_status)

        while True:
            status = self.get_status(_logger=False)
            if status in on_status:
                break

            if _logger:
                logger.info(
                    f"Job status \"{status.describe()}\". Waiting for it to reach ({', '.join(map(str, on_status))}). Sleeping for {seconds} seconds."
                )
            time.sleep(seconds)

        if _return_dataset:
            try:
                result = self._datacenter.get_datasets(
                    remotepath=f"{self._execid}/output", _logger=False
                )[0]
                return Dataset(
                    datasetid=result["id"], _session=self._session, _props=result
                )
            except Exception:
                return None

    def read_arguments(self, filename, ftype="yaml"):
        """Reads argument values of the job from a json or yaml file

        Parameters
        ----------
        filename : str
            The name of the file (incl. extension) from which to read the arguments
        ftype : str
            Can be either "json" or "yaml" depending on what file format you want to read
        """
        import yaml

        with open(filename, "r") as f:
            if ftype == "json":
                argdict = json.load(f)
            elif ftype == "yaml":
                argdict = yaml.load(f, Loader=yaml.FullLoader)
            else:
                raise AttributeError(
                    f"Invalid file type {ftype}. Can be only 'json' or 'yaml'."
                )

        for key, value in argdict.items():
            setattr(self, key, value)

    def write_arguments(self, filename, ftype="yaml"):
        """Writes the current argument values of the job to a json or yaml file

        Parameters
        ----------
        filename : str
            The name of the file (incl. extension) in which to write the arguments
        ftype : str
            Can be either "json" or "yaml" depending on what file format you want to write
        """
        import yaml

        argdict = {
            key: value for key, value in self.__dict__.items() if key in self._commands
        }
        with open(filename, "w") as f:
            if ftype == "json":
                json.dump(argdict, f, sort_keys=True, indent=4)
            elif ftype == "yaml":
                yaml.dump(argdict, f)
            else:
                raise AttributeError(
                    f"Invalid file type {ftype}. Can be only 'json' or 'yaml'."
                )

    def cancel(self, _logger=True):
        """Cancel the job

        Cancels the job. This will set the status to ERROR and stop any running execution (children as well)
        """
        self._session.cancel_job(self._execid, _logger=_logger)

    def _delete(self, _logger=True):
        """Deletes the job and all it's information from the backend"""
        self._session.delete_job(self._execid, _logger=_logger)

    def _getJobInfo(self, execid=None, _logger=True):
        if execid is None:
            if not hasattr(self, "_execid"):
                _throwError(
                    "No execid found in job object. The job has possibly not been submitted yet.",
                    _logger,
                )
            execid = self._execid

        headers = {
            "Content-type": "application/json",
            "Accept": "text/plain",
            "token": self._token,
        }

        r = _request_url(
            "get",
            f"{self._server_endpoint}/jobs/{execid}",
            headers=headers,
            _logger=_logger,
        )
        return json.loads(r.text) if r is not None else None

    def get_error_info(self, _logger=True):
        """Get information related to an errored job

        Parameters
        ----------
        _logger: bool
            Set as True for printing the info and errors in sys.stdout.
            If False, it returns the same information (default=True).

        Returns
        -------
        error_info : str
            Information on the cause of the error
        """
        job_info = self._getJobInfo(_logger=_logger)
        if job_info is None:
            return ""

        error_info = job_info.get("error_info", "")

        if _logger:
            logger.info(f"Error Info: {error_info}")

        return error_info

    def _download(self, name, path, tmpdir=None, attempts=5, execid=None, _logger=True):
        if name not in ("input", "output", "config", "intermediate"):
            raise RuntimeError(
                "name argument must be either input, output, config or intermediate"
            )

        if execid is None:
            execid = self._execid

        ds = self._datacenter.get_datasets(remotepath=f"{execid}/{name}", _logger=False)
        if len(ds) == 0:
            if _logger:
                logger.info(f"No data found for dataset {execid}/{name}")
            return

        assert (
            len(ds) == 1
        ), "More than one job dataset found with the same name. This should never happen."

        return self._datacenter.download_dataset(
            ds[0]["id"], path, tmpdir=tmpdir, attempts=attempts, _logger=_logger
        )

    def _upload(
        self,
        name,
        path,
        comments=None,
        public=False,
        overwrite=True,
        tmpdir=None,
        attempts=5,
        execid=None,
        appname=None,
        remotepath=None,
        _logger=True,
    ):
        if name not in ("input", "output", "config", "intermediate"):
            raise RuntimeError(
                "name argument must be either input, output, config or intermediate"
            )

        if execid is None:
            execid = self._execid

        if appname is None:
            appname = self._appid.lower().split("-")[0]

        if comments is None:
            try:
                comments = f"{self.name} {self.description} {self.group}".strip()
            except Exception:
                comments = ""

        if remotepath is None:
            remotepath = f"{execid}/{name}"

        self._datacenter.upload_dataset(
            localpath=path,
            remotepath=remotepath,
            comments=comments,
            public=public,
            execid=execid,
            overwrite=overwrite,
            tmpdir=tmpdir,
            attempts=attempts,
            _logger=_logger,
            tags=[f"app:{appname}:{name}", f"type:{name}"],
        )
