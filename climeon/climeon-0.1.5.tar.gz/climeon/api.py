"""Climeon API wrapper, used to access the Climeon API from Python.

Authentication credentials will be fetched from environment variables
``API_USER`` and ``API_PASS`` or programatically at client instantiation or
else through user interaction via Climeon Live Azure B2C.
"""

# Standard modules
from datetime import timedelta, timezone
from hashlib import sha1
from io import StringIO
import json
from logging import getLogger
from os import getenv, path, listdir, remove, makedirs
from tempfile import gettempdir

# External modules
import msal
import pandas as pd
import requests

# Climeon modules
from .identifiers import powerblock, module, hp_system

# API details
PROD_URL = "https://api.climeonlive.com/api/v1"
DEV_URL = "https://climeonliveapi-staging.azurewebsites.net/api/v1"

# MSAL settings
CLIENT_ID = "fe8152ab-d22c-4f61-9a24-17bb397bee75"
AUTHORITY = "https://climeonlive.b2clogin.com/climeonlive.onmicrosoft.com/"
POLICY_ROPC = "B2C_1_ropc"
POLICY_SIGN_IN = "B2C_1_standard_signin"
AUTHORITY_SIGN_IN = AUTHORITY + POLICY_SIGN_IN
AUTHORITY_ROPC = AUTHORITY + POLICY_ROPC
MSAL_SCOPE = ["https://climeonlive.onmicrosoft.com/backend/read"]

# Offline cache settings
BASE_FOLDER = getenv("APPDATA", gettempdir())
OFFLINE_FOLDER = path.join(BASE_FOLDER, "ClimeonLive")
OFFLINE_NAME = "%s_%s_%s_%s_%s"
FOLDER_SIZE_LIMIT = 2*1024*1024*1024
PARQUET_WARN = False

# Analytics max interval default settings
MAX_RESULTS = 10000
MAX_INTERVALS = {
    MAX_RESULTS: "PT1S",
    MAX_RESULTS * 10: "PT10S",
    MAX_RESULTS * 60: "PT1M",
    MAX_RESULTS * 600: "PT10M",
    MAX_RESULTS * 3600: "PT1H",
    MAX_RESULTS * 43200: "PT12H",
    MAX_RESULTS * 86400: "PT24H",
}
VALID_INTERVALS = list(MAX_INTERVALS.values())

