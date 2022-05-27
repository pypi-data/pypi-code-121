# Copyright 2022 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

from typing import Iterable

from . import logger
from .connection_parameters import ConnectionParameters
from .connector_filter import ConnectorFilter
from .connector_request_service_pb2 import ConnectorRequest
from .connector_request_service_pb2_grpc import ConnectorRequestServiceStub
from .server_service_pb2_grpc import ServerServiceStub
from .hub_channel import HubChannel


class HubClient(HubChannel):
    """A convenience utility class for making GRPC unary, client and server streaming requests to Cegal Hub Connectors via a running Cegal Hub Server.

    Args:
        HubChannel (HubChannel): Extends HubChannel which provides logic for setting up a GRPC channel
    """
    def __init__(self, connection_parameters: ConnectionParameters = None, token_provider=None):
        """Create a HubClient utility object for making Cegal Hub Connector requests via a Cegal Hub Server.

        Args:
            connection_parameters (ConnectionParameters, optional): The configuration details to communicate with a running Cegal Hub Server. Defaults to None.
            token_provider (token_provider, optional): Most often an OidcClient object. Defaults to None.
        """        
        super().__init__(connection_parameters, token_provider)
        self._connector_request_stub = ConnectorRequestServiceStub(self._channel)
        self._server_request_stub = ServerServiceStub(self._channel)
        self._connection_parameters = connection_parameters

    def do_unary_request(self, wellknown_connector_identifier, wellknown_payload_identifier, payload, connector_filter: ConnectorFilter = None, major_version:int=0, minor_version:int=0):
        """Make a unary GRPC client request against a wellknown Cegal Hub Connector type and wellknown payload identifier via a running Cegal Hub Server.

        Args:
            wellknown_connector_identifier (str): The wellknown identifier of a Cegal Hub Connector type such as cegal.hub.agent or cegal.hub.petrel 
            wellknown_payload_identifier (str): The wellknown payload identifier (functionality supported by the Cegal Hub Connector) such as cegal.hub.agent.list_files
            payload (Any): A protobuf Any object
            major_version (int): The major version number for the payload
            minor_version (int): The minor version number for the payload
            connector_filter (ConnectorFilter, optional): A ConnectorFilter to help target a specific Connector instance(s). Defaults to None.

        Returns:
            tuple: A tuple containing a success / failure bool, the result Any payload and the connector instance identifier str that handled the request
        """        
        if connector_filter is None:
            connector_filter = ConnectorFilter()
        request = ConnectorRequest(
            wellknown_connector_identifier=wellknown_connector_identifier,
            wellknown_payload_identifier=wellknown_payload_identifier,
            payload_major_version = major_version,
            payload_minor_version = minor_version,
            target_connector_id=connector_filter.target_connector_id,
            payload=payload,
        )

        if connector_filter.labels_dict:
            for k in connector_filter.labels_dict.keys():
                request.labels[k] = connector_filter.labels_dict[k]
        logger.debug(f"unary request: {request}")
        result = self.connector_request_stub.DoUnary(request)
        logger.debug(f"unary result: {result}")
        if (result.ok):
            return (True, result.payload, result.connector_id)
        else:
            return (False, result.error_message, result.connector_id)

    def do_server_streaming(self, wellknown_connector_identifier: str, wellknown_payload_identifier: str, payload, connector_filter: ConnectorFilter = None, major_version:int=0, minor_version:int=0):
        """Make a server streaming GRPC client request against a wellknown Cegal Hub Connector type and wellknown payload identifier via a running Cegal Hub Server.

        Args:
            wellknown_connector_identifier (str): The wellknown identifier of a Cegal Hub Connector type such as cegal.hub.agent or cegal.hub.petrel 
            wellknown_payload_identifier (str): The wellknown payload identifier (functionality supported by the Cegal Hub Connector) such as cegal.hub.agent.list_files
            payload (Any): A protobuf Any object
            connector_filter (ConnectorFilter, optional): A ConnectorFilter to help target a specific Connector instance(s). Defaults to None.
            major_version (int): The major version number for the payload
            minor_version (int): The minor version number for the payload

        Yields:
            tuple: A tuple containing a success / failure bool, the result Any payload and the connector instance identifier str that handled the request
        """        
        if connector_filter is None:
            connector_filter = ConnectorFilter()
        request = ConnectorRequest(
            wellknown_connector_identifier=wellknown_connector_identifier,
            wellknown_payload_identifier=wellknown_payload_identifier,
            target_connector_id=connector_filter.target_connector_id,
            payload=payload,
            payload_major_version=major_version,
            payload_minor_version=minor_version,
        )

        if connector_filter.labels_dict:
            for k in connector_filter.labels_dict.keys():
                request.labels[k] = connector_filter.labels_dict[k]
        logger.debug(f"server streaming request: {request}")
        responses = self.connector_request_stub.DoServerStreaming(request)
        for result in responses:
            if (result.ok):
                logger.debug(f"server streaming result ok: {result}")
                yield (True, result.payload, result.connector_id)
            else:
                logger.debug(f"server streaming result error: {result.error_message}")
                yield (False, result.error_message, result.connector_id)

    def do_client_streaming(self, wellknown_connector_identifier: str, wellknown_payload_identifier: str, iterable_payloads: Iterable, connector_filter: ConnectorFilter = None, major_version:int=0, minor_version:int=0):
        """Make a client streaming GRPC client request against a wellknown Cegal Hub Connector type and wellknown payload identifier via a running Cegal Hub Server.

        Args:
            wellknown_connector_identifier (str): The wellknown identifier of a Cegal Hub Connector type such as cegal.hub.agent or cegal.hub.petrel 
            wellknown_payload_identifier (str): The wellknown payload identifier (functionality supported by the Cegal Hub Connector) such as cegal.hub.agent.list_files
            iterable_payloads (Iterable): The client payloads to stream to the Cegal Hub Connector
            major_version (int): The major version number for the payload
            minor_version (int): The minor version number for the payload
            connector_filter (ConnectorFilter, optional): A ConnectorFilter to help target a specific Connector instance(s). Defaults to None.

        Returns:
            tuple: A tuple containing a success / failure bool, the result Any payload and the connector instance identifier str that handled the request

        Yields:
            [type]: [description]
        """        
        if connector_filter is None:
            connector_filter = ConnectorFilter()

        def wrap_iterable_payloads(it_p):
            for payload in it_p:
                request = ConnectorRequest(
                    wellknown_connector_identifier=wellknown_connector_identifier,
                    wellknown_payload_identifier=wellknown_payload_identifier,
                    target_connector_id=connector_filter.target_connector_id,
                    payload=payload,
                    payload_major_version=major_version,
                    payload_minor_version=minor_version,
                )
                if connector_filter.labels_dict:
                    for k in connector_filter.labels_dict.keys():
                        request.labels[k] = connector_filter.labels_dict[k]
                yield request

        logger.debug("client streaming sending iterable requests")
        result = self.connector_request_stub.DoConnectorInstanceClientStreaming(wrap_iterable_payloads(iterable_payloads))

        if (result.ok):
            logger.debug(f"client streaming result ok: {result}")
            return (True, result.payload, result.connector_id)
        else:
            logger.debug(f"client streaming result error: {result}")
            return (False, result.error_message, result.connector_id)

    @property
    def connector_request_stub(self):
        """The service stub for clients to communicate with Cegal Hub Connectors

        Returns:
            ConnectorRequestServiceStub: The service stub for clients to communicate with Cegal Hub Connectors
        """        
        return self._connector_request_stub

    @property
    def server_request_stub(self):
        """The service stuf stub for clients to communicate with a Cegal Hub Server

        Returns:
            ServerServiceStub: The service stuf stub for clients to communicate with a Cegal Hub Server
        """        
        return self._server_request_stub

    @property
    def connection_parameters(self):
        """The ConnectionParameters object associated with the running Cegal Hub Server.

        Returns:
            ConnectionParameters: The ConnectionParameters object associated with the running Cegal Hub Server.
        """        
        return self._connection_parameters

    def close(self):
        """Close the underlying GRPC channel.
        """
        self._channel.close()
