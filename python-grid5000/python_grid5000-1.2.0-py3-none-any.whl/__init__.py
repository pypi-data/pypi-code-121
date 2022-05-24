import copy
import json
import logging
from pathlib import Path
from typing import Dict, Union


import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import yaml

from .exceptions import *  # noqa
from .objects import *  # noqa
from .__version__ import __version__


logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.grid5000.fr/stable"
DEFAULT_CA_BUNDLE = "/etc/ssl/certs/ca-certificates.crt"
USER_AGENT = "python-grid5000 %s" % __version__


def _create_session(
    retries=5, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None
):
    session = session or requests.Session()

    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


class Grid5000(object):
    """Represents a Grid5000 API connection.

    Args:
        uri (str): The URL of the Grid5000 api.
        username (str): The user login.
        password (str): The user password.
        verify_ssl (bool); Whether SSL certificates should be validated.
        timeout (float): Timeout to use for requests to the Grid5000 API.
        session (requests.Session): session to use
        ssl_cert (str): path to the client certificate file for Grid5000 API
        ssl_key (str): path to the client key file for Grid5000 API
    """

    def __init__(
        self,
        uri=DEFAULT_BASE_URL,
        username=None,
        password=None,
        verify_ssl=None,
        timeout=None,
        session=None,
        sslcert=None,
        sslkey=None,
        ssluser="anonymous",
        **kwargs,
    ):
        self._uri = uri
        self.timeout = timeout
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        if self.verify_ssl is None:
            # By default, requests ignores trusted CA from the system
            # (it uses certifi instead).
            # On Grid'5000 frontend and nodes, it is necessary to use the
            # system CA bundle, because it includes the root Grid'5000 CA
            # allowing to validate the internal API certificate.
            ca_bundle = Path(DEFAULT_CA_BUNDLE)
            if ca_bundle.exists():
                self.verify_ssl = ca_bundle
            else:
                # As a last resort, use certifi
                self.verify_ssl = True

        self.client_ssl = False
        self.client_cert = None
        if sslcert is not None:
            self.client_ssl = True
            self.default_ssl_user = ssluser
            if sslkey is not None:
                self.client_cert = (sslcert, sslkey)
            else:
                self.client_cert = sslcert

        self.headers = {"user-agent": USER_AGENT}
        self.session = _create_session()

        # manage auth
        self._http_auth = None
        if self.username and not self.client_ssl:
            self._http_auth = requests.auth.HTTPBasicAuth(self.username, self.password)

        self.set_initial_managers()
        if not self.verify_ssl:
            logger.warning(
                "Unverified HTTPS request is being made. Make sure "
                + "to do this on purpose or set verify_ssl in the configuration "
                + "file"
            )
            import urllib3

            urllib3.disable_warnings()

    def set_initial_managers(self):
        self.root = RootManager(self)
        self.sites = SiteManager(self)
        self.stitcher = StitcherManager(self)
        self.network_equipments = RootNetworkEquipmentManager(self)

    @classmethod
    def from_yaml(cls, yaml_file):
        try:
            with open(yaml_file, "r") as f:
                conf = yaml.safe_load(f)
                return cls(**conf)
        except Exception as e:
            logging.warn(e)
            logging.info("...Falling back to anonymous connection")
            return cls()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return self.session.close()

    def _build_url(self, path):
        """Returns the full url from path.

        If path is already a url, return it unchanged. If it's a path, append
        it to the stored url.

        Returns:
            str: The full URL
        """
        if path.startswith("http://") or path.startswith("https://"):
            return path
        else:
            return "%s%s" % (self._uri, path)

    def _get_session_opts(
        self, content_type=None, accept=None, user_id=None, other_headers=None
    ):
        """Returns list of option and headers to use of an http transaction

        Args:
            content_type (str): value of the Content-type http headers
            accept (str) : value of the Accept http header
            user_id (str) : Grid5000 user id to use in certificate mode
            other_headers (dict) : other http headers to include
        """
        request_headers = self.headers.copy()
        if content_type is not None:
            request_headers["Content-type"] = content_type
        if accept is not None:
            request_headers["Accept"] = accept

        res = {
            "headers": request_headers,
            "timeout": self.timeout,
            "verify": self.verify_ssl,
            "cert": self.client_cert,
        }

        if self.client_ssl:
            if user_id is not None:
                request_headers["X-Api-User-CN"] = user_id
                request_headers["X-Remote-Ident"] = user_id
            else:
                request_headers["X-Api-User-CN"] = self.default_ssl_user
                request_headers["X-Remote-Ident"] = self.default_ssl_user
        else:
            res["auth"] = self._http_auth

        if other_headers is not None:
            request_headers.update(other_headers)

        return res

    def http_request(
        self,
        verb,
        path,
        query_data=None,
        post_data=None,
        header_data=None,
        streamed=False,
        content_type="application/json",
        accept="application/json",
        **kwargs,
    ):
        """Make an HTTP request to the Grid5000 API.

        Args:
            verb (str): The HTTP method to call ('get', 'post', 'put',
                        'delete')
            path (str): Path or full URL to query ('/sites' or
                        'http://api.grid5000.fr/stable/sites')
            query_data (dict): Data to send as query parameters
            post_data (dict): Data to send in the body (will be converted to
                              json)
            header_data (dict): Data to send as http headers
            streamed (bool): Whether the data should be streamed
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            A requests result object.

        Raises:
            Grid5000HttpError: When the return code is not 2xx
        """
        query_data = {} if query_data is None else query_data
        url = self._build_url(path)

        g5k_user = None
        if self.client_ssl:
            g5k_user = kwargs.pop("g5k_user", None)

        opts = self._get_session_opts(
            content_type=content_type,
            accept=accept,
            user_id=g5k_user,
            other_headers=header_data,
        )

        verify = opts.pop("verify")
        timeout = opts.pop("timeout")
        cert = opts.pop("cert")

        json = post_data
        data = None

        # building params from query params and kwargs
        params = {}
        params = copy.deepcopy(query_data)
        params.update(kwargs)

        req = requests.Request(verb, url, json=json, data=data, params=params, **opts)
        prepped = req.prepare()

        settings = self.session.merge_environment_settings(
            prepped.url, {}, streamed, verify, cert
        )

        while True:
            result = self.session.send(prepped, timeout=timeout, **settings)
            # TODO:
            # https://www.grid5000.fr/mediawiki/index.php/API#Status_Codes
            if 200 <= result.status_code < 300:
                return result

            error_message = result.content
            try:
                error_json = result.json()
                for k in ("message", "error"):
                    if k in error_json:
                        error_message = error_json[k]
            except (KeyError, ValueError, TypeError):
                pass

            if result.status_code == 401:
                raise Grid5000AuthenticationError(
                    response_code=result.status_code,
                    error_message=error_message,
                    response_body=result.content,
                )

            raise Grid5000HttpError(
                response_code=result.status_code,
                error_message=error_message,
                response_body=result.content,
            )

    def http_get(self, path, query_data={}, streamed=False, raw=False, **kwargs):
        """Make a GET request to the Grid5000 server.

        Args:
            path (str): Path or full URL to query ('/projects' or
                        'http://whatever/v4/api/projecs')
            query_data (dict): Data to send as query parameters
            streamed (bool): Whether the data should be streamed
            raw (bool): If True do not try to parse the output as json
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            A requests result object is streamed is True or the content type is
            not json.
            The parsed json data otherwise.

        Raises:
            Grid5000HttpError: When the return code is not 2xx
            Grid5000ParsingError: If the json data could not be parsed
        """
        result = self.http_request(
            "get", path, query_data=query_data, streamed=streamed, **kwargs
        )

        # NOTE(msimonin): Grid5000 API is returning
        # 'application/json; charset=utf-8'
        if (
            "application/json" in result.headers["Content-Type"]
            and not streamed
            and not raw
        ):
            try:
                return result.json()
            except Exception:
                raise Grid5000ParsingError(
                    error_message="Failed to parse the server message"
                )
        else:
            return result

    def http_list(self, path, query_data={}, **kwargs):
        """Make a GET request to the Grid5000 API for list-oriented queries.

        Args:
            path (str): Path or full URL to query ('/sites' or
                        'https://base_url/sites')
            query_data (dict): Data to send as query parameters
            **kwargs: Extra options to send to the server (e.g. sudo, page,
                      per_page)

        Returns:
            list: A list of the objects returned by the server.

        Raises:
            Grid5000HttpError: When the return code is not 2xx
            Grid5000ParsingError: If the json data could not be parsed
        """
        url = self._build_url(path)

        result = self.http_request("get", url, query_data=query_data, **kwargs)

        # NOTE(msimonin): in the future we may want to support automatic
        # pagination Thus we'll need to return an iterator here (in a generic
        # way ...)

        # NOTE(msimonin): here we hit the HATEOAS vs non HATEOAS hell
        result = result.json()
        if "items" in result:
            return result["items"]
        else:
            return result

    def http_post(self, path, query_data={}, post_data={}, **kwargs):
        """Make a POST request to the Grid5000 server.

        Args:
            path (str): Path or full URL to query ('/sites' or
                        'https://api.grid5000.fr/stable/sites')
            query_data (dict): Data to send as query parameters
            post_data (dict): Data to send in the body (will be converted to
                              json)
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            The parsed json returned by the server if json is return, else the
            raw content

        Raises:
            Grid5000HttpError: When the return code is not 2xx
            Grid5000ParsingError: If the json data could not be parsed
        """
        result = self.http_request(
            "post", path, query_data=query_data, post_data=post_data, **kwargs
        )
        try:
            # NOTE(msimonin): Grid5000 API is returning
            # 'application/json; charset=utf-8'
            if "application/json" in result.headers["Content-Type"]:
                return result.json()
        except Exception:
            raise Grid5000ParsingError(
                error_message="Failed to parse the server message"
            )
        return result

    def http_delete(self, path, **kwargs):
        """Make a DELETE request to the Grid5000 server.

        Args:
            path (str): Path or full URL to query ('/projects' or
                        'http://whatever/v4/api/projecs')
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            The requests object.

        Raises:
            Grid5000HttpError: When the return code is not 2xx
        """
        return self.http_request("delete", path, content_type=None, **kwargs)

    def dump_ref_api(self):
        """Get the whole ref api as a dict

        This is https://api.grid5000.fr/3.0?deep=1
        """
        return self.http_get("/", query_data=dict(deep=1))


