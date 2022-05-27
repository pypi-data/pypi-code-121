# (c) 2015-2022 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
from playmolecule.job import Job, JobStatus
from playmolecule.utils import (
    get_destination_folder,
    ensurelist,
    parse_timestamp_utc,
    utc_timestamp_to_local,
    _requestURL,
)
from playmolecule.datacenter import DataCenter
from playmolecule.config import _config
from dateutil.parser import parse as dateparse
import time
import logging
import requests
import json
import os


logger = logging.getLogger(__name__)


class UserNotFoundError(Exception):
    pass


class UserFailedRegistrationError(Exception):
    pass


class UserUpdateError(Exception):
    pass


class SessionError(Exception):
    pass


def _throw_error(message, _logger=False):
    if _logger:
        logger.error(message)
    else:
        raise SessionError(message)


def _request_url(*args, **kwargs):
    return _requestURL(*args, **kwargs, _throwError=_throw_error)


def _describe_app(python_obj, job=None):
    columns = "{:<30} {:<20} {:<20} {:<30} {:<40}"
    print(
        columns.format(
            "Name",
            "Type",
            "Mandatory",
            "Value" if job else "Default",
            "Description",
        )
    )

    nonprivparams = [param for param in python_obj["params"] if param["name"][0] != "_"]
    mandatoryparams = sorted(
        [param for param in nonprivparams if param["mandatory"]],
        key=lambda param: param["name"],
    )
    optionalparams = sorted(
        [param for param in nonprivparams if not param["mandatory"]],
        key=lambda param: param["name"],
    )
    printparams = mandatoryparams + optionalparams

    for param in printparams:
        print(
            columns.format(
                param["name"],
                param["type"],
                "True" if param["mandatory"] else "False",
                str(getattr(job, param["name"])) if job else param["value"],
                param["description"],
            )
        )

    if len(python_obj["periodicities"]):
        columns = "{:<30} {:<20} {:<20}"
        print(columns.format("Name", "param", "value"))
        for p in python_obj["periodicities"]:
            if p["name"][0] != "_":
                print(columns.format(p["name"], p["param"], p["value"]))


def _find_token(token):
    """Searches for the token file in the default locations and env vars"""
    if token is not None:
        return token

    fileenv = ["PM_TOKEN_FILE"]
    tokenenv = ["PM_TOKEN"]
    tokenfiles = [os.path.join(os.path.expanduser("~"), ".playmolecule", "token.json")]

    msg = "Looking for PM token in [config]"
    try:
        token = _config.get("user", "token")
    except Exception as e:
        msg += f": {e}"
    else:
        msg += ": Found!"
        logger.info(msg)
        return token
    logger.info(msg)

    for envvar in fileenv:
        val = os.getenv(envvar)
        msg = f"Looking for PM token in [env: {envvar} => {val}]"
        if val is not None and os.path.exists(val):
            try:
                token = json.load(open(val, "r"))["token"]
            except Exception:
                msg += ": Failed to parse json file!"
            else:
                msg += ": Found!"
                logger.info(msg)
                return token
        logger.info(msg)

    for envvar in tokenenv:
        val = os.getenv(envvar)
        msg = f"Looking for PM token in [env: {envvar}]"
        if val is not None:
            msg += ": Found!"
            token = val
            logger.info(msg)
            return token
        logger.info(msg)

    for tokenfile in tokenfiles:
        msg = f"Looking for PM token in [{tokenfile}]"
        if os.path.exists(tokenfile):
            try:
                token = json.load(open(tokenfile, "r"))["token"]
            except Exception:
                msg += ": Failed to parse json file!"
            else:
                msg += ": Found!"
                logger.info(msg)
                return token
        logger.info(msg)

    logger.info("No PM token found.")
    return None


