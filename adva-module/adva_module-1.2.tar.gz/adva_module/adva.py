import requests
import urllib3
from functools import reduce

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


LOGIN = 'session_login'
LOGOUT = 'session_logout'
REFRESH = 'session_refresh'
LOGS = 'condition_log'
HISTORY = 'history_monitor'


class AdvaError(Exception):

    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return self.reason


class AdvaResult(object):

    """
    Adva Result class
    """

    def __init__(self):
        """
        Arguments:
            _output: Result
            _success: Boolean
            _error: Error output
        """
        self._output = None
        self._success = False
        self._error = None

    @property
    def output(self):
        return self._output

    @property
    def success(self):
        return self._success

    @property
    def error(self):
        return self._error

    def json(self):
        return {
            "output": self.output,
            "success": self.success,
            "error": self.error,
        }

    @success.setter
    def success(self, value):
        self._success = value

    @error.setter
    def error(self, value):
        self._error = value

    @output.setter
    def output(self, value):
        self._output = value

    def __str__(self):
        return "CobraResult"


class Adva(object):

    """
    Core Adva class
    """

    def __init__(self, **kwargs):
        """
        Initialise a NitroClass
        """
        self._ip = kwargs.get("ip", "127.0.0.1")
        self._url = "https://{}/FSP3000/scripts/".format(self._ip)
        self._username = kwargs.get("username", None)
        self.__password = kwargs.get("password", None)
        self._verify = kwargs.get("verify", False)
        self._headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'es-419,es;q=0.9,es-ES;q=0.8,en;q=0.7,en-GB;q=0.6,en-US;q=0.5',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': 'Windows',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.44',
            'X-Requested-With': 'XMLHttpRequest',
        }
        self._payload = {
            "user": self._username,
            "password": self.__password,
            "login_context": "13",
        }
        self._cookies = None
        self._session = requests.Session()
        self._result = AdvaResult()

    # -------------------------------------------------   Control

    @property
    def result(self):
        return self._result

    @property
    def cookies(self):
        return self._cookies

    @cookies.setter
    def cookies(self, value):
        self._cookies = value

    def login(self):
        """
        Login function to manage session with Adva
        """
        try:
            attributes = {
                "url": self._url + LOGIN,
                "headers": self._headers,
                "data": self._payload,
                "verify": self._verify
            }
            self._session.post(**attributes)
            self._cookies = self._session.cookies.get_dict()['session_id']
        except Exception as e:
            self._result.error = "[LoginError]: " + str(e)

    def logout(self, token=None):
        """
        Logout function to quit from Adva
        """
        try:
            payload = {
                "url": self._url + LOGOUT,
                "headers": self._headers,
                "verify": self._verify,
            }
            if token:
                payload['headers']['Cookie'] = 'session_id={};'.format(token)
                requests.get(**payload)
            else:
                if self._cookies:
                    self._session.get(**payload)
        except Exception as e:
            self._result.error = "[LogoutError]: " + str(e)

    def refresh(self, token=None):
        """
        Refresh function to refresh session
        """
        try:
            payload = {
                "url": self._url + REFRESH,
                "headers": self._headers,
                "verify": self._verify,
            }
            if token:
                payload['headers']['Cookie'] = 'session_id={};'.format(token)
                requests.get(**payload)
            else:
                if self._cookies:
                    self._session.get(**payload)
        except Exception as e:
            self._result.error = "[RefreshError]: " + str(e)

    def query(self, **kwargs):
        """
        Function to query Adva
        """
        domain = kwargs.get('domain', None)
        params = kwargs.get('params', None)
        token = kwargs.get('token', None)
        try:
            payload = {
                "url": self._url + domain,
                "headers": self._headers,
                "params": params,
                "verify": self._verify,
            }
            if token:
                payload["headers"]["Cookie"] = 'session_id={};'.format(token)
                return requests.get(**payload)
            else:
                if self._cookies:
                    return self._session.get(**payload)
        except Exception as e:
            self._result.error = "[QueryError]: " + str(e)
            return False

    def get_logs(self, counts, token=None):
        """
        Function to get Logs
        """
        try:
            input = {
                "domain": LOGS,
                "token": token,
                "params": {
                    'count': str(counts)
                }
            }
            response = self.query(**input)
            self._result.output = response.json()['olderEntries']
            self._result.success = True
        except Exception as e:
            self._result.error = "[ResponseError]: " + str(e)

    def get_history_15min(self, interface, token=None):
        """
        Function to get history attenuation 15 minutes
        """
        try:
            input = {
                "domain": HISTORY,
                "token": token,
                "params": {
                    '{}'.format(interface): '',
                    'timePeriod': '15MIN',
                    'firstRecordNo': '1',
                }
            }
            response = self.query(**input)
            temp = []
            for item in response.json()['records']:
                lista = list(
                    map(lambda x: {x["keyword"]: x["value"]}, item["parameters"]))
                f = reduce(lambda a, b: {**a, **b}, lista)
                f["recordNo"] = item["recordNo"]
                f["timestampDisp"] = item["timestampDisp"]
                temp.append(f)
            self._result.output = temp
            self._result.success = True
        except Exception as e:
            self._result.error = "[ResponseError]: " + str(e)

    def get_history_24hour(self, interface, token=None):
        """
        Function to get history attenuation 24 minutes
        """
        try:
            input = {
                "domain": HISTORY,
                "token": token,
                "params": {
                    '{}'.format(interface): '',
                    'timePeriod': '24HOUR',
                    'firstRecordNo': '1',
                }
            }
            self.query(**input)
        except Exception as e:
            self._result.error = "[ResponseError]: " + str(e)
