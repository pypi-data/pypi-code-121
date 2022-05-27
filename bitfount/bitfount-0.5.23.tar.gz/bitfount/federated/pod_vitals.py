"""Module for creating Pod Vitals webserver."""
from asyncio import AbstractEventLoop
from dataclasses import dataclass
import logging
from os import environ
import socket
from threading import Lock
import time

from aiohttp import web
from aiohttp.web import Application, AppRunner, Request, Response, TCPSite

logger = logging.getLogger(__name__)

MAX_TASK_EXECUTION_TIME = 3_600


@dataclass
class _PodVitals:
    """Tracks statistics used to determine a pod's vitals."""

    # On initalization, set last_task_execution_time
    # to current time so that we dont kill a Pod
    # before it has had time to pick up its first task
    _last_task_execution_time = time.time()
    _last_task_execution_lock = Lock()

    @property
    def last_task_execution_time(self) -> float:
        """The timestamp of the lastest task executed in the pod."""
        with self._last_task_execution_lock:
            return self._last_task_execution_time

    @last_task_execution_time.setter
    def last_task_execution_time(self, time: float) -> None:
        """Set last_task_execution_time."""
        with self._last_task_execution_lock:
            self._last_task_execution_time = time


class _PodVitalsHandler:
    """_PodVitals webserver."""

    def __init__(self, pod_vitals: _PodVitals):
        self.pod_vitals = pod_vitals

        self.app = Application()
        self.app.add_routes(
            [web.get("/status", self.status), web.get("/health", self.health)]
        )
        self.runner = AppRunner(self.app)

    def _get_pod_vitals_port(self) -> int:
        """Determine port to serve _PodVitals webserver over.

        If env var `BITFOUNT_POD_VITALS_PORT` is set we use this
        port number. Else we dynamically select an open ports.
        Dynamically selecting an open port allows end users to
        run multiple pods locally.
        """
        pod_vitals_port = environ.get("BITFOUNT_POD_VITALS_PORT")
        if pod_vitals_port:
            try:
                port = int(pod_vitals_port)
            except ValueError:
                raise ValueError(
                    f"BITFOUNT_POD_VITALS_PORT must be an integer. "
                    f"BITFOUNT_POD_VITALS_PORT set to '{pod_vitals_port}'"
                )
            if not (1 <= port <= 65535):
                raise ValueError(
                    "Invalid BITFOUNT_POD_VITALS_PORT given. Must be in range [1-65535]"
                )
        else:
            port = self._open_socket()
        return port

    def _open_socket(self) -> int:
        """Retrieves an open tcp port.

        This introduces the risk of race condition as we
        choose an open port here but do not claim it until
        we start the server. If the pod is running inside
        a container the BITFOUNT_POD_VITALS_PORT
        env var should be set.
        """
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp.bind(("", 0))
        _, port = tcp.getsockname()
        tcp.close()
        return int(port)

    async def status(self, request: Request) -> Response:
        """Handler to support `/status` requests."""
        return web.json_response({"status": "OK"}, status=200)

    async def health(self, request: Request) -> Response:
        """Determine a pod's health.

        We define a pod as healthy if its lastest task execution time
        is less than 1 hour ago.
        """
        is_healthy = False
        now = time.time()
        if now - self.pod_vitals.last_task_execution_time < MAX_TASK_EXECUTION_TIME:
            is_healthy = True
        return web.json_response({"healthy": is_healthy}, status=200)

    def start(self, loop: AbstractEventLoop) -> None:
        """Start _PodVitals webserver."""
        loop.run_until_complete(self.runner.setup())
        port = self._get_pod_vitals_port()
        # Needs to be set to `0.0.0.0` to bind in Docker container
        # Could be made configurable in future?
        # Marked nosec as this is just serving a static healthcheck endpoint
        site = TCPSite(self.runner, "0.0.0.0", port)  # nosec
        logger.info(f"Running Pod Vitals interface on: http://localhost:{port}/health")
        loop.run_until_complete(site.start())
