# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import os
import uuid
import hashlib
from pathlib import Path
from queue import Queue
import threading
import contrast

from contrast import __version__
from contrast.agent import scope
from contrast import AGENT_CURR_WORKING_DIR
from contrast.agent.settings import Settings
from contrast.extern import structlog as logging
from requests import post as post_request, get as get_request
from contrast.utils import service_util
from contrast.utils.decorators import cached_property


logger = logging.getLogger("contrast")

FILE_LOCATIONS = [
    # Most stable place but some OS may not allow creating here
    "/etc/contrast/python/",
    os.path.join(AGENT_CURR_WORKING_DIR, "config", "contrast"),
]

DISCLAIMER = (
    "The Contrast Python Agent collects usage data "
    "in order to help us improve compatibility and security coverage. "
    "The data is anonymous and does not contain application data. "
    "It is collected by Contrast and is never shared. "
    "You can opt-out of telemetry by setting the "
    "CONTRAST_AGENT_TELEMETRY_OPTOUT environment variable to '1' or 'true'. "
    "Read more about Contrast Python Agent telemetry: "
    "https://docs.contrastsecurity.com/en/python-telemetry.html"
)

BASE_URL = "https://telemetry.python.contrastsecurity.com"
BASE_ENDPOINT = "api/v1/telemetry"
URL = f"{BASE_URL}/{BASE_ENDPOINT}"
HEADERS = {"User-Agent": f"python-{__version__}"}


