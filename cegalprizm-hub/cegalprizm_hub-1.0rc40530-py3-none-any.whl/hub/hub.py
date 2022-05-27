# Copyright 2022 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

import grpc
from packaging import version
from cegal.keystone_auth import OidcClient, OidcOptions
from cegal.keystone_auth.responses import CegalProductTemplate
from . import logger
from .connector_filter import ConnectorFilter
from .agent import AgentContext
from .petrel import PetrelContext
from .client import HubClient
from .connection_parameters import ConnectionParameters
from .server_config import ServerConfig
from .keystone_auth_interceptor import auth_header_interceptor
from .server_service_pb2 import HealthQuery, ServerQuery, ConnectorQuery, ActivateServerRequest
from .server_service_pb2_grpc import ServerServiceStub
from cegalprizm.hub import __version__


class Hub:
    """Provides access to communicate with an instance of a running Cegal Hub Server. The Cegal Hub Server may be local or remote. A Hub instance
    provides helper methods to make Cegal Hub Server queries and access to Cegal Hub Petrel Connectors and Cegal Hub Agent Connectors via contexts."""

    def __init__(self, connection_parameters: ConnectionParameters = None):
        """Creates a Hub with the specified ConnectionParameters with useful methods to obtain contexts
        to a Cegal Hub Agent Connector or Cegal Hub Petrel Connector and make Cegal Hub Server queries. 

        Args:
            connection_parameters (ConnectionParameters, optional): The connection parameters which address
            a Cegal Hub Server. Defaults to None.
        """
        if connection_parameters is None:
            logger.debug("connection parameters not provided, will create default")
            connection_parameters = ConnectionParameters()
            
        self._hub_client = HubClient(connection_parameters)

    def __repr__(self):
        return "hub connection params: " + repr(self._hub_client._connection_parameters)      

    def default_petrel_ctx(self):
        """Get a default PetrelContext object. If the user has several PetrelContext objects available it will arbitrarily select the first
        instance. This PetrelContext will be a strong handle to a specific Petrel instance.
        
        Raises:
            Exception: If no Petrel instances are connected to the Hub Server or are not available to the user.

        Returns:
            PetrelContext: A strong handle to a running instance of Petrel connected to Hub Server.
        """
        cf = ConnectorFilter()
        ctx = PetrelContext(self._hub_client, "cegal.hub.petrel", cf)
        available = ctx.available
        logger.debug(f"there are {len(available)} connectors available")
        if len(available) > 0:
            logger.debug(f"selecting 1st available connector with id {available[0].connector_id}")
            ctx.connector_filter.target_connector_id = available[0].connector_id
            return ctx
        else:
            logger.warn("No Petrel connectors are available")
            raise Exception("No Petrel connectors are available")

    def new_petrel_ctx(self, connector_filter: ConnectorFilter = None):
        """Create a new PetrelContext. If a targeting ConnectorFilter is not provided, this will be a loose handle to all available
        Petrel instances that the user has available. In this scenario if multiple Petrel instances are available, logical client requests
        will be made using a round-robin schedule.

        Args:
            connector_filter (ConnectorFilter, optional): A means to target a particular connector instance(s). Defaults to None.

        Returns:
            PetrelContext: A handle to one or more Petrel instances.
        """        
        if connector_filter is None:
            connector_filter = ConnectorFilter()
        return PetrelContext(self._hub_client, "cegal.hub.petrel", connector_filter)

    def default_agent_ctx(self):
        """Get a default AgentContext object. If the user has several AgentContext objects available it will arbitrarily select the first
        instance. This AgentContext will be a strong handle to a specific Agent instance.
        
        Raises:
            Exception: If no Agent instances are connected to Hub Server or are not available to the user.

        Returns:
            AgentContext: A strong handle to a running instance of an Agent connected to Hub Server.
        """        
        cf = ConnectorFilter()
        ctx = AgentContext(self._hub_client, "cegal.hub.agent", cf)
        available = ctx.available
        logger.debug(f"there are {len(available)} connectors available")
        if len(available) > 0:
            logger.debug(f"selecting 1st available connector with id {available[0].connector_id}")
            ctx.connector_filter.target_connector_id = available[0].connector_id
            return ctx
        else:
            logger.warn("No Agent connectors are available")
            raise Exception("No Agent connectors are available")

    def new_agent_ctx(self, connector_filter: ConnectorFilter = None):
        """Create a new AgentContext.If a targeting ConnectorFilter is not provided, this will be a loose handle to all available
        Agent instances that the user has available. In this scenario if multiple Agent instances are available, logical client requests
        will be made using a round-robin schedule.

        Args:
            connector_filter (ConnectorFilter, optional): A means to target a particular connector instance(s). Defaults to None.

        Returns:
            AgentContext: A handle to one or more Agent instances.
        """        
        if connector_filter is None:
            connector_filter = ConnectorFilter()
        return AgentContext(self._hub_client, "cegal.hub.agent", connector_filter)

    def verify_health(self):
        """Verify the health of a running Cegal Hub Server

        Returns:
            HealthQueryResult: An object containing non-sensitive open information about the Cegal Hub Server
        """        
        msg = HealthQuery()
        result = self._hub_client.server_request_stub.VerifyHealth(msg)
        logger.info("Cegal Hub Server GRPC service is healthy")
        return result

    def query_server(self):
        """Query a running Cegal Hub Server for information on the Hub Server.

        Returns:
            ServerQueryResult: An object containing information about the running Cegal Hub Server.
        """        
        msg = ServerQuery()
        result = self._hub_client.server_request_stub.QueryServer(msg)
        logger.debug(result)
        return result

    def print_query_server(self):
        """Print human-friendly information about a running Cegal Hub Server.
        """        
        msg = ServerQuery()
        result = self._hub_client.server_request_stub.QueryServer(msg)
        logger.debug(result)
        dt = result.run_date.ToDatetime()
        print("Server started: " + str(dt))
        print("Server version: " + result.version)
        print("Server git hash: " + result.git_hash)
        print("Operating system: " + result.operating_system)
        print("License type: " + result.license)
        print("GRPC API Version: " + result.grpc_api_version)
        print("Allow Connector join token: " + str(result.allow_connector_join_token))
        print("Require Connector join token: " + str(result.require_connector_join_token))
        print("Require Connector authentication: " + str(result.require_connector_auth))
        print("Require Client authentication: " + str(result.require_client_auth))
        print("Number of connected private connectors: " + str(result.num_connected_private_connectors))
        print("Number of connected public connectors: " + str(result.num_connected_public_connectors))

    def query_connectors(self, wellknown_identifier="", wellknown_payload_identifier="", connector_filter: ConnectorFilter = None):
        """Query Connectors available to the user on a running Cegal Hub Server.

        Args:
            wellknown_identifier (str, optional): Limit the returned result to only Connectors of a given wellknown type. Defaults to "".
            wellknown_payload_identifier (str, optional): Limit the return result to only include Connectors that have the specified wellknown payload. Defaults to "".
            connector_filter (ConnectorFilter, optional): A ConnectorFilter object to target a specific Connector(s). Defaults to None.

        Returns:
            ConnectorQueryResult: An object containing information about the Cegal Hub Connectors available to the user.
        """        
        if connector_filter is None:
            connector_filter = ConnectorFilter()
        msg = ConnectorQuery()
        msg.filter.connector_instance_id = connector_filter.target_connector_id
        msg.filter.wellknown_identifier = wellknown_identifier
        msg.filter.wellknown_payload_identifier = wellknown_payload_identifier
        if connector_filter.labels_dict: 
            for k in connector_filter.labels_dict.keys():
                msg.filter.labels[k] = connector_filter.labels_dict[k]

        result = self._hub_client._server_request_stub.QueryConnectors(msg)
        if (result.ok):
            logger.debug(result)
            return result.available_connectors
        else:
            return result.error_message

    def print_query_connectors(self,
                               show_meta: bool = True,
                               show_payloads: bool = True,
                               show_labels: bool = True,
                               wellknown_identifier: str = "",
                               wellknown_payload_identifier: str = "",
                               connector_filter: ConnectorFilter = None):
        """Print human-friendly information about the Cegal Hub Connectors available to the user.

        Args:
            show_meta (bool, optional): Include meta information in the output. Defaults to True.
            show_payloads (bool, optional): Include payload information in the output. Defaults to True.
            show_labels (bool, optional): Include Connector labels in the output. Defaults to True.
            wellknown_identifier (str, optional): Target a specific instance of a running Cegal Hub Connector with the given connector identifier. Defaults to "".
            wellknown_payload_identifier (str, optional): Target specific Connectors based on the specified wellknown payload identifier. Defaults to "".
            connector_filter (ConnectorFilter, optional): A ConnectorFilter object to target a specific Connector(s). Defaults to None.

        Raises:
            Exception: If there is a problem querying the running Cegal Hub Server
        """                               
        if connector_filter is None:
            connector_filter = ConnectorFilter()
        msg = ConnectorQuery()
        msg.filter.connector_instance_id = connector_filter.target_connector_id
        msg.filter.wellknown_identifier = wellknown_identifier
        msg.filter.wellknown_payload_identifier = wellknown_payload_identifier
        if connector_filter.labels_dict:
            for k in connector_filter.labels_dict.keys():
                msg.filter.labels[k] = connector_filter.labels_dict[k]

        result = self._hub_client._server_request_stub.QueryConnectors(msg)
        if (result.ok):
            if len(result.available_connectors) == 0:
                print("No connectors found!")
            for connector in result.available_connectors:
                print("connector instance")
                print("------------------")
                print("id: " + connector.connector_id)
                print("wellknown id: " + connector.wellknown_identifier)
                if show_meta:
                    dt = connector.connect_date.ToDatetime()
                    print("supports public requests: " + str(connector.supports_public_requests))
                    print("friendly name: " + connector.friendly_name)
                    print("description: " + connector.description)
                    print("host name: " + connector.host_name)
                    print("operating system: " + connector.operating_system)
                    print("connect date: " + str(dt))
                    print("version: " + connector.version)
                    print("build version: " + connector.build_version)
                if show_payloads:
                    print("")
                    print(" connector payloads")
                    print(" ------------------")
                    for k in connector.supported_payloads:
                        print(" wellknown payload id: " + connector.supported_payloads[k].wellknown_payload_identifier + ", friendly name: " + connector.supported_payloads[k].friendly_name + ", description: " + connector.supported_payloads[k].description)
                if show_labels:
                    print("")
                    print(" connector labels")
                    print(" ------------------")
                    for key in connector.labels:
                        print(" key:" + key + "     value:" + connector.labels[key])
                print("")
        else:
            raise Exception(f"error querying server: {result.error_message}")

    def activate(self):
        """Activate a running Cegal Hub Server instance. The activation is only needed once on a running Cegal Hub Server instance. It is also only needed
        if the Cegal Hub is running in Server mode.

        Returns:
            ActivateServerResult: An object representing the result of the activation.
        """        
        # use the hub logical client as server claim is in there for server activation (if the user is licensed to use it)
        # basic to desktop upgrade only needs hub_connector_api claim
        oidc_options = oidc_options = OidcOptions(client_id="prizm",
                                           provider_uri=ServerConfig.get_keystone_url(),
                                           audiences=["hub_connector_api"],
                                           extra_scopes=["offline_access", "hub_connector_api"])
        oidc_client = OidcClient(oidc_options,
        page_handler=CegalProductTemplate(
        product="Cegal Prizm",
        extra="<h3>You have successfully logged into Cegal Prizm</h3>"))
        url = self._hub_client.connection_parameters.host + ":" + str(self._hub_client.connection_parameters.port)

        if self._hub_client.connection_parameters.use_tls:
            chan = grpc.secure_channel(url, grpc.ssl_channel_credentials())
        else:
            chan = grpc.insecure_channel(url, options=(('grpc.enable_http_proxy', 0),))
        interceptor = auth_header_interceptor(token_provider=oidc_client)
        channel = grpc.intercept_channel(chan, interceptor)
        stub = ServerServiceStub(channel)
        msg = ActivateServerRequest()
        result = stub.ActivateServer(msg)
        if (result.ok):
            logger.info("Cegal Hub Server activated or upgraded")
        else:
            logger.warning(f"error activating server: {result.error_message}")

        return result

    def is_version_compatible(self):
        """Checks the compatibility of the Cegal Hub Python client library with the running Cegal Hub Server.

        Returns:
            bool: True if compatible, False if incompatible or compatibilty cannot be determined.
        """        
        msg = HealthQuery()
        try:
            result = self._hub_client.server_request_stub.VerifyHealth(msg)
        except Exception as error:
            logger.warning(f"cannot verify compatibility as Cegal Hub Server cannot be reached: {error}")
            return False

        client_version = version.parse(__version__)
        server_version = version.parse(result.grpc_api_version)
        try:
            client_version.major
        except AttributeError:
            logger.info(f"cannot parse major version, you are probably running a development version")
            client_version = version.parse("1.0.0")

        #compare the major version number for compatibility
        compatible = client_version.major == server_version.major
        if compatible is False:
            logger.warning(f"the Hub Server major version '{server_version.major}' is not compatible with the Python client library major version '{client_version.major}'")
        return compatible    

    def close(self):
        """Close the underlying HubClient GRPC channel.
        """        
        self._hub_client.close()    
