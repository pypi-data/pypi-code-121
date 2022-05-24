from __future__ import annotations

import asyncio
import contextlib
import functools
import itertools
import json
import logging
import os
import random
import re
import ssl
import string
import subprocess
import sys
import tempfile
import threading
import time
import warnings
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from logging.config import dictConfig
from math import ceil
from typing import Dict, List, NoReturn, Optional, Tuple, Union
from urllib.parse import urlencode

import backoff
import dask

if sys.version_info >= (3, 8):
    from typing import TypedDict, get_args, get_origin, get_type_hints
else:
    from typing_extensions import TypedDict, get_args, get_origin, get_type_hints

import aiohttp
import boto3
import click
import dask
import rich
import yaml
from coiled.exceptions import (
    AccountFormatError,
    ApiResponseStatusError,
    CidrInvalidError,
    GPUTypeError,
    InstanceTypeError,
    ParseIdentifierError,
    PortValidationError,
    UnsupportedBackendError,
)
from dask.distributed import Security
from rich.console import Console

from .compatibility import COILED_VERSION, PY_VERSION
from .errors import ServerError

logger = logging.getLogger(__name__)


ACCOUNT_REGEX = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
ALLOWED_PROVIDERS = ["aws", "vm_aws", "gcp", "vm_gcp"]

COILED_LOGGER_NAME = "coiled"
COILED_SERVER = "https://cloud.coiled.io"

AWS_INSTANCES_FAMILY_FILTER = ["t2", "t3", "m5", "c2", "c5"]


class VmType(TypedDict):
    """
    Example:
        {
        'name': 't2d-standard-8',
        'cores': 8,
        'gpus': 0,
        'gpu_name': None,
        'memory': 32768,
        'backend_type': 'vm_gcp'
        }
    """

    name: str
    cores: int
    gpus: int
    gpu_name: str
    memory: int
    backend_type: str


# TODO: copied from distributed, introduced in 2021.12.0.
# We should be able to remove this someday once we can increase
# the minimum supported version.
def in_async_call(loop, default=False):
    """Whether this call is currently within an async call"""
    try:
        return loop.asyncio_loop is asyncio.get_running_loop()
    except RuntimeError:
        # No *running* loop in thread. If the event loop isn't running, it
        # _could_ be started later in this thread though. Return the default.
        if not loop.asyncio_loop.is_running():
            return default
        return False


def validate_account(account: str):
    if ACCOUNT_REGEX.match(account) is None:
        raise AccountFormatError(
            f"Bad account format. Account '{account}' should be a combination "
            "of lowercase letters, numbers and hyhens."
        )


def random_str(length: int = 8):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


class GatewaySecurity(Security):
    """A security implementation that temporarily stores credentials on disk.

    The normal ``Security`` class assumes credentials already exist on disk,
    but our credentials exist only in memory. Since Python's SSLContext doesn't
    support directly loading credentials from memory, we write them temporarily
    to disk when creating the context, then delete them immediately."""

    def __init__(self, tls_key, tls_cert, extra_conn_args: Optional[dict] = None):
        self.tls_key = tls_key
        self.tls_cert = tls_cert
        self.extra_conn_args = extra_conn_args or {}

    def __repr__(self):
        return "GatewaySecurity<...>"

    def get_connection_args(self, role):
        ctx = None
        if self.tls_key and self.tls_cert:
            with tempfile.TemporaryDirectory() as tempdir:
                key_path = os.path.join(tempdir, "dask.pem")
                cert_path = os.path.join(tempdir, "dask.crt")
                with open(key_path, "w") as f:
                    f.write(self.tls_key)
                with open(cert_path, "w") as f:
                    f.write(self.tls_cert)
                ctx = ssl.create_default_context(
                    purpose=ssl.Purpose.SERVER_AUTH, cafile=cert_path
                )
                ctx.verify_mode = ssl.CERT_REQUIRED
                ctx.check_hostname = False
                ctx.load_cert_chain(cert_path, key_path)
        return {
            "ssl_context": ctx,
            "require_encryption": True,
            "extra_conn_args": self.extra_conn_args,
        }


