from http import server
import os
import urllib.parse
import uuid
from typing import List, Tuple

from locust import SequentialTaskSet, TaskSet
from locust.clients import HttpSession
from requests import Response

from . import logger
from ._actions import _Actions
from ._admin import Admin
from ._app_importer import AppImporter
from ._design import Design
from ._feature_flag import FeatureFlag
from ._feature_toggle_helper import (get_client_feature_toggles,
                                     override_default_flags,
                                     set_mobile_feature_flags)
from ._interactor import _Interactor
from ._locust_error_handler import log_locust_error
from ._news import _News
from ._records import _Records
from ._reports import _Reports
from ._sites import _Sites
from ._tasks import _Tasks
from .exceptions import MissingConfigurationException

log = logger.getLogger(__name__)


# Can be called during an initalization event of a locust test to
# procedurally generate Appian credentials
def procedurally_generate_credentials(CONFIG: dict) -> None:
    """
    Helper method that can be used to procedurally generate a set of Appian user credentials

    Note: This class must be called in the UserActor class of your Locust test in order to create
    the credentials before any Locust users begin to pick them up.

    Args:
        CONFIG: full locust config dictionary, AKA the utls.c variable in locust tests Make sure the following keys are present.
        procedural_credentials_prefix: Base string for each generated username
        procedural_credentials_count: Appended to prefix, will create 1 -> Count+1 users
        procedural_credentials_password: String which will serve as the password for all users

    Returns:
        None

    """
    required_keys = [
        "procedural_credentials_prefix",
        "procedural_credentials_count",
        "procedural_credentials_password",
    ]
    missing_keys = [key for key in required_keys if key not in CONFIG]
    if missing_keys:
        raise MissingConfigurationException(missing_keys)

    if "credentials" not in CONFIG:
        CONFIG["credentials"] = []
    for i in range(CONFIG["procedural_credentials_count"]):
        creds = [
            CONFIG["procedural_credentials_prefix"] + str(int(i) + 1),
            CONFIG["procedural_credentials_password"],
        ]
        CONFIG["credentials"].append(creds)

    if not CONFIG["credentials"]:
        raise Exception("Something went wrong while attempting to procedurally generate Appian credentials. Please verify all relevant configuration.")


def setup_distributed_creds(CONFIG: dict) -> dict:
    """
    Helper method to distribute Appian credentials across separate load drivers when running Locust in distributed mode.
    Credential pairs will be passed out in Round Robin fashion to each load driver.

    Note: This class must be called in the UserActor class of your Locust test to ensure that the "credentials" key is
    prepared before tests begin.

    Note: If fewer credential pairs are provided than workers, credentials will be distributed to workers in a Modulo fashion.

    Args:
        CONFIG: full locust config dictionary, AKA the utls.c variable in locust tests Make sure the following keys are present.

    Returns:
        CONFIG: same as input but with credentials key updated to just the subset of credentials required for given load driver.

    """
    if 'credentials' not in CONFIG:
        raise MissingConfigurationException(['credentials'])

    # STY is the envrionment variable to identify which 'screen' subprocess we are running in. There will be one unique STY name
    # per load driver when running in distributed mode.
    session_name = os.getenv("STY")
    if session_name and "locustdriver" in session_name:
        # The variable will look like "12345.locustdriver-2-0"
        num_workers, worker_id = map(int, session_name.split("locustdriver-")[1].split("-"))
        credentials_subset = CONFIG['credentials'][worker_id % (len(CONFIG['credentials']))::num_workers]
        if len(credentials_subset) > 0:
            CONFIG['credentials'] = credentials_subset
    return CONFIG['credentials']


def _trim_trailing_slash(host: str) -> str:
    return host[:-1] if host and host.endswith('/') else host


class NoOpEvents():
    def fire(self, *args: str, **kwargs: int) -> None:
        pass

    def context(self, *args: str, **kwargs: int) -> dict:
        return {}


def appian_client_without_locust(host: str, record_mode: bool = False, base_path_override: str = None) -> 'AppianClient':
    """
    Returns an AppianClient that can be used without locust to make requests against a host, e.g.

    >>> appian_client_without_locust()
    >>> client.login(auth=('username', 'password'))
    >>> client.get_client_feature_toggles()

    This can be used for debugging/ making CLI style requests, instead of load testing
    Returns:
        AppianClient: an Appian client that can be used
    """
    inner_client = HttpSession(_trim_trailing_slash(host), NoOpEvents(), NoOpEvents())
    if record_mode:
        setattr(inner_client, 'record_mode', True)
    return AppianClient(inner_client, host=host, base_path_override=base_path_override)