class Grid5000Offline(Grid5000):
    """Browse the ref API (only GET / possibly offline)."""

    def __init__(self, data: Dict):
        self._data = data["items"]
        self._uri = ""
        self.set_initial_managers()

    @classmethod
    def from_yaml(cls, data_path: Union[Path, str]):
        if isinstance(data_path, str):
            data_path = Path(data_path)
        data = dict()
        with data_path.open("r") as f:
            data = json.load(f)
        return cls(data)

    def http_get(self, path, *args, **kwargs):
        return self._ride_down_the_data(path)

    def http_list(self, path, *args, **kwargs):
        """
        There's some differences in the returned format when reading the ref
        API as a whole.
        """
        c = self._ride_down_the_data(path)
        if isinstance(c, dict):
            return list(c.values())
        return c

    def http_delete(self, path, *args, **kwargs):
        raise ValueError("You can't delete a resource with this client")

    def http_post(self, path, *args, **kwargs):
        raise ValueError("You can't modify a resource with this client")

    def _ride_down_the_data(self, path):
        """Retrieve an internal dict targetted by path.

        /sites/rennes/cluster/paravance -> data[sites][rennes][cluster][paravance]
        """
        splitted = path[1:].split("/")
        node = self._data
        for split in splitted:
            if split in node:
                node = node[split]
                continue
            if isinstance(node, list):
                # lookup internally
                node = [c for c in node if c.get("uid") == split][0]
                continue
            # 404 without any HTTP calls :)
            raise Grid5000HttpError(
                f"Impossible to follow the path {path} in the data", response_code=404
            )
        return node
