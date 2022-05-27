# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import os
import socket
import struct

import contrast
from contrast.agent.connection_status import ConnectionStatus
from contrast.agent.service_config import ServiceConfig
from contrast.agent.settings import Settings
from contrast.api.dtm_pb2 import (
    Activity,
    AgentStartup,
    ApplicationCreate,
    ApplicationUpdate,
    HttpRequest,
    Message,
    ObservedRoute,
    Poll,
    ServerActivity,
)
from contrast.api.settings_pb2 import AgentSettings
from contrast.utils.exceptions.contrast_service_exception import (
    ContrastServiceException,
)
from contrast.utils.singleton import Singleton
from contrast.utils import service_util
from contrast.utils.service_util import ServiceUtil
from contrast.utils.timer import now_ms

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


_RECV_FMT = ">I"
_APPLICATION_LANGUAGE = "Python"


class _ServiceState(Singleton):
    def init(self):
        """
        Singletons should override init, not __init__.
        """
        self.count = 0
        self.connection_status = ConnectionStatus()
        self.bundled_flag = "external"
        self.service_config = ServiceConfig(Settings().config)
        self.poll = Poll()

    @property
    def local_service_configured(self):
        return self.service_config.local_service_configured

    @property
    def client_id(self):
        """
        Client id is used by Speedracer to recognize when messages are sent by different
        worker processes of the same application.
        client_id must be the parent process id as it is the same for all workers serving an app.
        :return: str app name and parent process id
        """
        return str(Settings().app_name) + "-" + str(os.getppid())

    @property
    def app_path(self):
        """
        Return the path for where the application is running, either configured
        in common config or by looking at the current working dir.
        """
        return (
            Settings().config.get("application.path") or contrast.AGENT_CURR_WORKING_DIR
        )

    @property
    def resend_startup(self):
        return self.connection_status.resend_startup

    def start_service(self):
        """
        Start the bundled service.

        Should not be run if the user would like to connect to an external service.

        :return: bool if bundled Contrast Service was started.
        """
        settings = Settings()

        logger.info(
            "Attempted to start bundled Contrast Service for application %s.",
            settings.app_name,
        )
        logger.info(
            "If socket already exists at %s, will attempt to connect to that instead",
            self.service_config.address,
        )

        path = settings.config.get("agent.service.logger.path")

        if not ServiceUtil(path).start_bundled_service():
            logger.error("Contrast Service did not start")
            return False

        return True

    def initialize_and_send_messages(self):
        """
        Initializing the connection to Contrast Service requires checking if the app is configured
        to use the bundled service and turning it on if so.

        If the app isn't configured to use the bundled service or after turning the bundled service on,
        agent sends initial messages to Contrast Service (AgentStartup, ApplicationCreate)
        to determine that it is successfully able to communicate with it.

        If configuration specifies an external service, whatever manages the external service should handle cases
        of the service being down. The agent should not be responsible for managing service state in this case.

        :return: list of Message responses

        """
        settings = Settings()

        if settings.is_bundled_enabled and self.local_service_configured:
            self.bundled_flag = "bundled"

            if not self.start_service():
                # if bundled service is configured but it could not be started,
                # then we don't have service data to process, so we should not
                # continue on with Agent startup.
                raise ContrastServiceException

        logger.info("Will communicate with Contrast Service")
        self._build_and_send_startup_msgs()

    def _build_and_send_startup_msgs(self):
        settings = Settings()

        first_msg = self._build_agent_startup_msg(settings)

        # it's only necessasry to wait to send messages when using the bundled service
        # because it takes a bit to start up
        wait = 1 if self.bundled_flag == "bundled" else 0

        responses = self.send_messages_retry([first_msg], wait=wait)
        if not responses:
            # If we received no response for the first message, we should not
            # try to send the second message.
            raise ContrastServiceException

        settings.process_responses(responses)

        # now that we have server features from first_msg we can build + send app create
        second_msg = self._build_app_create_msg(settings)

        # no wait because we know SR is already up
        responses = self.send_messages_retry([second_msg])
        if not responses:
            # If we received no response for the second message, we should not
            # continue on with Agent startup.
            raise ContrastServiceException

        settings.process_responses(responses)

    def send_messages_retry(self, messages, attempts=0, wait=0, raise_exception=True):
        """
        Attempt to send a list of messages to Speedracer. If sending messages fails, this method
        recursively calls itself to attempt to resend 3 times.

        If after 3 times sending messages still failed, the connection status is set to faise
        and the exception may or may not be raised.

        :param messages: message(s) to to send to Speedracer
        :param attempts: a count of number of attempts to send to messages.
        :param wait: seconds to wait before sending the messages.
            This is used when the bundled service is getting started (start_service has been called)
            because sometimes it takes a second for it to get setup.
        :param raise_exception: bool to determine if to raise an exception or not
            The caller of this method will determine if to ask this method to raise the exception or not.
            Currently the logic is that the caller will ask to raise the exception if the caller itself is catching for it.

            Current callers that will ask for this exception to be raised are:
            1. when initializing communication to Speedracer, because the middleware needs to know if this initialization
                has failed to set settings initialization to false.
            2. when input analysis messages are send to Speedracer, because the middleware needs to know if
                this analysis has failed to re-route the request to call_without_agent.

            Current callers that will not want the exception to be raised:
            1. when final messages are sent to Speedracer for reporting. The middleware is not equipped
                to handle an exception at that time, so if sending these messages fails, the reporting will fail
                but the application should not.

        :return: list of responses from Speedracer
        :side effect: ContrastServiceException if raise_exception is True
        """
        service_util.sleep(wait)

        try:
            return self._send_messages(messages)
        except ContrastServiceException:
            logger.debug(
                "Trying to send messages, but received ContrastServiceException"
            )

            if attempts < 3:
                if self.bundled_flag == "bundled":
                    # this may lead to multiple contrast-service processes existing on the same host if
                    # the first initialized process is not up before other app workers / threads attempt
                    # to start the service.
                    self.start_service()
                logger.debug("Retrying to send messages...")
                return self.send_messages_retry(
                    messages, attempts + 1, wait, raise_exception
                )

            logger.warning(
                "Unable to send messages to Contrast Service after 3 attemps."
            )
            self.connection_status.failure()
            if raise_exception:
                raise

        return []

    def send_dtm(self, message):
        """
        This takes in a json string so that we can encode and decode in separate tasks

        :param message: json string representation of the dtm object
        :return: json string of the response
        :side effect: ContrastServiceException if any problems connecting / sending messages occur
        """
        packed = message.SerializeToString()
        sock = None
        try:
            sock = socket.socket(self.service_config.socket_type, socket.SOCK_STREAM)
            sock.connect(self.service_config.address)
            self.send_message(sock, packed)
            response = self.receive_message(sock)

            if response is not None:
                settings = AgentSettings()
                settings.ParseFromString(response)
                return settings

            logger.warning("Received an empty response from Contrast Service")
        except Exception:
            # If there are any issues connecting or sending messages to Contrast Service,
            # we raise a special exception for middleware handle_exception to catch but not raise
            # so the request can be processed without the agent.
            raise ContrastServiceException
        finally:
            if sock is not None:
                sock.close()

        return None

    def _send_messages(self, messages):
        responses = []
        messages = [messages] if not isinstance(messages, list) else messages

        to_send = self.update_messages(messages)

        logger.debug("Sending %s messages to Contrast Service", len(to_send))
        for agent_message, msg in zip(messages, to_send):
            logger.debug(
                "Sending %s message with msg_count=%s, pid=%s",
                agent_message.__class__.__name__,
                msg.message_count,
                msg.pid,
            )

            response = self.send_dtm(msg)
            if response is not None:
                logger.debug(
                    "Received response for message with msg_count=%s, pid=%s",
                    msg.message_count,
                    msg.pid,
                )
                responses.append(response)
            else:
                logger.debug(
                    "No response for message with msg_count=%s, pid=%s",
                    msg.message_count,
                    msg.pid,
                )

        self.connection_status.success()
        return responses

    def send_message(self, sock, msg):
        """
        Prefix each message with a 4-byte length (network byte order)
        """
        msg = struct.pack(_RECV_FMT, len(msg)) + msg
        sock.sendall(msg)

    def receive_message(self, sock):
        """
        Read message length and unpack it into an integer

        :param sock - socket to receive information from
        :return bytes if successful else None
        """
        raw_message_length = self.receive_all(sock, 4)

        if not raw_message_length:
            logger.debug("Falsy raw message length of %s", raw_message_length)
            return None

        message_length = struct.unpack(_RECV_FMT, raw_message_length)[0]
        return self.receive_all(sock, message_length)

    def receive_all(self, sock, n):
        """
        Helper function to recv n bytes or return None if EOF is hit
        """
        buffer_array = bytearray()
        while len(buffer_array) < n:
            packet = sock.recv(n - len(buffer_array))
            if not packet:
                return None
            buffer_array.extend(packet)
        return bytes(buffer_array)

    def build_empty_message(self):
        settings = Settings()

        message = Message()
        message.app_name = settings.app_name
        message.app_path = self.app_path
        message.app_language = _APPLICATION_LANGUAGE
        message.client_id = self.client_id
        message.client_number = 1
        message.client_total = 1
        message.timestamp_ms = now_ms()
        message.pid = settings.pid

        self.count += 1
        message.message_count = self.count

        return message

    def update_message(self, agent_message):
        message = self.build_empty_message()

        if isinstance(agent_message, Activity):
            agent_message.duration_ms = now_ms()
            message.activity.CopyFrom(agent_message)

        if isinstance(agent_message, AgentStartup):
            message.agent_startup.CopyFrom(agent_message)

        if isinstance(agent_message, ServerActivity):
            message.server_activity.CopyFrom(agent_message)

        if isinstance(agent_message, ApplicationCreate):
            message.application_create.CopyFrom(agent_message)

        if isinstance(agent_message, ApplicationUpdate):
            message.application_update.CopyFrom(agent_message)

        if isinstance(agent_message, HttpRequest):
            message.prefilter.CopyFrom(agent_message)

        if isinstance(agent_message, ObservedRoute):
            message.observed_route.CopyFrom(agent_message)

        if isinstance(agent_message, Poll):
            message.poll.CopyFrom(agent_message)

        return message

    def update_messages(self, messages):
        """
        Possible messages supported currently

        contrast.api.dtm.ServerActivity server_activity = 10;
        contrast.api.dtm.AgentStartup agent_startup = 11;
        contrast.api.dtm.ApplicationCreate application_create = 12;
        contrast.api.dtm.ApplicationUpdate application_update = 13;
        contrast.api.dtm.Activity activity = 14;
        contrast.api.dtm.Poll
        """
        updated = []
        for item in messages:
            prepared_msg = self.update_message(item)
            updated.append(prepared_msg)

        return updated

    def _build_agent_startup_msg(self, settings):
        agent_startup = AgentStartup()

        agent_startup.server_name = settings.get_server_name()
        agent_startup.server_path = settings.get_server_path()
        agent_startup.server_type = settings.get_server_type()
        agent_startup.server_version = contrast.__version__

        agent_startup.environment = settings.config.get("server.environment")

        agent_startup.server_tags = settings.config.get("server.tags")
        agent_startup.application_tags = settings.config.get("application.tags")
        agent_startup.library_tags = settings.config.get("inventory.tags")
        agent_startup.finding_tags = settings.config.get("assess.tags")

        agent_startup.version = contrast.__version__

        settings = Settings()

        log_info = {
            "Server Name": agent_startup.server_name,
            "Server Path": agent_startup.server_path,
            "Server Type": agent_startup.server_type,
            "Application Name": settings.app_name,
            "Application Path": self.app_path,
            "Application Language": _APPLICATION_LANGUAGE,
        }

        logger.info("Application context", **log_info)

        return agent_startup

    def _build_app_create_msg(self, settings):
        create = ApplicationCreate()
        create.group = settings.config.get("application.group", "")
        create.app_version = settings.config.get("application.version", "")
        create.code = settings.config.get("application.code", "")

        create.metadata = settings.config.get("application.metadata", "")

        # build based views
        create.session_id = settings.config.session_id
        create.session_metadata = settings.config.get_session_metadata()

        # instrumentation mode
        create.mode.protect = settings.is_protect_enabled()
        create.mode.assess = settings.is_assess_enabled()

        return create