class AppianClient:
    def __init__(self, session: HttpSession, host: str, base_path_override: str = None, portals_mode: bool = False) -> None:
        """
        Appian client class contains all the required functions to interact with Tempo.

        Note: This class will be called inside ``AppianTaskSet`` so it is not necessary to call this explicitly in a test.
        ``self.appian`` can be used directly in a test.

        Args:
            session: Locust session/client object
            host (str): Host URL

        """
        self.client = session
        self.portals_mode = portals_mode
        self.host = _trim_trailing_slash(host)
        self._interactor = _Interactor(self.client, self.host, portals_mode=portals_mode)

        self._actions = _Actions(self.interactor)
        self._admin = Admin(self.interactor)
        self._design = Design(self.interactor)
        self._news = _News(self.interactor)
        self._records = _Records(self.interactor)
        self._reports = _Reports(self.interactor)
        self._tasks = _Tasks(self.interactor)
        self._sites = _Sites(self.interactor)
        self._app_importer = AppImporter(self.interactor)

        # Adding a few session specific attributes to self.client to that it can be carried and handled by session
        # in case of having multiple sessions in the future.
        setattr(self.client, "feature_flag", "")
        setattr(self.client, "feature_flag_extended", "")

        # Used for sites where /suite is not in the URL, i.e. local builds
        setattr(self.client, "base_path_override", base_path_override)

    @property
    def interactor(self) -> _Interactor:
        """
        Interactor that can be used to make lower level requests against Appian

        See :doc:`_interactor <appian_locust._interactor>`
        """
        return self._interactor

    @property
    def actions(self) -> _Actions:
        """
        API for querying, starting and completing actions

        See :doc:`_actions <appian_locust._actions>`
        """
        return self._actions

    @property
    def admin(self) -> Admin:
        """
        API for interacting with the Admin Console

        See :doc:`_actions <appian_locust._admin>`
        """
        return self._admin

    @property
    def app_importer(self) -> AppImporter:
        """
        API for importing applications

        See :doc:`_app_importer <appian_locust._app_importer>`
        """
        return self._app_importer

    @property
    def design(self) -> Design:
        """
        API for interacting with /design

        See :doc:`_actions <appian_locust._design>`
        """
        return self._design

    @property
    def news(self) -> _News:
        """
        API for interacting with the news feed

        See :doc:`_news <appian_locust._news>`
        """
        return self._news

    @property
    def records(self) -> _Records:
        """
        API for interacting with record lists and record dashboards

        See :doc:`_records <appian_locust._records>`
        """
        return self._records

    @property
    def reports(self) -> _Reports:
        """
        API for importing applications

        See :doc:`_reports <appian_locust._reports>`
        """
        return self._reports

    @property
    def tasks(self) -> _Tasks:
        """
        API for interacting with tasks and task forms in Appian

        See :doc:`_tasks <appian_locust._tasks>`
        """
        return self._tasks

    @property
    def sites(self) -> _Sites:
        """
        API for interacting with sites in Appian

        See :doc:`_sites <appian_locust._sites>`
        """
        return self._sites

    def login(self, auth: list = None, check_login: bool = True) -> Tuple[HttpSession, Response]:
        return self.interactor.login(auth, check_login=check_login)

    def logout(self) -> None:
        """
        Logout from Appian
        """
        logout_uri = (
            self.host
            + "/suite/logout?targetUrl="
            + urllib.parse.quote(self.host + "/suite/tempo/")
        )

        headers = self.interactor.setup_request_headers(logout_uri)
        self.interactor.get_page(logout_uri, headers=headers, label="Logout.LoadUi", check_login=False)

    def get_client_feature_toggles(self) -> None:
        try:
            self.client.feature_flag, self.client.feature_flag_extended = ("7ffceebc", "1bff7f49dc1fffceebc") if self.portals_mode else (
                get_client_feature_toggles(self.interactor, self.client)
            )
        except Exception as e:
            log_locust_error(e, error_desc="Client Feature Toggles Error")
            raise e