class Telemetry(threading.Thread):
    SLEEP = 60 * 60 * 3  # 3hrs
    RETRY_SLEEP = 60
    REPORTED_ERRORS = {}

    def __init__(self):
        super().__init__()
        self.daemon = True

        self.enabled = True
        self.message_q = None
        self.stopped = False
        self.settings = Settings()

        self._check_is_public_build()
        self._check_enabled()

    @property
    def wait_time(self):
        return self.SLEEP

    @cached_property
    def instance_id(self):
        if self._mac_addr is None:
            return "_" + uuid.uuid4().hex
        return self._sha256(hex(self._mac_addr))

    @cached_property
    def application_id(self):
        if self._mac_addr is None:
            return "_" + uuid.uuid4().hex
        return self._sha256(hex(self._mac_addr) + self.settings.app_name)

    @cached_property
    def _mac_addr(self):
        """
        The MAC address for the current machine's primary network adapter as a base-10
        integer. If we find a multicast MAC address, return None.
        See _is_multicast_mac_address.
        """
        _mac_addr = uuid.getnode()
        if self._is_multicast_mac_address(_mac_addr):
            return None
        return _mac_addr

    def run(self):
        if not self.enabled:
            return

        # Ensure thread runs in scope because it is initialized
        # before our thread.start patch is applied.
        with scope.contrast_scope():
            from contrast.agent.events import StartupMetricsTelemetryEvent

            logger.debug("Starting telemetry thread")

            # 100 is purely for safety; should be unlikely to hit.
            self.message_q = Queue(maxsize=100)

            # Do not move creating startup msg outside of this function
            # so the work stays in the telemetry thread, not the main thread.
            self.add_message(StartupMetricsTelemetryEvent())
            if not self.stopped:
                self.send_message()

            # This while loop should complete, shutting down the thread
            # if agent has become disabled during the course of the agent lifecycle.
            while not self.stopped and self.settings.is_agent_config_enabled():
                self.send_message()
                service_util.sleep(self.wait_time)

    def add_message(self, msg):
        if not self.enabled or msg is None:
            return

        logger.debug("Adding msg to telemetry queue: %s", msg)
        self.message_q.put(msg)

    def send_message(self):
        msg = self.message_q.get()

        try:
            logger.debug("Sending Telemetry msg %s", msg)
            response = self._post(msg)
            self._check_response(response)
        except Exception as ex:
            logger.debug("Could not send message from telemetry queue.", ex)

    def should_report_error(self, error, original_func):
        key = " ".join(
            [
                type(error).__name__,
                original_func.__name__,
                original_func.__module__,
                str(error),
            ]
        )

        if key in self.REPORTED_ERRORS:
            self.REPORTED_ERRORS[key] += 1
            return False

        self.REPORTED_ERRORS[key] = 1

        return True

    def report_error(self, error, original_func, logger_="", message=""):
        """
        Report an agent error/exception to Telemetry.

        Take great care to avoid calling this where application errors or customer
        code may be caught.
        """
        from contrast.agent.events import ErrorTelemetryEvent

        if self.should_report_error(error, original_func):
            self.add_message(
                ErrorTelemetryEvent(error=error, logger_=logger_, message=message)
            )

    def _post(self, msg):
        data = [msg.to_json()]
        url = f"{URL}{msg.path}"
        response = post_request(
            url, json=data, headers=HEADERS, allow_redirects=False, verify=True
        )

        logger.debug("Telemetry response: %s %s", response.status_code, response.reason)
        return response

    def _check_response(self, response):
        """
        Per RFC-6585, check response status code for 429. If so, sleep
        for the amount given by Retry-After header, if present, or 60 secs.
        """
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            sleep_time = int(retry_after) if retry_after else self.RETRY_SLEEP

            logger.debug("Telemetry sleeping for %s seconds", sleep_time)
            service_util.sleep(sleep_time)

    def _is_multicast_mac_address(self, mac_addr):
        """
        A multicast MAC address is an indication that we're not seeing a hardware MAC
        address, which means this value is subject to change even on a single server.
        MAC addresses have a multicast bit that is only set for such addresses. This
        method returns True if the supplied mac address is a multicast address.

        Note that when uuid.getnode() isn't able to find a hardware MAC address, it
        randomly generates an address and (critically) sets the multicast bit.
        """
        return bool(mac_addr & (1 << 40))

    def _sha256(self, str_input):
        return hashlib.sha256(str_input.encode()).hexdigest()

    def _check_enabled(self):
        if contrast.telemetry_disabled() or self._connection_failed():
            self.enabled = False
        else:
            self._find_or_create_file()

        # Debug log for dev purposes. The only time an agent user should see anything
        # about telemetry is if the disclaimer is print/logged.
        logger.debug("Agent telemetry is %s", "enabled" if self.enabled else "disabled")

    def _check_is_public_build(self) -> None:
        is_public = os.environ.get("IS_PUBLIC_BUILD")
        self.is_public_build = True

        if is_public and is_public.lower() in ("0", "false"):
            self.is_public_build = False

        # Debug log for dev purposes. The only time an agent user should see anything
        # about telemetry is if the disclaimer is print/logged.
        logger.debug(
            "Agent telemetry %s",
            "is in public build mode"
            if self.is_public_build
            else "is not in public build mode",
        )

    def _connection_failed(self):
        try:
            # any response here is fine as long as no error is raised.
            get_request(BASE_URL)
            return False
        except Exception as ex:
            # Any exception such as SSLError, ConnectionError, etc
            logger.debug("Telemetry connection failed: %s", ex)

        return True

    def _find_or_create_file(self):
        """
        Find an existing .telemetry file or create an empty one.

        /etc/contrast/python/ is the preferred location because it's permanent
        across any agent, but in some OS we may not be able to create it.

        The .telemetry file is intended to be an empty file only as a marker
        to let us know if we have print/logged the disclaimer. Failing to find it
        in any situation means we should print/log.
        """
        name = ".telemetry"

        # 1. If .telemetry file exists, don't print/log disclaimer
        for path in FILE_LOCATIONS:
            file_path = os.path.join(path, name)
            if Path(file_path).exists():
                return

        # 2. If .telemetry file does not exist, attempt to create dir structure
        # and the empty file
        for path in FILE_LOCATIONS:
            file_path = os.path.join(path, name)
            try:
                Path(path).mkdir(parents=True, exist_ok=True)
                Path(file_path).touch()
                break
            except Exception:
                continue

        # 3. Print/log disclaimer if .telemetry file was created or if it failed to
        # be created
        print(DISCLAIMER)  # pylint: disable=superfluous-parens
        logger.info(DISCLAIMER)
