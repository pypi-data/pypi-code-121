# Copyright 2022 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

import copy

from . import logger
from .connector_filter import ConnectorFilter
from .client import HubClient
from .server_service_pb2 import ConnectorQuery


class BaseContext():
    """A Base Context typically extended by another class which will contain some utility methods
    to communicate with a specific Connector type"""

    def __init__(self, hub_client: HubClient, wellknown_connector_id: str, connector_filter: ConnectorFilter = None):
        """Create a BaseContext from the specified parameters

        Args:
            hub_client (HubClient): The HubClient which makes client requests to Cegal Hub Server.
            wellknown_connector_id (str): the wellknown string that represents the Connector type. i.e cegal.hub.agentor cegal.hub.petrel
            connector_filter (ConnectorFilter, optional): the filter for targeting a specific instance or instances of a Connector type. Defaults to None.
        """
        self._hub_client = hub_client
        self._wellknown_connector_id = wellknown_connector_id
        if connector_filter is None:
            logger.debug("no ConnectorFilter specified")
            connector_filter = ConnectorFilter()
        self._connector_filter = connector_filter

    def __repr__(self):
        return "wellknown_connector_id: " + self._wellknown_connector_id + ", connector filter:" + repr(self._connector_filter)

    @property
    def available(self):
        """Get the available Cegal Hub Connectors

        Raises:
            Exception: If there was a problem obtaining the available Cegal Hub Connectors

        Returns:
            Connector[]: An enumeration of objects for available Connectors
        """        
        stub = self._hub_client.server_request_stub
        msg = ConnectorQuery()
        msg.filter.connector_instance_id = self._connector_filter.target_connector_id
        msg.filter.wellknown_identifier = self._wellknown_connector_id
        if self._connector_filter._labels_dict:
            for k in self._connector_filter._labels_dict.keys():
                msg.filter.labels[k] = self._connector_filter._labels_dict[k]
        logger.debug("querying the the server for available connectors")
        result = stub.QueryConnectors(msg)
        if not result.ok:
            logger.warn(f"error querying the server for connectors:  result.error_message")
            raise Exception(f"error querying the server for connectors:  result.error_message")
        else:
            return result.available_connectors

    @property
    def connector_filter(self):
        """Get the ConnectorFilter associated with the context.

        Returns:
            ConnectorFilter: The ConnectorFilter object.
        """        
        return self._connector_filter

    @connector_filter.setter
    def connector_filter(self, connector_filter=None):
        """Set the ConnectorFilter on the context.

        Args:
            connector_filter ([type], optional): The ConnectorFilter object. Defaults to None.
        """        
        if connector_filter is None:
            connector_filter = ConnectorFilter()
        self._connector_filter = connector_filter

    @property
    def connection_parameters(self):
        """Get a deep copy of the ConnectionParameters corresponding to the running Cegal Hub Server

        Returns:
            ConnectionParameters: The ConnectionParameters object.
        """
        return copy.deepcopy(self._hub_client.connection_parameters)
