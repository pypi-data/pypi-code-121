# Copyright 2022 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

import os


class ServerConfig():
    """The global Hub Server configuration for communicating with a Cegal Hub Server. This is used primarily with ConnectionParameters objects.
    When a ConnectionParameters object is created but no values are provided, the ConnectionParameters object will rely on the ClientConfig and ServerConfig 
    global configurations for defaults."""

    __host: str = None
    __port: int = None
    __use_tls: bool = None
    __keystone_url: str = None

    @staticmethod
    def set_host(host: str):
        """Update the host address of the Cegal Hub Server

        Args:
            host (str): The host address of the Cegal Hub Server
        """        
        ServerConfig.__host = host

    @staticmethod
    def get_host():
        """Get the host address of a Cegal Hub Server. By default it will look for an environment variable
        called CEGAL_HUB_HOST

        Returns:
            [str]: The address of the Cegal Hub Server.
        """        
        if ServerConfig.__host is None:
            val = ServerConfig.__get_envvar("CEGAL_HUB_HOST")
            if val[0]:
                return val[1]
            else:
                return "localhost"
        else:
            return ServerConfig.__host

    @staticmethod
    def set_port(port: int):
        """Update the port on which to talk to a Cegal Hub Server.

        Args:
            port (int): The port to talk to a Cegal Hub Server.
        """        
        ServerConfig.__port = port

    @staticmethod
    def get_port():
        """Gets the port on which to talk to a Cegal Hub Server. By default it will look for an environment variable
        called CEGAL_HUB_PORT

        Returns:
            [int]: The port on which to talk to a Cegal Hub Server.
        """        
        if ServerConfig.__port is None:
            val = ServerConfig.__get_envvar("CEGAL_HUB_PORT")
            if val[0]:
                return int(val[1])
            else:
                return 9595
        else:
            return ServerConfig.__port

    @staticmethod
    def set_use_tls(use_tls: bool):
        """Set whether or not to use Transport Level Security (TLS) when talking to a Cegal Hub Server

        Args:
            use_tls (bool): True if using TLS, False otherwise.
        """        
        ServerConfig.__use_tls = use_tls

    @staticmethod
    def get_use_tls():
        """Get whether or not to use Transport level Security (TLS) when talking to a Cegal Hub Server. By default it will look for an environment variable
        called CEGAL_HUB_USE_TLS

        Returns:
            [bool]: True if using TLS, False otherwise.
        """        
        if ServerConfig.__use_tls is None:
            val = ServerConfig.__get_envvar("CEGAL_HUB_USE_TLS")
            if val[0]:
                return val[1].lower() == "true"
            else:
                return False
        else:
            return ServerConfig.__use_tls

    @staticmethod
    def __get_envvar(key: str):
        env = os.environ
        try:
            return (True, env[key])
        except:
            return (False, "")

    @staticmethod
    def set_keystone_url(url: str):
        """Update the URL for the Cegal Keystone Secure Token Server. Typically only used by Cegal development teams.

        Args:
            url (str): The URL to the Cegal Keystone Secure Token Server.
        """        
        ServerConfig.__keystone_url = url

    @staticmethod
    def get_keystone_url():
        """Get the URL of the Cegal Keystone Secure Token Server.

        Returns:
            [str]: The URL of the Cegal Keystone Secure Token Server.
        """        
        if ServerConfig.__keystone_url is None:
            return "https://keystone.cegal-geo.com/identity"
        return ServerConfig.__keystone_url

    @staticmethod
    def __repr__():
        return "host:" + ServerConfig.get_host() + ", port:" + repr(ServerConfig.get_port()) + ", use TLS:" + repr(ServerConfig.get_use_tls()) + ", Keystone URL:" + ServerConfig.get_keystone_url()