def is_connected():
    return _ServiceState().connection_status.connected


def build_update_message(routes):
    """
    Create an ApplicationUpdate message with framework information and routes.

    :param routes: Dict of api.Route, will be empty if in Protect mode
    :return: ApplicationUpdate instance
    """
    settings = Settings()

    update_message = ApplicationUpdate()

    update_message.platform.major = settings.framework.version.major
    update_message.platform.minor = settings.framework.version.minor
    update_message.platform.build = settings.framework.version.patch

    # Route coverage is an assess feature. Routes will be empty
    # so the update_message will have no routes.
    for route in routes.values():
        update_message.routes.extend([route.to_dtm()])

    return update_message


def send_messages_get_responses(messages):
    """Send messages to service and return responses"""
    service_state = _ServiceState()

    if service_state.resend_startup:
        logger.debug("Resending startup messages")
        service_state._build_and_send_startup_msgs()

    return service_state.send_messages_retry(messages, raise_exception=False)


def send_messages(messages):
    """
    Rely on ServiceClient having already initialized its connection to Speedracer
    and ask it to send a list of messages.
    Process the responses from sending the messages.
    :param messages: a list of protobuf messages to send
    :side effect: ContrastServiceException could be raised but should be catch by the middleware
    """
    responses = send_messages_get_responses(messages)
    Settings().process_responses(responses)


def send_heartbeat_message():
    """
    Agent sends a Poll message to Speedracer as a way to maintain a heartbeat.
    Note that a Poll message should never be the first message sent to Speedracer,
    a Poll message should only be sent AFTER an AgentStartup.
    """
    return send_messages([_ServiceState().poll])


def send_startup_messages():
    """
    Initialize ServiceClient and its connection to Speedracer by asking it to send the agent and app
    initialization messages. This is successful if responses are received to process for new settings.

    :return: bool if successfuly able to send initial messages and receive and process responses.
    """
    _ServiceState().initialize_and_send_messages()