async def handle_api_exception(response, exception_cls=ServerError) -> NoReturn:
    with contextlib.suppress(
        aiohttp.ContentTypeError, json.JSONDecodeError, AttributeError
    ):
        # First see if it's an error we created that has a more useful
        # message
        error_body = await response.json()
        if isinstance(error_body, dict):
            errs = error_body.get("non_field_errors")
            if "message" in error_body:
                raise exception_cls(error_body["message"])
            elif errs and isinstance(errs, list) and len(errs):
                raise exception_cls(errs[0])
            else:
                raise exception_cls(
                    "Server error, ".join(f"{k}={v}" for (k, v) in error_body.items())
                )
        else:
            raise exception_cls(error_body)

    error_text = await response.text()

    if not error_text:
        # Response contains no text/body, let's not raise an empty exception
        error_text = f"{response.status} - {response.reason}"
    raise exception_cls(error_text)


def normalize_server(server: Optional[str]) -> str:
    if not server:
        server = COILED_SERVER
    # Check if using an older server
    if "beta.coiledhq.com" in server or "beta.coiled.io" in server:
        # NOTE: https is needed here as http is not redirecting
        server = COILED_SERVER

    # remove any trailing slashes
    server = server.rstrip("/")

    return server


def get_account_membership(
    response: dict, account: Optional["str"] = None
) -> Optional[dict]:
    if account is None:
        account = response.get("username")
        account = account.lower() if account else None

    membership_set = response.get("membership_set", [])

    for membership in membership_set:
        account_details = membership.get("account", {})
        has_membership = account_details.get("slug") == account
        if has_membership:
            return membership

    else:
        return None


def get_auth_header_value(token: str) -> str:
    """..."""
    # TODO: delete the branching after client only supports ApiToken.
    if "-" in token:
        return "ApiToken " + token
    else:
        return "Token " + token


def has_program_quota(membership: dict) -> bool:
    account_details = membership.get("account", {})
    return account_details.get("active_program", {}).get("has_quota") is True


# We only use ApiResponseStatusError on status 502, 503, 504
@backoff.on_exception(backoff.expo, ApiResponseStatusError, logger=logger)
async def handle_credentials(
    *,
    server: Optional[str] = None,
    token: Optional[str] = None,
    account: Optional[str] = None,
    save: Optional[bool] = None,
    retry: bool = True,
) -> Tuple[str, str, str]:
    """Validate and optionally save credentials

    Parameters
    ----------
    server
        Server to connect to. If not specified, will check the
        ``coiled.server`` configuration value.
    token
        Coiled user token to use. If not specified, will prompt user
        to input token.
    account
        Name of Coiled account to use. If not provided, will
        default to the user account.
    save
        Whether or not save credentials to coiled config file.
        If ``None``, will ask for input on whether or not credentials
        should be saved. Defaults to None.
    retry
        Whether or not to try again if invalid credentials are entered.
        Retrying is often desired in interactive situations, but not
        in more programmatic scenerios. Defaults to True.

    Returns
    -------
    user
        Username
    token
        User API token
    server
        Server being used
    """
    if account:
        validate_account(account)
    # If testing locally with `ngrok` we need to
    # rewrite the server to localhost
    server = server or dask.config.get("coiled.server", COILED_SERVER)
    server = normalize_server(server)
    login_url = f"{server}/profile"
    if token is None:
        rich.print(f"Please login to [link]{login_url}[/link] to get your token")
        # Using click instead of getpass to make testing easier
        token = click.prompt("Token", hide_input=True)
        if not token:
            raise ValueError(
                "Token not provided, unable to login. You can create new tokens and "
                f"managing your existing ones at {server}/profile.\n"
            )

    # TODO: revert when we remove versioneer
    if dask.config.get("coiled.no-minimum-version-check", False):
        client_version = "coiled-frontend-js"
    else:
        client_version = COILED_VERSION

    # Validate token and get username
    async with aiohttp.ClientSession(
        headers={
            "Authorization": get_auth_header_value(token),
            "Client-Version": client_version,
        }
    ) as session:
        response = await session.request("GET", f"{server}/api/v1/users/me/")

        try:
            data = await response.json()
        except (aiohttp.ContentTypeError, json.JSONDecodeError):
            # The code bellow will handle status codes that are errors,
            # we are setting data to an empty dict to make typing happy
            data = {}

        if response.status == 426:
            # Upgrade required
            await handle_api_exception(response)
        elif response.status in [502, 503, 504]:
            raise ApiResponseStatusError(
                f"Unable to receive data from the server. Received {response.status} - Temporary Error."
            )
        elif response.status >= 400:
            if (
                isinstance(data, dict)
                and retry
                and "Invalid token" in data.get("detail", "")
            ):
                # Token is not valid, ask for a new one
                rich.print(
                    "[red]Invalid Coiled token encountered. You can create new tokens and manage "
                    f"your existing ones at {server}/profile.\n"
                )
                return await handle_credentials(server=server, token=None, save=None)
            else:
                await handle_api_exception(response)

        account_membership = get_account_membership(data, account=account)
        # only validate if account arg is provided by user
        if account and not account_membership:
            rich.print(
                "[red]You are not a member of this account. Perhaps try another one?\n"
            )
            account = click.prompt("Account")
            if account:
                validate_account(account)
            else:
                rich.print("[red]No account provided, unable to login.")

            return await handle_credentials(
                server=server, token=token, save=None, account=account
            )

    # We should always have username from above, but let's be defensive about it just in case.
    user = data.get("username")
    if not user:
        raise ValueError(
            "Unable to get your account username after login. Please try to login again, if "
            "the error persists, please reach out to Coiled Support at support@coiled.io"
        )

    # Avoid extra printing when creating clusters
    if save is not False:
        rich.print("[green]Authentication successful")
        if not account_membership or not has_program_quota(account_membership):
            rich.print(
                "[red]You have reached your quota of Coiled credits for this account."
            )
    if save is None:
        # Optionally save user credentials for next time
        save_creds = input("Save credentials for next time? [Y/n]: ")
        if save_creds.lower() in ("y", "yes", ""):
            save = True
    if save:
        default_file = os.path.join(os.path.dirname(__file__), "coiled.yaml")
        config_file = os.path.join(
            os.path.expanduser("~"), ".config", "dask", "coiled.yaml"
        )
        # Make sure directory with config exists
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        configs = dask.config.collect_yaml([default_file, config_file])
        creds = {
            "coiled": {
                "user": user,
                "token": token,
                "server": server,
                "account": account_membership.get("account", {}).get("slug")
                if account_membership
                else None,
            }
        }
        config = dask.config.merge(*configs, creds)
        with open(config_file, "w") as f:
            f.write(yaml.dump(config))
        rich.print(f"Credentials have been saved at [blue]{config_file}")
        # Make sure saved configuration values are set for the current Python process
        dask.config.set(config)

    return user, token, server


