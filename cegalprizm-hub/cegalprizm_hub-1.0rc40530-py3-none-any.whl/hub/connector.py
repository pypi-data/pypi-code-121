# Copyright 2022 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

from typing import Dict, Iterable

import os
import threading
import socket
import sys
import time
import queue

from . import logger
from .connection_parameters import ConnectionParameters
from .connector_task_service_pb2 import CONNECTOR_UNARY, CONNECTOR_CLIENT_STREAMING, CONNECTOR_STREAMING
from .connector_task_service_pb2 import Connect, ConnectorResponse, ConnectorTaskResult
from .connector_task_service_pb2_grpc import ConnectorTaskServiceStub
from .hub_channel import HubChannel
from .task_registry import HubTaskRegistry


class HubConnector(HubChannel):
    """A generic HubConnector which can be extended by concrete implementations. This API is considered experimental.

    Args:
        HubChannel ([HubChannel]): A HubChannel object which defines the connection to a Cegal Hub Server

    """

    def __init__(self, wellknown_identifier: str,
                 friendly_name: str,
                 description: str,
                 version: str,
                 build_version: str,
                 connection_parameters: ConnectionParameters = None,
                 token_provider=None,
                 join_token: str = "",
                 supports_public_requests: bool = False,
                 additional_labels: Dict[str, str] = None):
        super().__init__(connection_parameters, token_provider)

        self._response_q = queue.Queue()
        self._wellknown_identifier = wellknown_identifier
        self._friendly_name = friendly_name
        self._description = description
        self._version = version
        self._build_version = build_version
        self._join_token = join_token
        self._supports_public_requests = supports_public_requests
        self._additional_labels = additional_labels

        self._connector_task_stub = ConnectorTaskServiceStub(self._channel)

    def _create_initial_message(self, task_registry: HubTaskRegistry):
        try:
            hostname = os.environ["HOSTNAME"]
        except:
            hostname = socket.gethostname()

        connectorInfo = Connect()
        connectorInfo.wellknown_identifier = self._wellknown_identifier
        connectorInfo.friendly_name = self._friendly_name
        connectorInfo.description = self._description
        connectorInfo.host_name = hostname
        connectorInfo.operating_system = sys.platform
        connectorInfo.version = self._version
        connectorInfo.build_version = self._build_version
        connectorInfo.supports_public_requests = self._supports_public_requests
        connectorInfo.join_token = self._join_token

        for task in task_registry.get_supported_tasks():
            connectorInfo.supported_payloads[task.wellknown_payload_identifier].wellknown_payload_identifier = task.wellknown_payload_identifier
            connectorInfo.supported_payloads[task.wellknown_payload_identifier].friendly_name = task.friendly_name
            connectorInfo.supported_payloads[task.wellknown_payload_identifier].description = task.description
            connectorInfo.supported_payloads[task.wellknown_payload_identifier].supported_rpc_types.append(CONNECTOR_UNARY)
            connectorInfo.supported_payloads[task.wellknown_payload_identifier].major_version = task.major_version
            connectorInfo.supported_payloads[task.wellknown_payload_identifier].minor_version = task.minor_version
            if task.payload_auth is not None:
                for audience in task.payload_auth.required_audiences:
                    connectorInfo.supported_payloads[task.wellknown_payload_identifier].auth.required_audience.append(audience)
                for claim in task.payload_auth.required_app_claims:
                    connectorInfo.supported_payloads[task.wellknown_payload_identifier].auth.required_blueback_app_claims.append(claim)

        if self._additional_labels:
            for key in self._additional_labels.keys():
                connectorInfo.labels[key] = self._additional_labels[key]
        return connectorInfo

    def _connector_tasks_iterator(self, task_registry) -> Iterable[ConnectorResponse]:
        info = self._create_initial_message(task_registry)
        initial_response = ConnectorResponse(connect=info)
        yield initial_response

        try:
            while True:
                task_result = self._response_q.get()
                response = ConnectorResponse(task_result=task_result)
                yield response
                self._response_q.task_done()
        except Exception as error:
            logger.error(f"{error}")

        logger.debug(f"Clearing response q")
        with self._response_q.mutex:
            self._response_q.queue.clear()
            self._response_q.all_tasks_done.notify_all()
            self._response_q.unfinished_tasks = 0
        logger.debug(f"Cleared response q")

    def _create_success_result(self, rpc_type, request_id, payload):
        task_result = ConnectorTaskResult()
        task_result.request_id = request_id
        task_result.rpc_type = rpc_type
        task_result.logical_request_completed = True
        task_result.ok = True
        task_result.payload.Pack(payload)
        return task_result

    def _create_failure_result(self, rpc_type, request_id, error_message):
        task_result = ConnectorTaskResult()
        task_result.request_id = request_id
        task_result.rpc_type = rpc_type
        task_result.logical_request_completed = True
        task_result.ok = False
        task_result.error_message = error_message
        return task_result

    def _do_connector_tasks(self, task_registry):
        while True:
            try:
                logger.info(f"Attempting to connect to Cegal Hub")
                response_iterator = self._connector_task_stub.DoConnectorTasks(self._connector_tasks_iterator(task_registry))
                for connectorTask in response_iterator:
                    if connectorTask.acknowledge_connector_joined:
                        logger.info(f"Successfully connected")
                    else:
                        logger.info(f"Task {connectorTask.payload_identifier} {connectorTask.request_id}")

                        if connectorTask.rpc_type == CONNECTOR_UNARY:
                            task = task_registry.get_unary_task(connectorTask.payload_identifier)
                            if task:
                                result = task(connectorTask.payload)
                                if result[0]:
                                    task_result = self._create_success_result(connectorTask.rpc_type, connectorTask.request_id, result[1])
                                else:
                                    task_result = self._create_failure_result(connectorTask.rpc_type, connectorTask.request_id, result[1])
                            else:
                                logger.warning(f"payload_identifier {connectorTask.payload_identifier} not recognised")
                                task_result = self._create_failure_result(connectorTask.rpc_type, connectorTask.request_id, f"payload_identifier {connectorTask.payload_identifier} not recognised")

                        elif connectorTask.rpc_type == CONNECTOR_CLIENT_STREAMING:
                            logger.warning(f"Client streaming task {connectorTask.request_id}")
                            task_result = self._create_failure_result(connectorTask.rpc_type, connectorTask.request_id, "Client streaming not supported")
                        elif connectorTask.rpc_type == CONNECTOR_STREAMING:
                            logger.warning(f"Server streaming task {connectorTask.request_id}")
                            task_result = self._create_failure_result(connectorTask.rpc_type, connectorTask.request_id, "Server streaming not supported")
                        else:
                            logger.error(f"Unknown RpcType {connectorTask}")
                            task_result = self._create_failure_result(connectorTask.rpc_type, connectorTask.request_id, "Unknown rpc type")

                        logger.info(f"Task complete")
                        self._response_q.put(task_result)

            except Exception as error:
                logger.error(f"{error}")

            logger.debug(f"Clearing response q")
            with self._response_q.mutex:
                self._response_q.queue.clear()
                self._response_q.all_tasks_done.notify_all()
                self._response_q.unfinished_tasks = 0
            logger.debug(f"Cleared response q")
            time.sleep(10)

    def start(self, task_registry: HubTaskRegistry):
        logger.debug("Starting DoConnectorTask")
        threading.Thread(target=self._do_connector_tasks(task_registry), daemon=True).start()
