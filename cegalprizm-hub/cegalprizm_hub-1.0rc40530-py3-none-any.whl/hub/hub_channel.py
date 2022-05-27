# Copyright 2022 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

import grpc

from cegal.keystone_auth import OidcClient, OidcOptions
from cegal.keystone_auth.responses import CegalProductTemplate

from . import logger
from .keystone_auth_interceptor import auth_header_interceptor
from .connection_parameters import ConnectionParameters
from .server_config import ServerConfig

class HubChannel:
    """A Cegal Hub configured GRPC channel for use with a Cegal Hub Server.
    """

    def __init__(self, connection_parameters: ConnectionParameters = None, token_provider=None):
        """Create a HubChannel which wraps a GRPC channel

        Args:
            connection_parameters (ConnectionParameters, optional): The connection paramaters for communicating with a Cegal Hub Server. Defaults to None.
            token_provider (token_provider, optional): Most often an OidcClient object. Defaults to None.
        """
        if connection_parameters is None:
            connection_parameters = ConnectionParameters()
        self._channel = None
        host = connection_parameters.host
        port = connection_parameters.port
        url = host + ":" + str(port)
        logger.debug(f"HubChannel using url {url}")
        self._token_provider = token_provider
        if connection_parameters.use_auth:
            if token_provider is None:
                logger.debug(f"HubChannel requires auth and no explict token provider specified, so will use the prizm clientid")
                oidc_options = OidcOptions(client_id="prizm",
                                           provider_uri=ServerConfig.get_keystone_url(),
                                           audiences=["hub_connector_api"],
                                           extra_scopes=["offline_access", "hub_connector_api"])
                self._token_provider = OidcClient(oidc_options,
                page_handler=CegalProductTemplate(
                product="Cegal Prizm",
                extra="<h3>You have successfully logged into Cegal Prizm</h3>"))

        chan = None
        channel_options = [
            ("grpc.max_receive_message_length", 524288000), 
            ("grpc.max_send_message_length", 524288000)
        ]

        if connection_parameters.use_tls:
            logger.debug("HubChannel creating a secure tls grpc channel")
            chan = grpc.secure_channel(url, grpc.ssl_channel_credentials(), options=channel_options)
        else:
            logger.debug("HubChannel creating an insecure grpc channel")
            channel_options.append(('grpc.enable_http_proxy', 0))
            chan = grpc.insecure_channel(url, options=channel_options)

        if connection_parameters.use_auth and self._token_provider is not None:
            logger.debug("HubChannel using a token provider")
            interceptor = auth_header_interceptor(token_provider=self._token_provider)
            chan = grpc.intercept_channel(chan, interceptor)
        else:
            logger.debug("HubChannel NOT using auth")

        self._channel = chan
        self._connection_parameters = connection_parameters

    @property
    def connection_parameters(self):
        """The ConnectionParameters associated with a running Cegal Hub Server.

        Returns:
            ConnectionParameters: The ConnectionParameters associated with a running Cegal Hub Server.
        """        
        return self._connection_parameters

    @property
    def channel(self):
        """The GRPC channel associated with a running Cegal Hub Server.

        Returns:
            Channel: The GRPC channel associated with a running Cegal Hub Server.
        """        
        return self._channel

    @property
    def token_provider(self):
        """The token provider associated with authenticating against a Cegal Hub Server.

        Returns:
            token_provider: Usually an OidcClient.
        """        
        return self._token_provider

    def close(self):
        """Close the underlying GRPC channel.
        """        
        self._channel.close()