class Spinner:
    """A spinner context manager to denotate we are still working"""

    def __init__(self, delay=0.2):
        self.spinner = itertools.cycle(["-", "/", "|", "\\"])
        self.delay = delay
        self.busy = False

    def write_next(self):
        with self._screen_lock:
            sys.stdout.write(next(self.spinner))
            sys.stdout.flush()

    def remove_spinner(self, cleanup=False):
        with self._screen_lock:
            sys.stdout.write("\b")
            if cleanup:
                sys.stdout.write(" ")  # overwrite spinner with blank
                sys.stdout.write("\r")  # move to next line
            sys.stdout.flush()

    def spinner_task(self):
        while self.busy:
            self.write_next()
            time.sleep(self.delay)
            self.remove_spinner()

    def __enter__(self):
        if sys.stdout.isatty():
            self._screen_lock = threading.Lock()
            self.busy = True
            self.thread = threading.Thread(target=self.spinner_task)
            self.thread.start()

    def __exit__(self, exception, value, tb):
        if sys.stdout.isatty():
            self.busy = False
            self.remove_spinner(cleanup=True)
        else:
            sys.stdout.write("\r")


def parse_identifier(
    identifier: str,
    property_name: str = "name",
    can_have_revision: bool = False,
    allow_uppercase: bool = False,
) -> Tuple[Optional[str], str, Optional[str]]:
    """
    Parameters
    ----------
    identifier:
        identifier of the resource, i.e. "coiled/xgboost" "coiled/xgboost:1ef489", "xgboost:1ef489" or "xgboost"
    can_have_revision:
        Indicates if this identifier supports having a ":<string>" postfix, as in
        the ":1ef489" in "xgboost:1ef489". At time of writing, this only has an effect
        on software environments. For other resources this has no meaning. At time
        of writing, this only affects the error message that will be printed out.
    property_name:
        The name of the parameter that was being validated; will be printed
        with any error messages, i.e. Unsupported value for "software_environment".

    Examples
    --------
    >>> parse_identifier("coiled/xgboost", "software_environment")
    ("coiled", "xgboost", None)
    >>> parse_identifier("xgboost", "software_environment", False)
    (None, "xgboost", None)
    >>> parse_identifier("coiled/xgboost:1ef4543", "software_environment", True)
    ("coiled", "xgboost", "1ef4543")

    Raises
    ------
    ParseIdentifierError
    """
    if allow_uppercase:
        rule = re.compile(r"^([a-zA-Z0-9-_]+?/)?([a-zA-Z0-9-_]+?)(:[a-zA-Z0-9-_]+)?$")
        rule_text = ""
    else:
        rule = re.compile(r"^([a-z0-9-_]+?/)?([a-z0-9-_]+?)(:[a-zA-Z0-9-_]+)?$")
        rule_text = "lowercase "

    match = re.fullmatch(rule, identifier)
    if match:
        account, name, revision = match.groups()
        account = account.replace("/", "") if account else account
        revision = revision.replace(":", "") if revision else revision
        return account, name, revision

    if can_have_revision:
        message = (
            f"Invalid {property_name}: should have format (<account>/)<name>(:<revision>),"
            ' for example "coiled/xgboost:1efd456", "xgboost:1efd456" or "xgboost". '
            f"It can only contain {rule_text}ASCII letters, numbers, hyphens and underscores. "
            "The <name> is required (xgboost in the previous example). The <account> prefix"
            f" can be used to specify a {property_name} from a different account, and the"
            f" :<revision> can be used to select a specific revision of the {property_name}."
        )
    else:
        message = (
            f"Invalid {property_name}: should have format (<account>/)<name>,"
            f' for example "coiled/xgboost" or "python-37". and can only contain {rule_text}ASCII letters,'
            ' numbers, hyphens and underscores. The <name> is required ("xgboost" and "python-37"'
            " in the previous examples)."
            f' The <account> prefix (i.e. "coiled/") can be used to specify a {property_name}'
            " from a different account."
        )
    raise ParseIdentifierError(message)


