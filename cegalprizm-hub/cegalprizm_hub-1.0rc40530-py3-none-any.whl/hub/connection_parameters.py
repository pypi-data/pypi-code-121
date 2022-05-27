# Copyright 2022 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

from .server_config import ServerConfig
from .client_config import ClientConfig


class ConnectionParameters:
    """The connection parameters for communicating with a Cegal Hub Server."""
    def __init__(self, host: str = None, port: int = None, use_tls: bool = None, use_auth: bool = None):
        """Creates a ConnectionParameters from the given arguments. If not provided the parameters will be set to
        either local values or created from environment varaiables.

        Args:
            host (str, optional): the IP address or dns name of the Cegal Hub Server. Defaults to None.
            port (int, optional): the port the CegalHub Server runs on. Typically this would be 9595 for local host or 443 for secure TLS connections. Defaults to None.
            use_tls (bool, optional): indicates that a secure connection to the Cegal Hub Server is required. Defaults to None.
            use_auth (bool, optional): indicates that the Python client requires authentication when communicating the Hub Server. Defaults to None.
        """

        if host is None:
            host = ServerConfig.get_host()
        if port is None:
            port = ServerConfig.get_port()
        if use_tls is None:
            use_tls = ServerConfig.get_use_tls()
        if use_auth is None:
            use_auth = ClientConfig.get_use_auth()
        self._host = host
        self._port = port
        self._use_tls = use_tls
        self._use_auth = use_auth

    def __repr__(self):
        return "host:" + self._host + ", port:" + str(self._port) + ", use TLS:" + repr(self._use_tls) + ", use auth:" + repr(self._use_auth)

    @property
    def host(self):
        """Get the host address of the Cegal Hub Server.

        Returns:
            str: The host address of the Cegal Hub Server.
        """        
        return self._host

    @property
    def port(self):
        """Get the port that the Cegal Hub Server runs on.

        Returns:
            str: The port that the Cegal Hub Server runs on.
        """        
        return self._port

    @property
    def use_tls(self):
        """Whether the Cegal Hub Server is running with TLS.

        Returns:
            bool: Whether the Cegal Hub Server is running with TLS.
        """        
        return self._use_tls

    @property
    def use_auth(self):
        """Whether to use authentication when connecting with the Cegal Hub Server.

        Returns:
            bool: Whether to use authentication when connecting with the Cegal Hub Server.
        """        
        return self._use_auth