class AppianTaskSet(TaskSet):
    def __init__(self, parent: TaskSet) -> None:
        """
        Locust performance tests with a TaskSet should set AppianTaskSet as their base class to have access to various functionality.
        This class handles creation of basic objects like ``self.appian`` and actions like ``login`` and ``logout``
        """

        super().__init__(parent)

        self.host = self.parent.host

        # A set of datatypes cached. Used to populate "X-Appian-Cached-Datatypes" header field
        self.cached_datatype: set = set()

    def on_start(self, portals_mode: bool = False) -> None:
        """
        Overloaded function of Locust's default on_start.

        It will create object self.appian and logs in to Appian

        Args:
            portals_mode (bool): set to True if connecting to portals site
        """
        self.portals_mode = portals_mode
        self.workerId = str(uuid.uuid4())
        base_path_override = self.parent.base_path_override \
            if hasattr(self.parent, "base_path_override") else ""
        self._appian = AppianClient(self.client, self.host, base_path_override=base_path_override, portals_mode=portals_mode)
        if not portals_mode:
            self.auth = self.determine_auth()
            self.appian.login(self.auth)

        self.appian.get_client_feature_toggles()

    def determine_auth(self) -> List[str]:
        """
        Determines what Appian username/password will be used on simulated logins. Auth will be determined
        using the following rules:

        If only "auth" key exists in config file, use the corresponding username and password for every login

        If only "credentials" key exists, pop one pair of credentials per Locust user until there's only one pair left.
        Then use the last pair of credentials for all remaining logins

        If both of the above keys exist, first use up all pairs in the "credentials" key, then use the pair in "auth"
        repeatedly for all remaining logings.

        In distributed mode, if only "credentials" key exists, each load driver will use last pair of credentials in the subset
        assigned to it via the setup_distributed_creds method.

        For example, if there are 3 pairs of credentials and 5 users per driver:
            Load driver 1 user 1 will take credential pair 1
            Load driver 2 users 1-5 will take credential pair 2
            Load driver 1 user 2-5 (and all after) will take credential pair 3

        Args:
            None

        Returns:
            auth: 2-entry list formatted as follows: ["username", "password"]

        """
        auth = self.parent.auth
        if hasattr(self.parent, 'credentials') and \
                isinstance(self.parent.credentials, list) and \
                self.parent.credentials:
            if len(self.parent.credentials) > 1 or (len(self.parent.credentials) == 1 and auth):
                auth = self.parent.credentials.pop(0)
            else:
                auth = self.parent.credentials[0]
        return auth

    def on_stop(self) -> None:
        """
        Overloaded function of Locust's default on_stop.

        It logs out the client from Appian.
        """
        if not self.portals_mode:
            self.appian.logout()

    @property
    def appian(self) -> AppianClient:
        """
        A wrapper around the generated AppianClient
        """
        return self._appian

    def override_default_flags(self, flags_to_override: List[FeatureFlag]) -> None:
        """
        API for overriding default feature flags.

        See :doc:`override_default_flags <appian_locust._feature_toggle_helper>`
        """
        try:
            override_default_flags(self.appian.interactor, flags_to_override)
        except Exception as e:
            log_locust_error(e, error_desc="Override Default Flags Error")
            raise e

    def declare_device_as_mobile(self) -> None:
        """
        API for designating a device as mobile to spoof running on a mobile device.

        See :doc:`declare_device_as_mobile <appian_locust._feature_toggle_helper>`
        """
        try:
            set_mobile_feature_flags(self.appian.interactor)
            self.appian.interactor.set_user_agent_to_mobile()
        except Exception as e:
            log_locust_error(e, error_desc="Override Default Flags Error")
            raise e

    def declare_device_as_desktop(self) -> None:
        """
        API for designating a device as desktop to emulate running on a computer device.
        This is done by default, so only use this method when running a mix of mobile and
        desktop tests.

        See :doc:`declare_device_as_mobile <appian_locust._feature_toggle_helper>`
        """
        try:
            self.appian.interactor.set_user_agent_to_desktop()
        except Exception as e:
            log_locust_error(e, error_desc="Error setting device as desktop")
            raise e


class AppianTaskSequence(SequentialTaskSet, AppianTaskSet):
    def __init__(self, parent: SequentialTaskSet) -> None:
        super(AppianTaskSequence, self).__init__(parent)