def get_platform():
    # Determine platform
    if sys.platform == "linux":
        platform = "linux"
    elif sys.platform == "darwin":
        platform = "osx"
    elif sys.platform == "win32":
        platform = "windows"
    else:
        raise ValueError(f"Invalid platform {sys.platform} encountered")
    return platform


class ExperimentalFeatureWarning(RuntimeWarning):
    """Warning raise by an experimental feature"""

    pass


class DeprecatedFeatureWarning(RuntimeWarning):
    pass


def experimental(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        warnings.warn(
            f"{func.__name__} is an experimental feature which is subject "
            "to breaking changes, being removed, or otherwise updated without notice "
            "and should be used accordingly.",
            ExperimentalFeatureWarning,
        )
        return func(*args, **kwargs)

    return inner


async def run_command_in_subprocess(cmd: str, suppress_error: bool = False):
    """Run the command in subprocess.

    If a user is using a python version < 3.8 then he will get a RuntimeError exception -
    ``Cannot add child handler, the child watcher does not have a loop attached``. As a
    workaround for the issue, we check if the user is running any earlier version of python
    and run the command in subprocess instead.

    For reference on the RuntimeError exception: https://bugs.python.org/issue35621

    """
    platform = get_platform()

    if PY_VERSION < "3.8" or platform == "windows":
        proc = subprocess.Popen(
            cmd.split(" "),
            bufsize=1,
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert proc.stdout
        for line in proc.stdout:
            yield line.rstrip()

    else:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        lines = []
        while proc.stdout and proc.stderr and proc.returncode is None:
            await asyncio.sleep(0.5)
            async for line in proc.stdout:
                line = line.decode().rstrip()
                lines.append(line)
                yield line

            async for line in proc.stderr:
                line = line.decode().rstrip()
                lines.append(line)
                yield line

        if proc.returncode and not suppress_error:
            raise ValueError("\n".join(lines))


def name_exists_in_dict(
    user: Union[str, None], name: Union[str, None], dictionary: Union[dict, None]
) -> bool:
    """Check if name exists in dictionary.

    Since we are returning ``<account>/<name>`` when listing software envs
    and cluster configs, this method will try to handle the case where sometimes
    we are passing a name with the format ``<account>/<name>`` and sometimes with
    ``<name``.

    If we can't find ``<account>/<name>`` in the dictionary, we will check if we
    can find the ``name`` substring in the dictionary keys.

    """
    if dictionary:
        if f"{user}/{name}" in dictionary or name in dictionary:
            return True
        if any([soft_env for soft_env in dictionary if name in soft_env]):
            return True
    return False


def rich_console():
    is_spyder = False

    with contextlib.suppress(AttributeError, ImportError):
        from IPython import get_ipython

        ipython = get_ipython().config
        if ipython.get("SpyderKernelApp"):
            is_spyder = True

    if is_spyder:
        print("Creating Cluster. This might take a few minutes...")
        return Console(force_jupyter=False)
    return Console()


def verify_aws_credentials(aws_access_key_id: str, aws_secret_access_key: str):
    "Verifies AWS Credentials are valid"
    sts = boto3.client(
        "sts",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    sts.get_caller_identity()


def scheduler_ports(protocol: Union[str, List[str]]):
    """Generate scheduler ports based on protocol(s)"""
    exclude = 8787  # dashboard port
    start = 8786
    if isinstance(protocol, str):
        return start

    port = start
    ports = []
    for _ in protocol:
        if port == exclude:
            port += 1
        ports.append(port)
        port += 1
    return ports


def parse_gcp_region_zone(region: Optional[str] = None, zone: Optional[str] = None):
    """Parse GCP zone and region or return default region/zone.

    This is an helper function to make it easier for us
    to parse gcp zones. Since users can specify regions,
    zones or one of the two, we should create some sane
    way to deal with the different combinations.

    """
    if not region and not zone:
        region = "us-east1"
        zone = "us-east1-c"
    elif region and not zone:
        # Most regions have region C and in us-east1 this region
        # has the best quotas
        zone = f"{region}-c"
    elif region and zone and len(zone) == 1:
        zone = f"{region}-{zone}"
    elif not region and zone and len(zone) == 1:
        region = "us-east1"
        zone = f"{region}-{zone}"
    elif zone and not region:
        region = zone[:-2]

    return region, zone


class UTCFormatter(logging.Formatter):
    converter = time.gmtime


def enable_debug_mode():
    from .context import COILED_SESSION_ID

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "utc": {
                "()": UTCFormatter,
                "format": "[UTC][%(asctime)s][%(levelname)-8s][%(name)s] %(message)s",
            },
        },
        "handlers": {
            "utc-console": {
                "class": "logging.StreamHandler",
                "formatter": "utc",
            },
        },
        "loggers": {
            "coiled": {
                "handlers": ["utc-console"],
                "level": logging.DEBUG,
            },
        },
    }
    dictConfig(LOGGING)
    logger.debug(f"Coiled Version : {COILED_VERSION}")
    start = datetime.now(tz=timezone.utc)
    trace_link = get_datadog_trace_link(
        start=start, **{"coiled-session-id": COILED_SESSION_ID}
    )
    logger.info(f"DD Trace: {trace_link}")
    trace_link = get_datadog_logs_link(
        start=datetime.now(tz=timezone.utc), **{"coiled-session-id": COILED_SESSION_ID}
    )
    logger.info(f"DD Logs: {trace_link}")


def get_datadog_trace_link(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    **filters: Dict[str, str],
):
    params = {
        "query": " ".join([f"@{k}:{v}" for k, v in filters.items()]),
        "paused": "true",
        "streamTraces": "false",
        "showAllSpans": "true",
    }
    if start:
        fuzzed = start - timedelta(minutes=1)
        params["start"] = str(int(fuzzed.timestamp() * 1000))
    if end:
        fuzzed = end + timedelta(minutes=1)
        params["end"] = str(int(fuzzed.timestamp() * 1000))
    return f"https://app.datadoghq.com/apm/traces?{urlencode(params)}"


def get_datadog_logs_link(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    **filters: Dict[str, str],
):
    params = {
        "query": " ".join([f"@{k}:{v}" for k, v in filters.items()]),
        "live": "false",
    }
    if start:
        fuzzed = start - timedelta(minutes=1)
        params["from_ts"] = str(int(fuzzed.timestamp() * 1000))
    if end:
        fuzzed = end + timedelta(minutes=1)
        params["to_ts"] = str(int(fuzzed.timestamp() * 1000))
    return f"https://app.datadoghq.com/logs?{urlencode(params)}"


def validate_gpu_type(gpu_type: str):
    """Validate gpu type provided by the user.

    Currently, we are just accepting the nvidia-tesla-t4 gpu type
    but in the next iteration we will accept more types. We are also
    filtering out virtual workstation gpus upstream, so we need this
    function to remove types that we know it will fail.

    """

    if gpu_type != "nvidia-tesla-t4":
        error_msg = (
            f"GPU type '{gpu_type}' is not a supported GPU type. Allowed "
            "GPU types are: 'nvidia-tesla-t4'."
        )
        raise GPUTypeError(error_msg)
    return True


def is_gcp(account: str, accounts: dict) -> bool:
    """Determine if an account backend is Google Cloud Provider.

    Parameters
    ----------
    account: str
        Slug of Coiled account to use.
    accounts: dict
        Dictionary of available accounts from the /api/v1/users/me endpoint.

    Returns
    -------
    gcp_backend: bool
        True if a GCP backend, else False.
    """
    user_account = accounts.get(account, {})
    user_options = user_account.get("options", {})
    gcp_backend = (
        user_account.get("backend") == "vm_gcp"
        or user_options.get("provider_name") == "gcp"
    )
    return gcp_backend


def is_customer_hosted(account: str, accounts: dict) -> bool:
    """Determine if an account backend is customer-hosted.

    Parameters
    ----------
    account: str
        Slug of Coiled account to use.
    accounts: dict
        Dictionary of available accounts from the /api/v1/users/me endpoint.

    Returns
    -------
    customer_hosted: bool
        True if a customer-hosted backend, else False.
    """
    user_account = accounts.get(account, {})
    backend_type = user_account.get("backend")
    customer_hosted = backend_type == "vm"
    return customer_hosted


def validate_cidr_block(cidr_block: str):
    """Validate cidr block added by the user.

    Here we are only checking if the cidr block is in the
    format <int>.<int>.<int>.<int>/<int>.

    """
    if not isinstance(cidr_block, str):
        raise CidrInvalidError(
            f"CIDR needs to be of type string, but received '{type(cidr_block)}' "
            "please specify your CIDR block as a string."
        )
    match = re.fullmatch(r"(\d{1,3}\.){3}\d{1,3}\/\d{1,3}", cidr_block)
    if not match:
        raise CidrInvalidError(
            f"The CIDR block provided '{cidr_block}' doesn't appear "
            "to have the correct IPV4 pattern, your CIDR block should "
            "follow the '0.0.0.0/0' pattern."
        )
    return True


def validate_ports(ports):
    """Validate the ports tha the user tries to pass.

    We need to make sure that the user passes a list of ints only,
    otherwise we should raise an exception.

    """
    if not isinstance(ports, list):
        raise PortValidationError(
            f"Ports need to be of type list, but received '{type(ports)}' "
            "please adds your ports in a list."
        )

    for port in ports:
        if not isinstance(port, int):
            raise PortValidationError(
                f"Ports need to be of type int, but received '{type(port)}' "
                "please use a int value for your port number."
            )
    return True


def validate_network(backend_options: dict, is_customer_hosted: bool):
    """Validate network configuration from backend options.

    Users can specify network and/or subnet(s) to use. We need to validate these and
    ensure that they're only used with customer hosted backend.
    """
    if not is_customer_hosted:
        raise UnsupportedBackendError(
            "Network configuration isn't available in a Coiled "
            "hosted backend. Please change your backend to configure network."
        )

    network_options = backend_options.get("network", {})

    # check that resource ids, if specified, are strings
    resource_ids = (
        network_options.get("network_id"),
        network_options.get("scheduler_subnet_id"),
        network_options.get("worker_subnet_id"),
        network_options.get("firewall_id"),
    )

    for resource_id in resource_ids:
        if resource_id and not isinstance(resource_id, str):
            raise TypeError(f"Network id '{id}' for '{resource_id}' must be a string.")


def parse_backend_options(
    backend_options: dict,
    account: str,
    accounts: dict,
    worker_gpu: Optional[int],
) -> dict:
    """Parse backend options before launching cluster.

    The following are checked and parsed before launching a cluster:
        - If launching into a GCP cluster, `preemptible` is aliased with `spot`.
        - If requesting worker GPUs, `spot` defaults to `False` unless specified.
        - If set, `zone` overrides `gcp_zone` (for GCP).

    Parameters
    ----------
    backend_options: dict
        Dictionary of backend specific options (e.g. ``{'region': 'us-east-2'}``).
    account: str
        Slug of Coiled account to use.
    accounts: dict
        Dictionary of available accounts from the /api/v1/users/me endpoint.
    worker_gpu: int
        Number of GPUs allocated for each worker.

    Returns
    -------
    backend_options: dict
        A dictionary of parsed backend options.
    """
    backend_options = deepcopy(backend_options)
    gcp_backend = is_gcp(account, accounts)
    customer_hosted = is_customer_hosted(account, accounts)
    # alias preemptible/spot
    if backend_options.get("preemptible") is not None and gcp_backend:
        backend_options["spot"] = backend_options.pop("preemptible")
    # default to on-demand for gpu workers
    if backend_options.get("spot") is None and bool(worker_gpu):
        backend_options["spot"] = False

    # zone (if set) overrides gcp_zone for gcp
    if backend_options.get("zone") and backend_options.get("gcp_project_name"):
        backend_options["gcp_zone"] = backend_options.get("zone")

    if backend_options.get("network"):
        validate_network(backend_options, customer_hosted)
    if backend_options.get("firewall"):
        cidr = backend_options["firewall"].get("cidr")
        ports = backend_options["firewall"].get("ports")
        if ports:
            validate_ports(ports)
        if cidr:
            validate_cidr_block(cidr)
    return backend_options


async def get_worker_creation_notification_error(
    cloud, account: Optional[str]
) -> Optional[str]:
    """Call get_notifications and return error messages from worker creation.

    When we try to create workers, we use the ``create_worker`` event type to
    the notification, we can quickly use this event type and the logging level
    ``ERROR`` to only get notifications that are related to worker creation.

    Note that we don't use the cluster name in the backend, but the cluster id
    so we can't really filter the notifications by name, with that in mind, we
    make the assumption that the last notification that we receive will be the
    one from the cluster that just ran. This is ugly but should work okay for
    now.

    """
    notifications = await cloud.get_notifications(
        account=account, json=True, event_type="create_worker", level="ERROR"
    )

    if notifications:
        last_notification = notifications[-1]
        error_message = last_notification.get("data", {}).get("error")

        # If there is no reason, lets avoiding showing "giving up" messages
        # with no useful message
        if error_message and "Reason" in error_message:
            return error_message
        return last_notification["msg"]


def parse_wait_for_workers(
    n_workers: int, wait_for_workers: Optional[bool | int | float] = None
) -> int:
    """Parse the option to wait for workers."""
    wait_for_workers = (
        # Set 30% as default value to wait for workers
        dask.config.get("coiled.wait-for-workers", 0.3)
        if wait_for_workers is None
        else wait_for_workers
    )

    if wait_for_workers is True:
        to_wait = n_workers
    elif wait_for_workers is False:
        to_wait = 0
    elif isinstance(wait_for_workers, int):
        if wait_for_workers >= 0 and wait_for_workers <= n_workers:
            to_wait = wait_for_workers
        else:
            raise ValueError(
                f"Received invalid value '{wait_for_workers}' as wait_for_workers, "
                f"this value needs to be between 0 and {n_workers}"
            )
    elif isinstance(wait_for_workers, float):
        if wait_for_workers >= 0 and wait_for_workers <= 1.0:
            to_wait = ceil(wait_for_workers * n_workers)
        else:
            raise ValueError(
                f"Received invalid value '{wait_for_workers}' as wait_for_workers, "
                "this value needs to be a value between 0 and 1.0."
            )
    else:
        raise ValueError(
            f"Received invalid value '{wait_for_workers}' as wait_for_workers, "
            "this value needs to be either a Boolean, an Integer or a Float."
        )

    return to_wait


def bytes_to_mb(bytes: float) -> int:
    """Convert bytes to Mb.

    Our backend expects the memory to be passed as Mb, so we need to convert
    bytes obtained by dask to Mb.

    """
    return round(abs(bytes) * 10**-6)


def parse_requested_memory(
    memory: Optional[Union[int, str, float, list[str], list[int], list[float]]],
    min_memory: Optional[Union[str, int, float]],
) -> dict:
    """Handle memory requested by user.

    Users calling `list_instance_types` can use different ways to specify memory,
    this function will handle the different cases and return a dictionary with the
    expected result.

    Note: We are also giving a +- 10% buffer on the requested memory.

    """
    parsed_memory = {}

    if isinstance(memory, list):
        if len(memory) > 2:
            raise ValueError(
                f"Memory should contain only two values in the format `[minimum, maximum]`, but received {memory}."
            )
        parsed_memory["memory__gte"] = bytes_to_mb(
            dask.utils.parse_bytes(memory[0]) * 0.89
        )
        parsed_memory["memory__lte"] = bytes_to_mb(
            dask.utils.parse_bytes(memory[1]) * 1.1
        )
    elif (
        isinstance(memory, int) or isinstance(memory, float) or isinstance(memory, str)
    ):
        parsed_memory["memory__gte"] = bytes_to_mb(
            dask.utils.parse_bytes(memory) * 0.89
        )
        parsed_memory["memory__lte"] = bytes_to_mb(dask.utils.parse_bytes(memory) * 1.1)

    if min_memory and not memory:
        parsed_memory["memory__gte"] = bytes_to_mb(dask.utils.parse_bytes(min_memory))

    return parsed_memory


def get_instance_type_from_cpu_memory(
    cpu: Optional[Union[int, List[int]]] = None,
    memory: Optional[Union[str, List[str]]] = None,
    backend: Optional[str] = None,
) -> List[str]:
    """Get instances by cpu/memory combination.

    We are using the `list_instance_types` method to get the
    instances that match the cpu/memory specification. If no
    instance can be found we will raise an exeception
    informing the user about this.

    """
    # Circular imports
    from .core import list_instance_types

    vm_types = list_instance_types(cores=cpu, memory=memory, backend=backend)

    instances = [instance_name for instance_name in vm_types]
    backend = vm_types.get(instances[0], {}).get("backend_type") if instances else None

    if backend == "vm_gcp":
        instances = [
            instance_name
            for instance_name in instances
            if instance_name.startswith("e2")
        ]
    else:
        instances = [
            instance_name
            for instance_name in instances
            if instance_name[:2] in AWS_INSTANCES_FAMILY_FILTER
        ]

    if not instances:
        error_message = (
            "Unable to find instance types that match the specification: \n"
            f"\t Cores: {cpu}  Memory: {memory} \n"
        )

        if cpu:
            error_message += "You can try selecting a range for the cpu or memory, for example: `cpu=[2, 8]` \n"
        if memory and cpu:
            memory_matching_instances = [
                instance_name for instance_name in list_instance_types(memory=memory)
            ]

            if memory_matching_instances:
                error_message += (
                    "You might want to pick these instances that match your "
                    "memory requirements, but have different core count. \n"
                    f"{memory_matching_instances} \n"
                    "You can use the `scheduler_vm_types=[]` or `worker_vm_types=[]` keyword "
                    "argument to specify instance types."
                )
        raise InstanceTypeError(error_message)
    return instances


def show_cluster_configuration_deprecation_warning():
    with warnings.catch_warnings():
        warnings.warn(
            "Cluster Configurations are deprecated and will be removed",
            DeprecationWarning,
        )


def validate_type(type_, obj_) -> bool:
    if hasattr(type_, "__forward_arg__"):
        # evaluate ForwardRef types -- this function breaks if we can't
        return validate_type(type_.__forward_arg__, obj_)
    try:
        if hasattr(type_, "__annotations__"):
            # check for type TypedDict

            # check that object is a dict
            if not isinstance(obj_, dict):
                return False

            # check all the keys
            for k, v in get_type_hints(type_).items():
                # get so that undefined key will be None, and check will
                # pass only if type is Optional
                if not validate_type(v, obj_.get(k)):
                    return False

            # make sure no extra keys
            obj_keys = set(obj_.keys())
            type_keys = set(get_type_hints(type_).keys())
            if len(obj_keys - type_keys):
                return False

            return True

        elif hasattr(type_, "__origin__"):
            if get_origin(type_) == Union:
                # check for type Union (including Optional)
                union_types = get_args(type_)
                return any((validate_type(subtype, obj_) for subtype in union_types))
            elif get_origin(type_) == list:
                # for list, check that each item has correct type
                subtype = get_args(type_)[0]
                return all((validate_type(subtype, list_item) for list_item in obj_))

        # check for other types (can check directly)
        return isinstance(obj_, type_)

    except Exception:
        # assume that this function works for the types we're checking
        return False


def validate_vm_typing(vm_types: Optional[List[str]]):
    """Validate instance typing.

    We need to add this function because the error that our API is returning
    isn't exactly user friendly. We should raise a type error with an informative
    message instead of the dictionary that the API throws.

    """
    if not vm_types:
        return
    if not isinstance(vm_types, list):
        raise TypeError(
            f"Instance types must be a list, but the value '{vm_types}' is of "
            f"type: {type(vm_types)}. Please use a list of strings when specifying "
            "instance types."
        )
    for instance in vm_types:
        if not isinstance(instance, str):
            raise TypeError(
                f" Instance types must be a string, but '{instance}' is of type "
                f"{type(instance)}. Please use a string instead."
            )
