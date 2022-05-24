"""Package used with REST APIs"""
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


# Used for all AW REST API queries
class REST():
    """REST API Framework"""

    # Add the varibles as self.
    def __init__(self,
                 url='',
                 protocol='https',
                 timeout=10,
                 retries=5,
                 headers=None,
                 proxy=None,
                 debug=False):
        # Import Proxy Server settings
        self.proxies = proxy
        self.url = url
        self.debug = debug
        self.timeout = timeout
        self.retries = retries
        self.protocol = protocol

        # Start the session
        self.sessions = requests.Session()
        if isinstance(headers, dict):
            self.sessions.headers.update(headers)

        retries = Retry(total=self.retries,
                        backoff_factor=1,
                        status_forcelist=[502, 503, 504])
        self.sessions.mount('%s://' % protocol,
                            HTTPAdapter(max_retries=retries))

        # Debugging
        if self.debug:
            print('API URL: %s' % self.url)
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True

    # HTTP GET, returns HTTP response object
    def get(self, path, querystring=""):
        "HTTP GET"
        connection = self.sessions.get(self.protocol + '://' + self.url + path,
                                       proxies=self.proxies,
                                       timeout=self.timeout,
                                       params=querystring)
        return connection

    # HTTP POST, returns HTTP response object
    def post(self, path, json=None, querystring="", payload=None):
        """HTTP POST"""
        connection = self.sessions.post(self.protocol + '://' + self.url +
                                        path,
                                        data=payload,
                                        json=json,
                                        proxies=self.proxies,
                                        timeout=self.timeout,
                                        params=querystring)
        return connection

    # HTTP PUT, returns HTTP response object
    def put(self, path, payload, querystring=""):
        """HTTP PUT"""
        connection = self.sessions.put(self.protocol + '://' + self.url + path,
                                       data=payload,
                                       proxies=self.proxies,
                                       timeout=self.timeout,
                                       params=querystring)
        return connection

    # HTTP DELETE, returns HTTP response object
    def delete(self, path, querystring=""):
        """HTTP DELETE"""
        connection = self.sessions.delete(self.protocol + '://' + self.url +
                                          path,
                                          proxies=self.proxies,
                                          timeout=self.timeout,
                                          params=querystring)
        return connection

    # HTTP patch, returns HTTP response object
    def patch(self, path, payload, querystring=""):
        """HTTP patch"""
        connection = self.sessions.patch(self.protocol + '://' + self.url + path,
                                         data=payload,
                                         proxies=self.proxies,
                                         timeout=self.timeout,
                                         params=querystring)
        return connection

    # HTTP GET, returns response headers json
    def response_headers(self, path, querystring=""):
        """Gets response headers"""
        connection = self.sessions.get(self.protocol + '://' + self.url + path,
                                       proxies=self.proxies,
                                       timeout=self.timeout,
                                       params=querystring)
        return connection.headers