class Client():
    """Climeon API client.

        Parameters:
            user (str): User mail to login with. If not supplied it will
                        be fetched from environment variable ``API_USER``, if
                        not set the user will be promted via Azure B2C.
            passwd (str): User password. If not supplied it will be
                          fetched from environment variable ``API_PASS``,
                          if not set the user will be promted via Azure B2C.
            prod (bool): Boolean indicating if the production or development
                         API should be used. Defaults to ``True``.
    """
    # pylint: disable=too-many-public-methods

    def __init__(self, user=None, passwd=None, prod=True):
        self.logger = getLogger(__name__)
        self.user = user or getenv("API_USER")
        self.passwd = passwd or getenv("API_PASS")
        self.url = PROD_URL if prod else DEV_URL
        self.headers = {"authorization": ""}
        ropc = self.user and self.passwd
        authority = AUTHORITY_ROPC if ropc else AUTHORITY_SIGN_IN
        self.app = msal.PublicClientApplication(CLIENT_ID,
                                                authority=authority,
                                                validate_authority=False)
        self.login()

    def login(self):
        """Logs in the user to Climeon API."""
        result = None
        if self.user and self.passwd:
            self.logger.debug("Logging in with user %s", self.user)
            result = self.app.acquire_token_by_username_password(self.user,
                                                                 self.passwd,
                                                                 MSAL_SCOPE)
        else:
            self.logger.debug("Silent login")
            accounts = self.app.get_accounts()
            account = accounts[0] if accounts else None
            result = self.app.acquire_token_silent(MSAL_SCOPE, account=account)
        if not result:
            self.logger.debug("Interactive login")
            result = self.app.acquire_token_interactive(MSAL_SCOPE)
        if "error" in result:
            raise Exception(result["error_description"])
        token = result["access_token"]
        auth = f"Bearer {token}"
        self.headers = {"authorization": auth}

    def get(self, endpoint, retry=True):
        """General purpose GET method."""
        req_url = self.url + endpoint
        response = requests.get(req_url, headers=self.headers)
        if response.text.startswith("AuthenticationFailed") and retry:
            self.login()
            return self.get(endpoint, retry=False)
        if not response.ok:
            raise Exception(response.text)
        return response

    def post(self, endpoint, body, retry=True):
        """General purpose POST method."""
        req_url = self.url + endpoint
        json_body = json.dumps(body)
        # Add needed headers
        headers = self.headers
        headers["Content-Type"] = "application/json-patch+json"
        headers["accept"] = "text/plain"
        response = requests.post(req_url, headers=headers, data=json_body)
        if response.text.startswith("AuthenticationFailed") and retry:
            self.login()
            return self.post(endpoint, body, retry=False)
        if not response.ok:
            raise Exception(response.text)
        return response


    # Analytics

    def analytics(self, machine_id, date_from, date_to, variables=None, interval=None):
        """Get specific machine/variable log data from the Analytics database.

        Parameters:
            machine_id (str): module or powerblock id e.g. "0100000016".
            date_from (datetime): Datetime to get data from.
            date_to (datetime): Datetime to get data to.
            variables (list, optional): Variables to get. Defaults to all
                                        available variables.
            interval (str, optional): Interval between timestamps. Defaults to a
                                      reasonable interval. Can be any of
                                      ``["PT1S", "PT10S", "PT1M", "PT10M", \
                                         "PT1H", "PT12H", "PT24H"]``.

        Returns:
            DataFrame: A Pandas DataFrame.
        """
        # pylint: disable=too-many-arguments,too-many-locals
        filename = offline_name(machine_id, date_from, date_to, variables, interval)
        dataframe = load_dataframe(filename)
        if not dataframe is None:
            return dataframe
        interval = interval or default_interval(date_from, date_to)
        if interval not in VALID_INTERVALS:
            raise ValueError("Interval must be one of %s" % VALID_INTERVALS)
        variables = variables or self.analytics_variables(machine_id)
        body = {
            "searchSpan": {
                "from": date_iso_utc(date_from),
                "to": date_iso_utc(date_to)
            },
            "interval": interval,
            "parameters": [{
                "id": machine_id,
                "variables": variables
            }]
        }
        response = self.post("/Analytics", body)
        raw_data = response.json()
        dataframe = json_to_dataframe(raw_data[machine_id])
        self._save_dataframe(dataframe, filename)
        return dataframe

    def analytics_variables(self, machine_id):
        """Get all available variables for a machine."""
        endpoint = f"/Analytics/variables/{machine_id}"
        response = self.get(endpoint)
        return response.json()

    def tsi_query(self, machine_id, date_from, date_to, variables, interval=None):
        """Query the TSI database.

        Parameters:
            machine_id (str): module or powerblock id e.g. "0100000016".
            date_from (datetime): Datetime to get data from.
            date_to (datetime): Datetime to get data to.
            variables (dict): Variables on TSX syntax. See
                              https://docs.microsoft.com/en-us/rest/api/time-series-insights/
            interval (str, optional): Interval size specified in ISO-8601
                                      duration format:
                                      https://en.wikipedia.org/wiki/ISO_8601

        Returns:
            DataFrame: A Pandas DataFrame.
        """
        #pylint: disable=too-many-arguments
        interval = interval or default_interval(date_from, date_to)
        if interval not in VALID_INTERVALS:
            raise ValueError("Interval must be one of %s" % VALID_INTERVALS)
        body = {
            "aggregateSeries": {
                "timeSeriesId": [
                    machine_id
                ],
                "searchSpan": {
                    "from": tsi_utc(date_from),
                    "to": tsi_utc(date_to)
                },
                "inlineVariables": variables,
                "interval": interval,
                "projectedVariables": list(variables.keys())
            }
        }
        response = self.post("/Analytics/tsi/query", body)
        raw_data = response.json()
        if "error" in raw_data:
            raise Exception(raw_data["error"]["message"])
        dataframe = json_to_dataframe(raw_data)
        return dataframe


    # Modules

    def modules(self):
        """Get info for all registered modules."""
        response = self.get("/Modules")
        return response.json()

    def module_info(self, module_id):
        """Get info for a specific module."""
        endpoint = f"/Modules/{module_id}"
        response = self.get(endpoint)
        return response.json()

    def modules_telemetry(self):
        """Get all modules latest telemetry."""
        response = self.get("/Modules/telemetry")
        return response.json()

    def module_telemetry(self, module_id):
        """Get latest module telemetry for a specific module."""
        endpoint = f"/Modules/{module_id}/telemetry/"
        response = self.get(endpoint)
        return response.json()

    def module_alerts(self, module_id):
        """Get current alerts for a specific module."""
        endpoint = f"/Modules/{module_id}/alerts/"
        response = self.get(endpoint)
        return response.json()

    def module_alert_history(self, module_id):
        """Get alert history for a specific module."""
        endpoint = f"/Modules/{module_id}/alertHistory/"
        response = self.get(endpoint)
        return response.json()


    # PowerBlocks

    def powerblocks(self):
        """Get info for all registered powerblocks."""
        response = self.get("/PowerBlocks")
        return response.json()

    def powerblock_info(self, powerblock_id):
        """Get info for a specific powerblock."""
        endpoint = f"/PowerBlocks/{powerblock_id}"
        response = self.get(endpoint)
        return response.json()

    def powerblock_alerts(self, powerblock_id):
        """Get current alerts for a specific powerblock."""
        endpoint = f"/PowerBlocks/{powerblock_id}/alerts/"
        response = self.get(endpoint)
        return response.json()

    def powerblock_alert_history(self, powerblock_id):
        """Get alert history for a specific powerblock."""
        endpoint = f"/PowerBlocks/{powerblock_id}/alertHistory/"
        response = self.get(endpoint)
        return response.json()


    # Users

    def users(self):
        """Get info for all registered users."""
        response = self.get("/Users")
        return response.json()


    # SecurityGroups

    def security_groups(self):
        """Get info for all registered security groups."""
        response = self.get("/SecurityGroups")
        return response.json()


    # Helpers

    def get_log_file(self, machine_id, date):
        """Retrieves log file for a specific module and date."""
        date_str = date.strftime("%y%m%d")
        if module(machine_id):
            endpoint = f"/Modules/{machine_id}/data/{date_str}"
        elif powerblock(machine_id):
            endpoint = f"/PowerBlocks/{machine_id}/data/{date_str}"
        elif hp_system(machine_id):
            endpoint = f"/HPSystems/{machine_id}/data/{date_str}"
        else:
            error = f"Bad id supplied {machine_id}"
            raise ValueError(error)
        response = self.get(endpoint)
        return response.text

    def download_logfile(self, machine_id, date, directory="."):
        """Download a logfile to disk."""
        date_str = date.strftime("%y%m%d")
        log_file = self.get_log_file(machine_id, date)
        log_path = f"{directory}/{machine_id}_{date_str}.csv"
        with open(log_path, mode="w+", encoding="utf-8") as file_stream:
            file_stream.write(log_file)
        return log_path

    def get_log_data(self, machine_id, date_from, date_to=None, variables=None):
        """Get log data for a machine/date."""
        filename = offline_name(machine_id, date_from, date_to, variables, "")
        dataframe = load_dataframe(filename)
        if not dataframe is None:
            return dataframe
        date_to = date_to or date_from + timedelta(days=1)
        diff = date_to - date_from
        date_list = [date_from + timedelta(days=d) for d in range(diff.days)]
        for date in date_list:
            data_str = self.get_log_file(machine_id, date)
            header_idx = data_str.index("Timestamp")
            dateframe = pd.read_csv(StringIO(data_str[header_idx:]))
            dateframe["Timestamp"] = pd.to_datetime(dateframe["Timestamp"])
            dateframe = dateframe.set_index("Timestamp")
            if variables:
                drop_var = [c for c in dateframe.columns if c not in variables]
                dateframe = dateframe.drop(drop_var, axis=1)
            if dataframe is None:
                dataframe = dateframe
            else:
                dataframe = pd.concat([dataframe, dateframe])
        self._save_dataframe(dataframe, filename)
        return dataframe

    def get_machines(self):
        """Get all registered modules/powerblocks."""
        powerblocks = self.powerblocks()
        machines = [m["moduleId"] for p in powerblocks for m in p["modules"]]
        machines.extend([p["powerBlockId"] for p in powerblocks])
        machines.sort()
        return machines

    def _save_dataframe(self, dataframe, filename):
        """Save dataframe to disk. Tries both parquet and pickle."""
        global PARQUET_WARN # pylint: disable=global-statement
        if not path.exists(OFFLINE_FOLDER):
            makedirs(OFFLINE_FOLDER)
        files = listdir(OFFLINE_FOLDER)
        folder_size = sum(path.getsize(f) for f in files if path.isfile(f))
        if folder_size > FOLDER_SIZE_LIMIT:
            oldest_file = min(files, key=path.getctime)
            remove(oldest_file)
        if not PARQUET_WARN:
            try:
                dataframe.to_parquet(filename + ".parquet")
            except ImportError:
                self.logger.warning("No parquet support installed. Falling back on pickle.")
                PARQUET_WARN = True
        if PARQUET_WARN:
            dataframe.to_pickle(filename + ".pickle")