class Session:
    """The central class through which we control the PlayMolecule backend.

    Starts a PlayMolecule session with a user token, each user has his own unique token.
    There are some operations which can only be performed by using the Admin token.

    Parameters
    ----------
    token: str
        The user token. If None it will try to read it from the config file.
    wait_for_backend : bool
        If set to True, it will block execution until it manages to contact the PlayMolecule backend
    server_ip : str
        The IP address of the backend server. If None it will try to read it from the config file.
    server_port : int
        The port on which the backend server listens. If None it will try to read it from the config file.
    server_version : str
        The API version of the backend server. If None it will try to read it from the config file.
    server_protocol : str
        The protocol used by the backend server.

    Examples
    --------
    >>> s = Session("my_token")
    >>> s = Session("my_token", server_ip="127.0.0.1", server_port=8095, wait_for_backend=True)
    """

    def __init__(
        self,
        token=None,
        wait_for_backend=False,
        server_ip=None,
        server_port=None,
        server_version="v1",
        server_protocol="http",
    ):
        self._token = _find_token(token)
        self.output = "."

        if server_ip is None or server_port is None:
            val = os.getenv("PM_BACKEND_ENDPOINT")
            if val is not None:
                self._server_endpoint = val
            else:
                self._server_endpoint = (
                    _config.get("server", "endpoint")
                    + "/"
                    + _config.get("server", "version")
                )
        else:
            self._server_endpoint = (
                f"{server_protocol}://{server_ip}:{server_port}/{server_version}"
            )

        if wait_for_backend:
            self.wait_for_backend()

        services = self.get_service_status(_logger=False)
        down = [serv for serv, val in services.items() if not val["Status"]]
        if len(down) != 0:
            logger.warning(
                f"PMWS Server is currently reporting the following services as offline: {down}"
            )

        if not self._is_logged_in():
            logger.warning(
                "Please either use register(), login(), or pass your personal token to Session to use the API."
            )

    def wait_for_backend(self):
        """Blocks execution until it's able to contact the backend server"""
        while True:
            try:
                _ = _request_url(
                    "get",
                    f"{self._server_endpoint}/apps",
                    headers={"token": self._token},
                    _logger=False,
                )
                break
            except SessionError:
                logger.warning(
                    "Could not find PMWS backend. Sleeping for 5s and trying again"
                )
                time.sleep(5)

    def register(self, admin_token):
        """Registers a new user in the backend

        Parameters
        ----------
        admin_token : str
            The admin user token
        """
        from getpass import getpass

        mail = input("Email: ")
        username = input("Full name: ")
        password = getpass()
        # Hash the pass with some salt
        res = self._register_user(
            mail=mail, username=username, password=password, admin_token=admin_token
        )
        print(f"User registered with token: {res}")
        self._token = res

    def login(self):
        """Logs in a user retrieving the user token from the user name and password"""
        from getpass import getpass

        mail = input("Email: ")
        password = getpass()
        # Hash the pass with some salt
        res = self._get_user(mail=mail, password=password)
        token = res["token"]
        print(f"User logged in with token: {token}")
        self._token = token

    def change_password(self, email, old_pass, new_pass, admin_token=None):
        """Change the password of a user

        Parameters
        ----------
        email : str
            The email address of the user
        old_pass : str
            The old password of the user
        new_pass : str
            The new password for the user
        admin_token : str
            The admin user token. If None you are only able to modify the current user's password.
        """
        res = self._get_user(mail=email, password=old_pass, admin_token=admin_token)

        json_msg = {
            "token": self._token if admin_token is None else admin_token,
            "user_id": res["id"],
            "old_password": old_pass,
            "new_password": new_pass,
        }
        res = _request_url(
            "post",
            f"{self._server_endpoint}/password/change",
            json=json_msg,
            _logger=False,
            checkError=False,
        )
        status = res.status_code
        res = json.loads(res.text)
        if status != requests.codes["ok"]:
            raise RuntimeError(res["message"] if "message" in res else "")

    def _get_user(self, userid=None, mail=None, password=None, admin_token=None):
        request_dict = {}
        if userid is not None:
            request_dict["id"] = userid
        if mail is not None:
            request_dict["mail"] = mail
        if password is not None:
            request_dict["password"] = password
        if admin_token is not None:
            request_dict["admin_token"] = admin_token

        mailid = mail if mail is not None else userid

        res = _request_url(
            "post",
            f"{self._server_endpoint}/users/{mailid}",
            data=request_dict,
            _logger=False,
            checkError=False,
        )
        status = res.status_code
        res = json.loads(res.text)
        if status != requests.codes["ok"]:
            raise UserNotFoundError(res["message"] if "message" in res else "")

        return res

    def _register_user(self, admin_token, username, mail, googleid=None, password=None):
        headers = {"admin": admin_token}
        request_dict = {"mail": mail, "username": username}
        if googleid is not None:
            request_dict["googleid"] = googleid
        if password is not None:
            request_dict["password"] = password

        res = _request_url(
            "post",
            f"{self._server_endpoint}/users",
            headers=headers,
            data=request_dict,
            _logger=False,
            checkError=False,
        )
        status = res.status_code
        res = json.loads(res.text)
        if status != requests.codes["ok"]:
            raise UserFailedRegistrationError(
                res["message"] if "message" in res else ""
            )

        return res

    def _update_user(
        self,
        userid,
        admin_token,
        is_banned=None,
        is_verified=None,
        verified_name=None,
        institution_name=None,
    ):
        headers = {"admin": admin_token}
        request_dict = {"id": userid}
        if is_banned is not None:
            request_dict["is_banned"] = is_banned
        if is_verified is not None:
            request_dict["is_verified"] = is_verified
        if verified_name is not None:
            request_dict["verified_name"] = verified_name
        if institution_name is not None:
            request_dict["institution_name"] = institution_name

        res = _request_url(
            "put",
            f"{self._server_endpoint}/users/{userid}",
            headers=headers,
            data=request_dict,
            _logger=False,
            checkError=False,
        )
        status = res.status_code
        res = json.loads(res.text)
        if status != requests.codes["ok"]:
            raise UserUpdateError(res["message"] if "message" in res else "")

        return res

    def _get_all_users(self, admin_token):
        res = _request_url(
            "get",
            f"{self._server_endpoint}/users",
            headers={"admin": admin_token},
            _logger=False,
        )

        return json.loads(res.text)

    def _is_logged_in(self):
        return self._token is not None

    def _require_log_in(self):
        if not self._is_logged_in():
            raise RuntimeError(
                "Please either use login(), register(), or pass your personal token to Session to use the API."
            )

    def _get_apps(self):
        self._require_log_in()

        r = _request_url(
            "get",
            f"{self._server_endpoint}/apps",
            headers={"token": self._token},
            _logger=False,
        )
        if r is None:
            return

        res = json.loads(r.text)
        apps = {}
        apps_rev = {}
        for app in res:
            apps_rev[app["id"]] = f"{app['name']}_v{app['version']}"
            if app["name"] not in apps:
                apps[app["name"]] = {}
            version = float(app["version"])
            if version not in apps[app["name"]]:
                apps[app["name"]][version] = {"id": app["id"]}

        return apps, apps_rev

    def _get_app_id(self, appname, version=None, _logger=True):
        apps, _ = self._get_apps()

        appnamelower = appname.lower()
        # Lower-case the app names for comparison
        apps = {key.lower(): val for key, val in apps.items()}

        if appnamelower not in apps:
            _throw_error(f"The app {appname} does not exist", _logger)

        if version is None:
            version = sorted(apps[appnamelower])[
                -1
            ]  # Get latest version if not specified
        else:
            version = float(version)
            if version not in apps[appnamelower]:
                _throw_error(
                    f"Version {version} of app {appname} does not exist", _logger
                )

        return apps[appnamelower][version]["id"]

    def get_apps(self, _logger=True):
        """Returns or prints the available apps.

        The list of apps is printed if _logger is True else it's returned

        Parameters
        ----------
        _logger: bool
            Set as True for printing the info and errors in sys.stdout.
            If False, it returns the same information as an object.

        Returns
        -------
        app_list : list
            A list with all the app info
        """
        self._require_log_in()

        r = _request_url(
            "get",
            f"{self._server_endpoint}/apps",
            headers={"token": self._token},
            _logger=_logger,
        )
        if r is None:
            return

        python_obj = json.loads(r.text)
        if _logger:
            print("%-30s %-50s %-20s" % ("Name", "Description", "Version"))
            for app in python_obj:
                print(
                    "%-30s %-50s %-20s"
                    % (app["name"], app["description"], app["version"])
                )
        else:
            return python_obj

    def describe_app(self, appname, version=None, _logger=True):
        """
        Describe the input parameters of an app.

        Parameters
        ----------
        appname: str
            The app name
        version: str
            The app version to be described.
        _logger : bool
            Set to False to return the app information as a dictionary. Otherwise it will be printed to sys.stdout.
        """
        self._require_log_in()

        appid = self._get_app_id(appname, version, _logger)
        r = _request_url(
            "get",
            f"{self._server_endpoint}/apps/{appid}",
            headers={"token": self._token},
            _logger=_logger,
        )
        if r is None:
            return

        python_obj = json.loads(r.text)
        if _logger:
            _describe_app(python_obj, None)
        else:
            return python_obj

    def get_jobs(
        self,
        limit=None,
        group=None,
        appid=None,
        execid=None,
        count=False,
        in_status=None,
        not_in_status=None,
        newer_than=None,
        older_than=None,
        _logger=True,
    ):
        """Returns or prints a list of submitted jobs.

        Parameters
        ----------
        limit: int
            Maximum number of jobs to be listed or returned
        group: str
            The executions group to be returned
        appid: str
            Specify the id of an app to return only executions of this app
        execid: str
            Specify the execution ID of a job. It can accept a partial beginning of an execution ID or the whole execid
        count: bool
            If True it will only return the number of jobs matching the above criteria
        in_status : list
            A list of JobStatus codes. Jobs which are in any of the specified states will be returned
        not_in_status : list
            A list of JobStatus codes. Only jobs which don't belong to any of the specified states will be returned
        newer_than : int
            Return only jobs more recent than `newer_than` seconds.
        older_than : int
            Return only jobs more old than `older_than` seconds.
        _logger: bool
            Set as True for printing the info and errors in sys.stdout.
            If False, it returns the same information as a list (default=True).

        Returns
        -------
        execs: list
            A list of job executions
        """
        self._require_log_in()

        request_dict = {}
        if in_status is not None:
            request_dict["in_status"] = [int(s) for s in ensurelist(in_status)]
        if not_in_status is not None:
            request_dict["not_in_status"] = [int(s) for s in ensurelist(not_in_status)]
        if group is not None:
            request_dict["group"] = str(group)
        if appid is not None:
            request_dict["app_id"] = str(appid)
        if execid is not None:
            request_dict["exec_id"] = str(execid)
        request_dict["newer_than"] = int(newer_than) if newer_than is not None else -1
        request_dict["older_than"] = int(older_than) if older_than is not None else -1
        request_dict["limit"] = limit if limit is not None else -1
        request_dict["count"] = count

        r = _request_url(
            "get",
            f"{self._server_endpoint}/jobs",
            headers={"token": self._token},
            json=request_dict,
            _logger=_logger,
        )
        if r is None:
            return

        # _, apps_rev = self._get_apps()
        if count:
            return json.loads(r.text)

        executions = json.loads(r.text)[::-1]
        for exe in executions:
            exe["date"] = parse_timestamp_utc(exe["date"])
            if "{" in exe["specs"]:
                try:
                    exe["specs"] = json.loads(exe["specs"].replace("'", '"'))
                except Exception:
                    pass
            else:  # Compatibility with old jobs
                exe["specs"] = {"app": exe["specs"]}

        if _logger:
            strfmt = "{:<20} {:<37} {:<16s} {:<30} {:<30} {:<30}"
            print(strfmt.format("App", "ID", "Status", "Date", "Name", "Group"))
            for exe in executions:
                print(
                    strfmt.format(
                        exe["container"],
                        exe["id"],
                        str(JobStatus(int(exe["status"]))),
                        utc_timestamp_to_local(exe["date"]).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        exe["name"],
                        exe["group"],
                    )
                )
        else:
            return executions

    def get_job(self, execid=None, name=None, group=None, strict=True, _logger=True):
        """Finds and returns a Job object

        Parameters
        ----------
        execid : str
            The execution id
        name : str
            The name of an execution
        group : str
            The group of an execution
        strict : bool
            If strict is True, Job creation will raise exceptions if not able to load correctly the app configuration into the Job.
        _logger: bool
            If False, it will reduce verbosity.

        Returns
        -------
        job: Job
            The job object with all it's parameters set

        Examples
        --------
        >>> job = s.get_job(execid="3cadd50b-b208-4a3d-8cf3-d991d22e858a")
        """
        self._require_log_in()

        if execid is not None:
            url = f"{self._server_endpoint}/jobs/{execid}"
        elif name is not None and group is not None:
            url = f"{self._server_endpoint}/jobs/group/{group}/{name}"
        else:
            _throw_error("The job id or group and name has to specified", _logger)
            return

        r = _request_url("get", url, headers={"token": self._token}, _logger=_logger)
        if r is None:
            return

        job_info = json.loads(r.text)
        job = Job(session=self, appid=None, job_json=job_info, strict=strict)
        return job

    def start_app(self, appname, version=None, _logger=True):
        """Returns a new job object of the specified app.

        Parameters
        ----------
        appname: str
            The app name of the used app.
        version: str
            The app version to be used.
        _logger: bool
            Set as True for printing the info and errors in sys.stdout. If False, it returns the same information as an object (default=True).

        Returns
        -------
        job: Job
            The new job object

        Examples
        --------
        >>> job = s.start_app("ProteinPrepare")
        >>> job.pdbid = "3ptb"
        >>> job.submit()
        """
        self._require_log_in()

        appid = self._get_app_id(appname, version, _logger)
        job = Job(session=self, appid=appid)
        return job

    def retrieve_jobs(
        self,
        outdir=".",
        force=False,
        execid=None,
        name=None,
        group=None,
        recursive=False,
        _logger=True,
    ):
        """Retrieve the results of several jobs.

        Parameters
        ----------
        outdir : str
            Path to which to retrieve the jobs
        force: bool
            If force=True, the destination folder will be overwritten
        execid:
            The id of the job to be retrieved.
        name : str
            The name of an execution to be retrieved
        group : str
            The group of an execution to be retrieved
        recursive : bool
            Set to True to store the jobs in subfolders named by the job names
        _logger: bool
            Set to False to reduce verbosity

        Examples
        --------
        >>> s.retrieve_jobs("./results", execid="3cadd50b-b208-4a3d-8cf3-d991d22e858a")
        >>> s.retrieve_jobs("./results", group="my_job_group") # Will retrieve all jobs of the group
        """
        self._require_log_in()

        outdir = os.path.abspath(outdir)
        if execid is not None:
            job = self.get_job(execid=execid)
            if recursive:
                folder = job.name
                if job.name == "":
                    folder = execid
                outdir = get_destination_folder(
                    os.path.join(outdir, folder), force=force
                )
            else:
                outdir = get_destination_folder(
                    os.path.join(outdir, execid), force=force
                )
            os.makedirs(outdir, exist_ok=True)
            job.retrieve(path=outdir, force=False, _logger=_logger)
        elif group is not None and name is not None:
            job = self.get_job(group=group, name=name)
            inner_folder = os.path.join(group, name)
            outdir = get_destination_folder(
                os.path.join(outdir, inner_folder), force=force
            )
            os.makedirs(outdir, exist_ok=True)
            job.retrieve(path=outdir, force=False, _logger=_logger)
        elif group is not None and name is None:
            jobs = self.get_jobs(group=group, _logger=_logger)
            outdir = get_destination_folder(os.path.join(outdir, group), force=force)
            os.makedirs(outdir, exist_ok=True)
            for job in jobs:
                self.retrieve_jobs(
                    execid=job["id"],
                    outdir=outdir,
                    recursive=True,
                    _logger=_logger,
                )

    def set_job_status(self, execid, status, error_info=None, _logger=True):
        """Sets the status of a job

        Parameters
        ----------
        execid : str
            The execution ID of the job to modify
        status : JobStatus
            The status to which to set the job
        error_info : str
            If the status is Error you can provide verbose information on the error for the users
        _logger : bool
            Set to False to reduce verbosity

        Examples
        --------
        >>> s.set_job_status(execid="3cadd50b-b208-4a3d-8cf3-d991d22e858a", status=JobStatus.ERROR)
        """
        self._require_log_in()

        headers = {
            "Content-type": "application/json",
            "Accept": "text/plain",
            "token": self._token,
        }
        request_dict = {
            "status": int(status),
        }
        if error_info is not None:
            request_dict["error_info"] = str(error_info)

        r = _request_url(
            "put",
            f"{self._server_endpoint}/jobs/{execid}",
            headers=headers,
            json=request_dict,
            _logger=_logger,
        )
        if r is None:
            return

        if _logger:
            logger.info(f"Status of execution {execid} updated to {str(status)}")

    def get_service_status(self, _logger=True):
        """Gets the current status of all PlayMolecule backend services

        Parameters
        ----------
        _logger : bool
            Set to False to return the status of the services instead of printing them to sys.stdout
        """
        r = _request_url(
            "get",
            f"{self._server_endpoint}/services",
            _logger=_logger,
        )
        if r is None:
            return None

        res = json.loads(r.text)
        for key in res:
            res[key]["LastChecked"] = dateparse(res[key]["LastChecked"])

        if _logger:
            logger.info("Current service status:")
            for key, val in res.items():
                status = "Up" if val["Status"] else "Down"
                logger.info(
                    f"    {key:12s}: {status:10s} Last Checked: {val['LastChecked']}"
                )
        else:
            return res

    def cancel_job(self, execid, _logger=True):
        """Cancels a job.

        This will set the status to ERROR and stop any running execution (children as well)

        Parameters
        ----------
        execid : str
            The execution ID of the job we wish to cancel
        """
        self._require_log_in()

        headers = {
            "Content-type": "application/json",
            "Accept": "text/plain",
            "token": self._token,
        }

        r = _request_url(
            "delete",
            f"{self._server_endpoint}/jobs/{execid}",
            headers=headers,
            _logger=_logger,
        )
        if r is None:
            return

        if _logger:
            logger.info(f"Execution {execid} was cancelled")

    def delete_job(self, execid, _logger=True):
        """Deletes a job and all associated data and metadata related to it from the backend. Cannot be undone.

        Parameters
        ----------
        execid : str
            The execution ID of the job we wish to cancel
        _logger : bool
            If set to False it reduces the verbosity of the output
        """
        self._require_log_in()

        headers = {
            "Content-type": "application/json",
            "Accept": "text/plain",
            "token": self._token,
        }

        r = _request_url(
            "delete",
            f"{self._server_endpoint}/jobs/{execid}/delete",
            headers=headers,
            _logger=_logger,
        )
        if r is None:
            return

        if _logger:
            logger.info(f"Execution {execid} was deleted")

    def _get_user_access(self, userid, appid, _logger=True):
        self._require_log_in()

        res = _request_url(
            "get",
            f"{self._server_endpoint}/users/{userid}/access/{appid}",
            headers={"token": self._token},
            _logger=_logger,
        )
        if res is None:
            return

        res = json.loads(res.text)
        return res if len(res) != 0 else None

    def _get_user_access_request_file(self, userid, appid, path, _logger=True):
        res = self._get_user_access(userid, appid, _logger)
        if res is None:
            return None

        dc = DataCenter(self)
        fileloc = dc.download_dataset(int(res["access_request_dataset_id"]), path)
        return fileloc

    def _set_user_access(
        self, userid, appid, status=None, request_dataset_id=None, _logger=True
    ):
        self._require_log_in()

        if status is None and request_dataset_id is None:
            raise RuntimeError(
                "You need to pass a value for either status or request_dataset_id"
            )

        request_dict = {
            "requestdatasetid": request_dataset_id,
            "status": status if status is not None else -10,
        }
        res = _request_url(
            "post",
            f"{self._server_endpoint}/users/{userid}/access/{appid}",
            headers={"token": self._token},
            data=request_dict,
            _logger=_logger,
        )
        if res is None:
            return

        return json.loads(res.text)

    def _request_user_access(self, userid, appid, request_file, _logger=True):
        self._require_log_in()

        dc = DataCenter(self)
        dsid = dc.upload_dataset(
            request_file,
            f"access-requests/{appid}/{userid}",
            overwrite=True,
            tags="access_requests",
            _logger=_logger,
        )
        if dsid is None:
            return _throw_error(
                "Failed to request user access due to upload failure", _logger=_logger
            )

        return self._set_user_access(
            userid, appid, request_dataset_id=dsid, _logger=_logger
        )

    def _reduce_user_access(self, userid, appid, _logger=True):
        self._require_log_in()

        res = _request_url(
            "delete",
            f"{self._server_endpoint}/users/{userid}/access/{appid}",
            headers={"token": self._token},
            _logger=_logger,
        )
        if res is None:
            return

        return json.loads(res.text)

    def _get_user_app_rating(self, userid, appid, _logger=True):
        self._require_log_in()

        res = _request_url(
            "get",
            f"{self._server_endpoint}/users/{userid}/rating/{appid}",
            headers={"token": self._token},
            _logger=_logger,
        )
        if res is None:
            return

        res = json.loads(res.text)
        return res if len(res) != 0 else None

    def _set_user_app_rating(self, userid, appid, rating, comment, _logger=True):
        self._require_log_in()

        request_dict = {"rating": rating, "comment": comment}
        res = _request_url(
            "post",
            f"{self._server_endpoint}/users/{userid}/rating/{appid}",
            headers={"token": self._token},
            data=request_dict,
            _logger=_logger,
        )
        if res is None:
            return

        return json.loads(res.text)

    def _get_total_app_rating(self, appid, _logger=True):
        self._require_log_in()

        res = _request_url(
            "get",
            f"{self._server_endpoint}/apps/{appid}/rating",
            headers={"token": self._token},
            _logger=_logger,
        )
        if res is None:
            return

        res = json.loads(res.text)
        return res["avg"], res["count"]

    def _get_usage_statistics(self, _logger=True):
        self._require_log_in()

        res = _request_url(
            "get",
            f"{self._server_endpoint}/usage_statistics",
            headers={"token": self._token},
            _logger=_logger,
        )
        if res is None:
            return

        res = json.loads(res.text)
        return res