def offline_name(machine_id, date_from, date_to, variables, interval):
    """Get offline name for log data."""
    var = "".join(c for c in variables) if variables else ""
    name_raw = OFFLINE_NAME % (machine_id, date_from, date_to, var, interval)
    filename = sha1(bytes(name_raw, "utf-8")).hexdigest()
    return path.join(OFFLINE_FOLDER, filename)

def load_dataframe(filename):
    """Load a dataframe from disk. Tries both parquet and pickle."""
    if path.exists(filename + ".parquet"):
        return pd.read_parquet(filename + ".parquet")
    if path.exists(filename + ".pickle"):
        return pd.read_pickle(filename + ".pickle")
    return None

def tsi_utc(date):
    """Convert a date to a format that TSI can use."""
    return date_iso_utc(date).replace("+00:00", "Z")

def date_iso_utc(date):
    """Convert date to timezone aware, UTC, ISO formatted string."""
    if date.tzinfo is None:
        # Timezone naive, use locale
        date = date.astimezone()
    return date.astimezone(timezone.utc).isoformat()

def json_to_dataframe(raw_data):
    """Convert raw json data to a dataframe."""
    columns = [p["name"] for p in raw_data["properties"]]
    columns.insert(0, "Timestamp")
    data = [p["values"] for p in raw_data["properties"]]
    data.insert(0, raw_data["timestamps"])
    data = list(map(list, zip(*data)))
    dataframe = pd.DataFrame(data, columns=columns)
    dataframe["Timestamp"] = pd.to_datetime(dataframe["Timestamp"])
    dataframe = dataframe.set_index("Timestamp")
    return dataframe

def default_interval(date_from, date_to):
    """Figure out a reasonable interval for a time range."""
    diff = (date_to - date_from).total_seconds()
    for max_result, interval in MAX_INTERVALS.items():
        if diff < max_result:
            return interval
    raise ValueError("Could not find a valid interval for this range.")
